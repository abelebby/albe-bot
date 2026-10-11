"""Evidence-boundary checks against local generated records; PDFs are not fixtures in Git."""
from pathlib import Path
import json,unittest
root=Path(__file__).resolve().parents[1]
class TopicBoundaries(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  p=root/'topic-records.json'
  if not p.exists():raise unittest.SkipTest('Compile local approved documents first.')
  cls.records=json.loads(p.read_text());cls.byid={r['key']:r for r in cls.records}
 def body(self,key):return Path(self.byid[key]['path']).read_text().split('## Source text',1)[1]
 def test_tannin_and_pin_flocs_separate(self):
  t=self.body('HB-p27');pin=self.body('HB-p20')
  self.assertIn('CR1800',t);self.assertNotIn('RL 1200',t);self.assertNotIn('3 : 10',t)
  self.assertIn('≈ 20 ppm',t);self.assertIn('or',t)
  self.assertIn('Organic Coagulant',pin);self.assertIn('Giram POM',pin);self.assertNotIn('High Fe',pin);self.assertNotIn('CR1800',pin)
 def test_specifications_keep_test_conditions(self):
  for sid in ['D04','D05']:
   text=self.body(sid+'-product-specifications')
   self.assertIn('25°C',text);self.assertIn('0.1%',text);self.assertIn('Residual acrylamide',text);self.assertNotIn('DOSAGE AND CONTROL',text)
 def test_source_conflicts_together(self):
  text=self.body('HB-tds-conflict');self.assertIn('2 times',text);self.assertIn('2.5 times',text)
  self.assertEqual(self.byid['HB-tds-conflict']['source_pages'],[16,18])
 def test_every_sds_section_keeps_provenance(self):
  for sid in ['D01','D02','D03','D07']:
   entries=[r for r in self.records if r['source_id']==sid]
   self.assertEqual({r['topic'] for r in entries},{f'sds-section-{n:02}' for n in range(1,17)})
   for r in entries:self.assertTrue(r['source_pages'])
 def test_unique_records_and_primary_vs_derivative(self):
  self.assertEqual(len(self.records),len(self.byid))
  self.assertEqual(len(self.records),130)
  for r in self.records:
   self.assertIn('DERIVATIVE' if r['source_id']=='SPM' else 'PRIMARY',r['kind'])
if __name__=='__main__':unittest.main()
