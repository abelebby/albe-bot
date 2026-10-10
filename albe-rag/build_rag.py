from pathlib import Path
from pypdf import PdfReader
import json,hashlib,re,shutil,os
root=Path(__file__).resolve().parent
spm=Path(os.environ.get('ALBE_DOCUMENT_DIR',str(root/'documents')))/'Field Service Handbook - SPM Friendly Edition.pdf'
(root/'originals').mkdir(exist_ok=True)
copy=root/'originals'/spm.name
if not copy.exists():shutil.copy2(spm,copy)
assert copy.read_bytes()==spm.read_bytes()
manifest=json.loads((root/'source-manifest.json').read_text())
spm_info={'source_id':'SPM','filename':spm.name,'path':str(copy),'sha256':hashlib.sha256(copy.read_bytes()).hexdigest(),'pages':45,'status':'supplied derivative language/layout edition; not new technical approval'}
manifest=[x for x in manifest if x['source_id']!='SPM']+[spm_info]
(root/'source-manifest.json').write_text(json.dumps(manifest,indent=2))
original=[json.loads(x) for x in (root/'source-passages.jsonl').read_text().splitlines()]
r=PdfReader(copy)
spm_pages=[{'pdf_page':i+1,'text':page.extract_text(extraction_mode='layout')} for i,page in enumerate(r.pages)]
(root/'extracts'/'SPM.json').write_text(json.dumps(spm_pages,ensure_ascii=False,indent=2))
(root/'extracts'/'SPM.txt').write_text('\n\n'.join(f'=== SPM PDF page {p["pdf_page"]} ===\n{p["text"]}' for p in spm_pages))
for n,ref in [(18,'13'),(19,'14'),(20,'15'),(21,'16'),(22,'17 and 24'),(33,'28')]:
 original.append({'id':f'SPM-p{n:02}','source_id':'SPM','source_filename':spm.name,'pdf_page':n,'printed_page':n,'original_printed_pages':ref,'text':r.pages[n-1].extract_text(extraction_mode='layout')})
ready=root/'rag-ready';ready.mkdir(exist_ok=True)
notes={
'D01':'Review of all 5 supplied SDS pages: no numeric client treatment dose is supplied. PAC 20% assay basis is unstated. Laboratory pH is not a water-treatment target. Liquid physical state conflicts with powder spill wording; skin-contact durations differ between Malay and English. No P61S equivalence is established.',
'D02':'Review of all 4 supplied SDS pages: no numeric client treatment dose, including POME dose, is supplied. The SDS does not identify PAC chemistry or a 30% assay. Earlier user description of PAC30% is not SDS evidence. Specific gravity is not a verified dosing-stock density. No P61S equivalence is established.',
'D03':'Review: body identifies sodium chloride, approximately 100 wt%. Cationic-polymer footer and acrylamide warning conflict with that identity. Request corrected supplier data for those safety claims. No raw-water coagulant/flocculant role or client clarification dose established.',
'D04':'Review of supplied PDS: no numeric client treatment dose or numeric operating pH range supplied. Stock up to 0.5% has unstated concentration basis; 10:1 dilution direction/basis unstated. pH/viscosity at 0.1% and 25°C are laboratory specifications. No RE3030 equivalence or comparative winner against 1333 established. No SDS supplied.',
'D05':'Review of supplied PDS: no numeric client treatment dose or numeric operating pH range supplied. Stock up to 0.5% has unstated concentration basis; 10:1 dilution direction/basis unstated. pH/viscosity at 0.1% and 25°C are laboratory specifications. No RE3030 equivalence or comparative winner against 1311 established. No SDS supplied.',
'D06':'Review of supplied PDS: ionicity is not explicitly stated (earlier user description cationic is not PDS evidence). Dosage is application dependent, no numeric client dose or stock preparation method supplied. Laboratory solution pH is not treatment-water target. No RE3030 equivalence established. No SDS supplied.',
'D07':'Review of supplied SDS: no numeric client treatment dose is supplied. Laboratory pH 11.3 at 1% is not target treatment pH. Density 2.53 at 20°C is relative density, not bulk or prepared-stock density. Toxicity endpoints are not treatment dosages. Organic-dust wording and physical-property entries are flagged in source review.'}
products={'D01':['1220'],'D02':['1833'],'D03':['pdv','salt'],'D04':['1311'],'D05':['1333'],'D06':['1490'],'D07':['soda']}
entries=[]
for b in original:
 key=b['source_id']; text=b['text']; text='\n'.join(re.sub(r' {3,}', '  ', line.strip()) for line in text.splitlines()); text=re.sub(r'\n{3,}','\n\n',text).strip()
 label=f'{b["source_filename"]} - PDF page {b["pdf_page"]}'
 if key=='HB':label+=f' (printed page {b["printed_page"]})'
 status='SUPPLIED PRIMARY SOURCE' if key!='SPM' else 'SUPPLIED SPM EXPLANATION; DERIVATIVE, NOT NEW TECHNICAL APPROVAL'
 header=f'# {label}\n\nEvidence type: {status}.\n'
 if key=='SPM':header+=f'Original handbook printed page(s): {b["original_printed_pages"]}. Editorial corrections must be distinguished from original statements.\n'
 if key=='HB':header+='Handbook examples are examples, not confirmed doses for a new client. Names are not interchangeable without source evidence.\n'
 if key in notes:header+='\nEditorial coverage note (review finding, not a manufacturer quotation): '+notes[key]+'\n'
 content=header+'\n## Source text\n\n'+text+'\n'
 p=ready/f'{b["id"]}.md';p.write_text(content)
 entries.append({'key':b['id'],'path':str(p),'name':p.name,'label':label,'source_id':key,'pdf_page':b['pdf_page'],'kind':status,'products':products.get(key,[]),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(root/'rag-catalog.json').write_text(json.dumps(entries,indent=2))
(root/'coverage-notes.json').write_text(json.dumps(notes,indent=2))
print('Compiled',len(entries),'source-page files including 6 SPM pages; originals unchanged.')
