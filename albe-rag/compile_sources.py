from pathlib import Path
import json,re,hashlib
root=Path(__file__).resolve().parent
manifest=json.loads((root/'source-manifest.json').read_text())
out=root/'source-passages';out.mkdir(exist_ok=True)
blocks=[]
for src in manifest:
 key=src['source_id']
 if key=='SPM':continue
 pages=json.loads((root/'extracts'/f'{key}.json').read_text())
 selected=[16,17,18,19,20,27,31] if key=='HB' else list(range(1,len(pages)+1))
 for n in selected:
  text=pages[n-1]['text']
  if key=='HB' and n==27:
   text=text[text.index('Raw Water with High Tannin'):]
  printed=n-3 if key=='HB' else n
  block={'id':f'{key}-p{n:02}','source_id':key,'source_filename':src['filename'],'source_sha256':src['sha256'],'pdf_page':n,'printed_page':printed,'scope':'raw-water' if key=='HB' else 'product-document','text':text,'status':'primary-source-extraction','limitations':'Layout extraction only; see reviewed findings and original page. Not a generated answer or a treatment recommendation.'}
  blocks.append(block)
  header=f'# {block["id"]}: {src["filename"]}\n\nSource: [{src["filename"]}]({src["path"]})\n\nPDF page {n}; printed page {printed}.\n\nThis is extracted source text. Spelling, numeric values, and inconsistencies are retained. Read with the original page and the review notes; do not treat an example as a client prescription.\n\n'
  (out/f'{block["id"]}.md').write_text(header+'```text\n'+text+'\n```\n')
(root/'source-passages.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in blocks))
print(f'{len(manifest)} original PDFs; {sum(x["pages"] for x in manifest)} original pages; {len(blocks)} source page passages compiled. App/model unchanged.')
