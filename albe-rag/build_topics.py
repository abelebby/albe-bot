"""Procedure-sized evidence records; original excerpts and editorial notes remain distinct."""
from pathlib import Path
import json,re,hashlib
root=Path(__file__).resolve().parent
old=json.loads((root/'page-catalog.json').read_text())
pages={e['key']:Path(e['path']).read_text().split('## Source text',1)[1].strip() for e in old}
notes=json.loads((root/'coverage-notes.json').read_text())
out=root/'topic-ready';out.mkdir(exist_ok=True)
records=[]
def cut(key,start,end=None):
 text=pages[key]
 pattern=lambda marker:r'\s*'.join(re.escape(word) for word in marker.split())
 match=re.search(pattern(start),text)
 if not match:raise ValueError(f'{key}: missing start marker {start!r}')
 a=match.start(); stop=re.search(pattern(end),text[match.end():]) if end else None
 if end and not stop:raise ValueError(f'{key}: missing end marker {end!r}')
 b=match.end()+stop.start() if stop else len(text)
 return text[a:b].strip()
def add(key,source,page,topic,text,products=(),review='',links=()):
 refs=page if isinstance(page,list) else [page]
 title=next(x['label'].split(' - PDF page')[0] for x in old if x['source_id']==source)
 kind='SUPPLIED SPM DERIVATIVE EXPLANATION' if source=='SPM' else 'SUPPLIED PRIMARY SOURCE EXCERPT'
 label=f'{title} - PDF page'+('s ' if len(refs)>1 else ' ')+', '.join(map(str,refs))+f' - {topic}'
 data={'key':key,'name':key+'.md','label':label,'source_id':source,'pdf_page':refs[0],'source_pages':refs,'topic':topic,'products':list(products),'kind':kind,'linked_topics':list(links)}
 header=f'# {label}\n\nEvidence type: {kind}.\nTopic: {topic}.\nSource PDF page(s): '+', '.join(map(str,refs))+'.\n'
 if source=='HB':header+='Original printed page(s): '+', '.join(str(n-3) for n in refs)+'.\n'
 if source=='SPM':header+='This is a supplied language/layout rewrite, not independent technical approval.\n'
 if products:header+='Named products: '+', '.join(products)+'.\n'
 if links:header+='Related topic records: '+', '.join(links)+'. These retain their own applicability.\n'
 if review:header+='\nEditorial review note (not manufacturer wording): '+review+'\n'
 content=header+'\n## Source text\n\n'+text.strip()+'\n';p=out/data['name'];p.write_text(content)
 data.update(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest());records.append(data)
# Original handbook: keep independent procedures separate even where they share a page.
add('HB-layout','HB',16,'treatment-layout',cut('HB-p16','RAW WATER OPERATING SYSTEM','Remarks:'),['P61S','RE3030','soda'], 'Diagram labels must be read with the original diagram. P61S is at the coagulant stage; RE3030 is after coagulation. Stirring notes and static-mixer placement are separate equipment guidance.')
for key,topic,start,end in [('sampling','sampling','(1)','(2)'),('coagulant-mixing','mixing','(2)','(3)'),('static-mixer','mixing-layout','(3)','(4)'),('floc-observation','floc-observation','(4)','(5)'),('flocculant-mixing','mixing','(5)','(6)')]:
 add('HB-'+key,'HB',16,topic,cut('HB-p16',start,end),['P61S'] if key=='coagulant-mixing' else ['RE3030'] if key=='flocculant-mixing' else [],'Equipment/layout-specific source instruction, not universal design sizing.')
