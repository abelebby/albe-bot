"""Extract the reviewed document set from a local ignored directory."""
from pathlib import Path
import hashlib,json,os
from pypdf import PdfReader
root=Path(__file__).resolve().parent
inputs=Path(os.environ.get('ALBE_DOCUMENT_DIR',str(root/'documents')))
names=[('HB','Field Service Handbook Version 6.pdf'),('D01','ABL- CF 1220 2024.pdf'),('D02','ABL-Cestfloc 1833 - MSDS (1).pdf'),('D03','ABL-PDV Salt.pdf'),('D04','CF 1311 PDS - 260928.pdf'),('D05','CF 1333 PDS - 260929.pdf'),('D06','CF 1490 PDS - 260929.pdf'),('D07','SODA ASH DENSE SDS - 2023.pdf')]
missing=[name for _,name in names if not (inputs/name).is_file()]
if missing:raise SystemExit('Missing local approved documents: '+', '.join(missing))
(root/'extracts').mkdir(exist_ok=True)
manifest=[]
for key,name in names:
 path=(inputs/name).resolve();reader=PdfReader(path)
 pages=[{'pdf_page':i+1,'text':p.extract_text(extraction_mode='layout')} for i,p in enumerate(reader.pages)]
 (root/'extracts'/f'{key}.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2))
 manifest.append({'source_id':key,'filename':name,'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pages':len(pages)})
(root/'source-manifest.json').write_text(json.dumps(manifest,indent=2))
print('Prepared local source extraction; no documents sent to external services.')
