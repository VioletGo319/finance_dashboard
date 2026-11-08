"""Data-source and honest missing-value regression tests."""
import unittest
from scripts.enrichment import annual_capex_fallback, disclosed_share_change, monitoring_scores, dataset_health
from scripts.network import graph_snapshot
from scripts.refresh import pct_rank, WEIGHTS

class TestDataEnrichment(unittest.TestCase):
 def test_primary_capex_seeds_not_backdated(self):
  self.assertFalse(annual_capex_fallback("2026-11-06"))
  d=annual_capex_fallback("2026-11-07")
  self.assertGreaterEqual(len(d),6)
  self.assertAlmostEqual(d["MSFT"]["growth"],115948/64551-1)
  self.assertTrue(d["META"]["source"].startswith("https://"))
  self.assertIn("net of proceeds",d["AMZN"]["metric"])
  self.assertEqual(d["MSFT"]["method"],"annual_capex_yoy_proxy")

 def test_share_changes_are_documented_not_imputed(self):
  _,net=graph_snapshot("2026-11-07")
  c=disclosed_share_change(net["verified_edges"],"2026-11-07")
  self.assertGreaterEqual(len(c),3)
  self.assertAlmostEqual(c["CRUS"][0]["change_pp"],2)
  self.assertAlmostEqual(c["SWKS"][0]["change_pp"],-2)
  self.assertAlmostEqual(c["FN"][0]["change_pp"],-11.3)

 def test_market_monitor_price_only(self):
  bars=[("2026-01-%02d" % i,100+i) for i in range(1,22)]
  q={x:{"bars":bars} for x in ("A","B","C")}
  z=monitoring_scores(q,("A","B","C"),pct_rank,{"A":.02,"B":.01,"C":-.02})
  self.assertTrue(all(x is not None for x in z.values()))
  self.assertAlmostEqual(z["A"],80)
  self.assertAlmostEqual(z["C"],20)

 def test_missing_prices_are_not_filled(self):
  score=monitoring_scores({"A":{"bars":[]}},("A","B","C"),pct_rank,{"A":None,"B":None,"C":None})
  self.assertTrue(all(x is None for x in score.values()))

 def test_full_alpha_requires_all_factors(self):
  self.assertEqual(len(WEIGHTS),6)
  self.assertAlmostEqual(sum(WEIGHTS.values()),1)
  d=dataset_health([{"close":1,"previous_close":2,"alpha":None,"provisional_alpha":None,"monitor_score":54,"factors":{"policy":None}}],WEIGHTS)
  self.assertEqual(d["official_present"],0)
  self.assertEqual(d["monitor_present"],1)
  self.assertEqual(d["factors_present"]["policy"],0)