add('HB-clarity','HB',16,'clarity-targets',cut('HB-p16','(6)','TDS after clarifier'),'','Operational references, not established drinking-water or effluent legal limits.')
tds1=cut('HB-p16','TDS after clarifier').split('Page 13')[0];tds2=cut('HB-p18','After addition','Soda ash can')
add('HB-tds-conflict','HB',[16,18],'tds-conflict',f'Original PDF page 16:\n{tds1}\n\nOriginal PDF page 18:\n{tds2}',review='The 2-times and 2.5-times thresholds conflict, and the first page overlaps its equality boundary. Neither ratio by itself confirms the cause of a client TDS rise.',links=['SPM-tds-conflict'])
add('HB-coagulant-stock','HB',17,'stock-preparation',cut('HB-p17','Alum / Soda Ash / PAC preparation','Precaution ;'),['PAC','soda','alum'],'The stated grams/final mL establish a mass/volume preparation, not a treatment dose.')
add('HB-pac-volume','HB',17,'concentration-basis',cut('HB-p17','Precaution ;','RE 3030 or'),['PAC'],'The source 1.3 factor is not a verified density or assay for every PAC product.')
add('HB-polymer-stock','HB',17,'stock-preparation',cut('HB-p17','RE 3030 or','Formula'),['RE3030','A110 PWG'],'No documented equivalence with Cestfloc 1311/1333/1490 is established.')
add('HB-p17','HB',17,'jar-calculation',cut('HB-p17','Formula','For chlorine'),review='Jar-table percentages refer to the gram/mL preparations on this source page. Calculate concentration from known stock basis; this does not select a client dose.')
add('HB-chlorine-reference','HB',17,'chlorine-reference',cut('HB-p17','For chlorine','Usage of Caustic'),review='Historical handbook compliance claim is not independently established here; no client oxidant-demand calculation is supplied.')
add('HB-p18','HB',18,'mass-calculation',cut('HB-p18','Actual Usage','Precaution'),['P61S'],'30 ppm is the source example, not a new-client recommendation. Source prints 6.4 kg; arithmetic is 6.48 kg. Flow is treated-water flow for this mass balance.')
add('HB-general-order','HB',18,'general-dosing-order',cut('HB-p18','Soda ash can','Total addition'),['PAC','soda'],'General clarification guidance. It does not override the separate high-tannin scenario. A reported brown colour alone does not establish tannin.',links=['HB-p27'])
add('HB-normal-coagulant-range','HB',18,'coagulant-range',cut('HB-p18','Total addition','As and when'),review='Source says normally, not a universally validated maximum for a client.')
add('HB-alum-blend','HB',18,'alum-blend',cut('HB-p18','As and when','Flocculant preparation'),['PAC','alum'],'Source blend guidance is not evidence that all products/grades are compatible. Confirm the exact products and jar-test outcome.')
add('HB-polymer-preparation-conflict','HB',18,'stock-preparation-conflict',cut('HB-p18','Flocculant preparation','Solubility In Water')+'\n\nSource table entry:\n'+cut('HB-p18','Liquid form','PAC Powder'),review='The blanket 0.5% preparation instruction conflicts with the adjacent liquid 0.5% / powder 0.1% entry. Product-specific instructions and stock basis need confirmation.')
add('HB-solubility-table','HB',18,'solubility-reference',cut('HB-p18','Solubility In Water','For regeneration'),review='Reference values retain their listed bases. Salt is not established as a clarification coagulant; softener regeneration is outside the current treatment scope.')
add('HB-alkalinity','HB',19,'alkalinity-relationships',cut('HB-p19','Alkalinity Relationship','For pH ≤'),review='Original table notation/reporting basis require clarification. SPM table corrections are editorial interpretations, not silently substituted primary text.')
add('HB-ph-equations','HB',19,'ph-equation-reference',cut('HB-p19','For pH ≤'),review='Source empirical equations are not universal pH prediction or soda-dose formulas; log(0) is undefined and validation is not supplied.')
add('HB-ph-adjuster','HB',20,'ph-adjustment',cut('HB-p20','pH Adjuster','Caustic And Soda'),['soda'],'Soda ash is a pH adjuster, not a coagulation product selected from pH alone.')
add('HB-caustic-conflict','HB',[17,20],'caustic-conversion-conflict',cut('HB-p17','Usage of Caustic')+'\n\nOriginal PDF page 20:\n'+cut('HB-p20','Caustic And Soda','High Fe'),['soda'],'The 1:2.2 and dense-soda factor 0.4 differ. Do not silently resolve these into one substitution recipe.')
add('HB-iron','HB',20,'iron-oxidation',cut('HB-p20','High Fe','Role of Organic'),review='This subsection supplies no client oxidant dose. Confirm iron and the actual water system; do not reuse cooling-water doses.')
add('HB-p20','HB',20,'pin-flocs',cut('HB-p20','Role of Organic'),'RL1200'.split(),'RL1200 is explicitly an organic coagulant. 1 ppm and PAC 40-to-30 ppm describe the Giram POM case, not a confirmed dose or outcome for this client. This is separate from the CR1800 tannin scenario.',links=['HB-p27','SPM-pin-flocs'])
add('HB-p27','HB',27,'high-tannin',cut('HB-p27','Raw Water with High Tannin','The reason behind is;'),['CR1800','PAC','alum','soda'],'Applicability is high-tannin raw water. Brown colour/low pH do not confirm tannin. The soda-ash restriction has OR triggers: pH<5, alum>100 ppm, PAC>40 ppm. CR1800 approximately 20 ppm is a documented scenario instruction, not a validated new-client dose. CR1800 chemistry/equivalence is not established. The restriction concerns soda ash, not PAC.',links=['HB-p20','SPM-tannin'])
add('HB-tannin-mechanism','HB',27,'mechanism-reference',cut('HB-p27','The reason behind is;'),review='This is the handbook explanation, not independently validated reaction evidence. Keep soluble versus insoluble labels exact. Use the procedural record for treatment-sequence questions.')
add('HB-p31','HB',31,'pump-calculation',pages['HB-p31'],review='Stock percent basis/density is not fully defined in the original example. The source result is not valid for every 30% stock without a mass-per-volume interpretation.')
# The SPM edition links explanations to matching original topics; it is not independent corroboration.
spm=[('SPM-layout',18,'treatment-layout','The raw-water treatment line','TDS is a warning'),('SPM-tds-conflict',18,'tds-conflict','TDS is a warning',None),('SPM-jar',19,'jar-calculation','Jar tests made simple','Watch the concentration'),('SPM-stock-basis',19,'concentration-basis','Watch the concentration','Other notes'),('SPM-historical-notes',19,'historical-reference','Other notes',None),('SPM-mass',20,'mass-calculation','Turn a jar test','Source operating notes'),('SPM-operating-notes',20,'general-dosing-order','Source operating notes','Material'),('SPM-solubility',20,'solubility-reference','Material',None),('SPM-alkalinity',21,'alkalinity-relationships','Understand alkalinity','Do not calculate pH'),('SPM-ph-limit',21,'ph-equation-reference','Do not calculate pH',None),('SPM-ph',22,'ph-adjustment','Soda ash and caustic','High iron'),('SPM-iron',22,'iron-oxidation','High iron','For small PAC'),('SPM-pin-flocs',22,'pin-flocs','For small PAC','Brown water'),('SPM-tannin',22,'high-tannin','Brown water',None),('SPM-pump',33,'pump-calculation','Calculate the pump feed rate',None)]
for key,n,topic,start,end in spm:
 if key=='SPM-operating-notes':
  section=cut(f'SPM-p{n}',start,end)
  bullets=[b.strip() for b in section.split('•')[1:]]
  for i,b in enumerate(bullets):
   subt=['general-dosing-order','general-dosing-order','alum-blend','stock-preparation'][min(i,3)]
   add(f'{key}-{i+1}','SPM',n,subt,'• '+b,review='Derivative source operating note; its conditions do not override the separate high-tannin scenario.')
  continue
 add(key,'SPM',n,topic,cut(f'SPM-p{n}',start,end),review='Supplied derivative explanation. Original wording, applicability, examples and technical-review issues retain priority; this does not approve a dose for a new client.')
