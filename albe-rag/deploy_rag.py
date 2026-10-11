from pathlib import Path
import requests,json,sqlite3
root=Path(__file__).resolve().parent;statep=root/'deployment.json';state=json.loads(statep.read_text()) if statep.exists() else {'files':{}}
s=requests.Session();base='http://127.0.0.1:8080'
def call(method,path,**kw):
 r=s.request(method,base+path,timeout=240,**kw);r.raise_for_status();return r.json()
a=call('POST','/api/v1/auths/signin',json={'email':'admin@localhost','password':'admin'});s.headers['Authorization']='Bearer '+a['token']
backup=root/'review'/'before-source-rag.db'
backup.parent.mkdir(exist_ok=True)
if not backup.exists():
 src=sqlite3.connect(root.parent/'backend/data/webui.db');dst=sqlite3.connect(backup);src.backup(dst);dst.close();src.close()
if not state.get('knowledge_id'):
 k=call('POST','/api/v1/knowledge/create',json={'name':'Albe source documents - raw water','description':'Original handbook raw-water passages, supplied SPM derivative explanations, and supplied product PDS/SDS. Page labels and editorial coverage notes preserved. No internet or prior chatbot guides.'});state['knowledge_id']=k['id'];statep.write_text(json.dumps(state,indent=2))
entries=json.loads((root/'rag-catalog.json').read_text())
for e in entries:
 old=state['files'].get(e['key'])
 if old and old['sha256']==e['sha256']:continue
 with open(e['path'],'rb') as f:
  d=call('POST','/api/v1/files/?process=true&process_in_background=false',files={'file':(e['name'],f,'text/markdown')},data={'metadata':json.dumps({'source_id':e['source_id'],'pdf_page':e['pdf_page'],'evidence_type':e['kind']})})
 call('POST',f'/api/v1/knowledge/{state["knowledge_id"]}/file/add',json={'file_id':d['id']})
 if old:
  state.setdefault('retired_file_ids',[]).append(old['id'])
  call('POST',f'/api/v1/knowledge/{state["knowledge_id"]}/file/remove?delete_file=false',json={'file_id':old['id']})
 state['files'][e['key']]={**e,'id':d['id']};statep.write_text(json.dumps(state,indent=2));print('Indexed',e['key'],flush=True)
# Detach obsolete page records only after every topic record is ready; preserve stored files.
active_keys={e['key'] for e in entries}
for key in list(state['files']):
 if key not in active_keys:
  old=state['files'].pop(key)
  call('POST',f"/api/v1/knowledge/{state['knowledge_id']}/file/remove?delete_file=false",json={'file_id':old['id']})
  state.setdefault('retired_file_ids',[]).append(old['id'])
statep.write_text(json.dumps(state,indent=2))
# Publish bindings only after every file has processed successfully.
for model_id in ['qwen3:1.7b']:
 try:
  m=call('GET','/api/v1/models/model?id='+requests.utils.quote(model_id,safe=''))
 except requests.HTTPError as error:
  if error.response.status_code!=404:raise
  m=None
 if not m:
  m=call('POST','/api/v1/models/create',json={'id':model_id,'base_model_id':None,'name':'ALBE BOT','meta':{'description':'','profile_image_url':'/static/albe-logo.png'},'params':{},'is_active':True})
 meta=m['meta'];old=meta.pop('elbe_troubleshooting',{})
 previous=meta.get('albe_source_rag',{})
 retired_collections=list(dict.fromkeys(old.get('managed_collection_ids',[])+previous.get('retired_collection_ids',[])))
 retired_files=list(dict.fromkeys(old.get('retired_file_ids',[])+[v['id'] for v in old.get('guides',{}).values()]+[v['id'] for v in old.get('products',{}).values()]+([old['handbook_reference']['id']] if old.get('handbook_reference') else [])+previous.get('retired_file_ids',[])+state.get('retired_file_ids',[])))
 notes=json.loads((root/'coverage-notes.json').read_text());products={p:notes[v['source_id']] for v in state['files'].values() for p in v['products'] if p.isnumeric()}
 meta['albe_source_rag']={'enabled':True,'knowledge_id':state['knowledge_id'],'files_by_name':{v['name']:v for v in state['files'].values()},'product_review_notes':products,'retired_collection_ids':retired_collections,'retired_file_ids':retired_files}
 meta['knowledge']=[{'id':state['knowledge_id'],'name':'Albe source documents - raw water','type':'collection'}]
 params=m['params'];params.update(system=(root/'SYSTEM-PROMPT.txt').read_text().strip(),temperature=0.1,num_ctx=6144,num_predict=650)
 call('POST','/api/v1/models/model/update',json={'id':model_id,'base_model_id':m.get('base_model_id'),'name':'ALBE BOT','params':params,'meta':meta,'is_active':m['is_active'],'access_grants':m.get('access_grants',[])})
call('POST','/api/v1/retrieval/config/update',json={'ENABLE_RAG_HYBRID_SEARCH':True,'ENABLE_RAG_HYBRID_SEARCH_ENRICHED_TEXTS':False,'TOP_K':6,'TOP_K_RERANKER':12,'HYBRID_BM25_WEIGHT':0.5,'RELEVANCE_THRESHOLD':0.0})
call('GET','/api/models');state['active_model']='qwen3:1.7b';state['internet_sources_added']=False;state['canned_responses_enabled']=False;statep.write_text(json.dumps(state,indent=2));print('Activated current model with new source index.',flush=True)
