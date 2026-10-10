import unittest,sys,types,importlib.util
from pathlib import Path
# Pure calculation/query tests do not load the running app or mutate its database.
retrieval=types.ModuleType('open_webui.retrieval.utils');retrieval.get_sources_from_items=None
misc=types.ModuleType('open_webui.utils.misc');misc.get_last_user_message=None;misc.add_or_update_system_message=None
sys.modules['open_webui.retrieval.utils']=retrieval;sys.modules['open_webui.utils.misc']=misc
spec=importlib.util.spec_from_file_location('source_rag',Path(__file__).resolve().parents[2]/'backend/open_webui/utils/albe_source_rag.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class CalculationAndContext(unittest.TestCase):
 def test_bounded_arithmetic(self):
  self.assertEqual(mod.arithmetic('What is 2 + 3 * 4?'),'Local calculator: 2 + 3 * 4 = 14')
  for x in ['__import__("os")','2**999','1/0','float("nan")','(2).__class__']:
   self.assertIsNone(mod.arithmetic(x))
 def test_mass_uses_explicit_inputs(self):
  self.assertIn('6.48 kg',mod.source_calculation('At 30 mg/L, 27 m³/h for 8 hours, how much product?'))
  self.assertIsNone(mod.source_calculation('What dose should I use at 27 m³/h for 8 hours?'))
  self.assertIsNone(mod.source_calculation('30 mg/L active at 27 m³/h for 8 hours'))
 def test_jar_requires_basis(self):
  self.assertIn('6 mg/L',mod.source_calculation('For a 500 mL jar sample, add 3 mL of 0.1% w/v stock'))
  self.assertIsNone(mod.source_calculation('500 mL jar sample, 3 mL of 0.1% stock'))
 def test_followup_uses_current_chat_user_only(self):
  msgs=[{'role':'user','content':'Tell me about 1333'},{'role':'assistant','content':'Fake 50 ppm recommended dose'},{'role':'user','content':'What about its preparation?'}]
  self.assertIn('1333',mod.retrieval_query(msgs));self.assertNotIn('50',mod.retrieval_query(msgs))
  self.assertNotIn('1333',mod.retrieval_query([msgs[-1]]))
  self.assertEqual(mod.retrieval_query(msgs+[{'role':'user','content':'What is 1833?'}]),'What is 1833?')
class GroundingChecks(unittest.TestCase):
 def test_observed_contradictions(self):
  m={'albe_source_rag':{'query':'Compare 1311 and 1333'},'sources':[]}
  self.assertTrue(mod.grounding_problems('Choose Cestfloc 1333 for higher acrylamide.',m))
  self.assertFalse(mod.grounding_problems('No comparative performance evidence establishes a preferred grade.',m))
  m={'albe_source_rag':{'query':'brown raw water'},'sources':[{'document':['Tannin x Na (Soluble) CR1800']}]}
  self.assertTrue(mod.grounding_problems('Tannin reacts with sodium to form an insoluble compound.',m))
  self.assertTrue(mod.grounding_problems('CR1800 at 20 ppm is applied.',m))
  self.assertFalse(mod.grounding_problems('The source describes approximately 20 ppm CR1800; verify in jar tests.',m))
 def test_verified_result_and_sources(self):
  calc=mod.source_calculation('30 mg/L, 27 m³/h, 8 hours')
  m={'albe_source_rag':{'calculator':calc,'passages':['HB-p18']},'sources':[{'metadata':[{'source':'HB-p18'}]}]}
  self.assertIn('6.48 kg. [1]',mod.calculator_completion(m))
  m['albe_source_rag']['passages']=[]
  self.assertIsNone(mod.calculator_completion(m))
if __name__=='__main__':unittest.main()