# Product PDS headings preserve complete specification tables and preparation conditions.
for sid,prod in [('D04','1311'),('D05','1333'),('D06','1490')]:
 text=pages[f'{sid}-p01']
 heads=['GENERAL DESCRIPTION','PRODUCT APPLICATION','TYPICAL PRODUCT SPECIFICATION' if sid!='D06' else 'PRODUCT SPECIFICATION','DOSAGE AND CONTROL','PRODUCT HANDLING INFORMATION','PRODUCT STORAGE INFORMATION','PRODUCT PACKING INFORMATION']
 present=[h for h in heads if h in text]
 for i,h in enumerate(present):
  a=text.index(h);b=text.index(present[i+1],a+len(h)) if i+1<len(present) else len(text)
  topic={'GENERAL DESCRIPTION':'product-identity','PRODUCT APPLICATION':'product-application','TYPICAL PRODUCT SPECIFICATION':'product-specifications','PRODUCT SPECIFICATION':'product-specifications','DOSAGE AND CONTROL':'product-preparation','PRODUCT HANDLING INFORMATION':'product-handling','PRODUCT STORAGE INFORMATION':'product-storage','PRODUCT PACKING INFORMATION':'product-packing'}[h]
  add(f'{sid}-{topic}',sid,1,topic,text[a:b],[prod],notes[sid])
# SDS: merge continued pages within each numbered section, never cut a table by page.
for sid in ['D01','D02','D03','D07']:
 current=0;groups={}
 for entry in [e for e in old if e['source_id']==sid]:
  text=pages[entry['key']]; n=entry['pdf_page']
  pattern=r'^\s*\(?SECTION\s+(\d{1,2})\b[^\n]*' if sid in ['D01','D07'] else r'^\s*(\d{1,2})\.\s+[A-Z][A-Z ]{5,}[^\n]*'
  matches=list(re.finditer(pattern,text,re.M));pos=0
  for m in matches:
   if m.start()>pos:groups.setdefault(current,[]).append((n,text[pos:m.start()]))
   current=int(m.group(1));pos=m.start()
  groups.setdefault(current,[]).append((n,text[pos:]))
 for number,parts in groups.items():
  body='\n\n'.join(t.strip() for _,t in parts if t.strip())
  if not body:continue
  if number==0:continue # Letterhead, not an operational evidence section.
  refs=list(dict.fromkeys(n for n,t in parts if t.strip()))
  add(f'{sid}-section-{number:02}',sid,refs,f'sds-section-{number:02}',body,next(e['products'] for e in old if e['source_id']==sid),notes[sid])
(root/'topic-records.json').write_text(json.dumps(records,indent=2))
(root/'rag-catalog.json').write_text(json.dumps(records,indent=2))
print(f'Compiled {len(records)} topic records. Original PDFs unchanged; data remains local.')
