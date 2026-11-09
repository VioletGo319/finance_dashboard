"""Tests of 40-stock candidate participation and missing-factor provenance."""
import unittest
from scripts.autonomous_universe import create_autonomous_universe, FACTOR_WEIGHTS
from scripts.autonomous_paper import target_weights,update_paper_state
from scripts.quant_strategy import SECTOR_BANDS

SYMS=list(dict.fromkeys(s for members in SECTOR_BANDS.values() for s in members))
assert len(SYMS)==40

def fixture():
    quotes={t:{"close":100+i,"price_date":"2026-11-06"} for i,t in enumerate(SYMS)}
    ranked=[]
    for i,t in enumerate(SYMS):
        components={k:float((10+i*3)%95) for k in FACTOR_WEIGHTS}
        if i%3==0:components={"monitor":52.0,"risk":45.0}
        if i%7==0:components={}
        ranked.append({"ticker":t,"component_scores":components,
                       "rank_eligible":i<13})
    universe=create_autonomous_universe(ranked,SYMS,"2026-11-06")
    return quotes,universe

class FullUniverseTest(unittest.TestCase):
    def test_every_stock_scored_provenance(self):
        p,u=fixture()
        self.assertEqual(u["universe_count"],40)
        self.assertEqual(len(u["candidates"]),40)
        self.assertEqual(set(c["ticker"] for c in u["candidates"]),set(SYMS))
        self.assertTrue(any(c["estimated_factor_weight"]>0 for c in u["candidates"]))
        self.assertTrue(any(any(v["kind"]=="ESTIMATED_FACTOR_SCORE"
                          for v in c["factor_provenance"].values()) for c in u["candidates"]))
        self.assertTrue(all(0<=c["observed_factor_coverage"]<=1 for c in u["candidates"]))
    def test_all_40_receives_positive_weights(self):
        prices,universe=fixture()
        weights,status=target_weights(universe["candidates"],prices,25.64,"2026-11-06",require_full=True)
        self.assertEqual(status,"READY_ALL_40")
        self.assertEqual(len(weights),40)
        self.assertTrue(all(v>0 for v in weights.values()))
        self.assertLessEqual(sum(weights.values()),.75+1e-8)
        self.assertLessEqual(max(weights.values()),.15+1e-8)
        for band, names in SECTOR_BANDS.items():
            self.assertLessEqual(sum(weights.get(t,0) for t in names),.40+1e-8)
    def test_no_estimated_price_executions(self):
        quotes,universe=fixture()
        del quotes[SYMS[5]]
        weights,status=target_weights(universe["candidates"],quotes,25.64,"2026-11-06",require_full=True)
        self.assertIsNone(weights)
        self.assertIn("UNPRICED_STOCKS",status)
    def test_full_universe_paper_plan_not_fake_fill(self):
        quotes,universe=fixture()
        quant={"autonomous_universe":universe,
               "screener":{"ranked":[]},
               "vix_trigger_policy":{"latest_vix_close":25.64,"latest_vix_date":"2026-11-06"}}
        a=update_paper_state(None,quant,quotes,"2026-11-06")
        self.assertEqual(a["trade_count"],0)
        self.assertEqual(len(a["pending"]["weights"]),40)
        self.assertEqual(a["cash"],1000)
        self.assertEqual(a["allocation_method"],"40_STOCK_BROAD_DIVERSIFIED")
    def test_upgrade_unfilled_legacy_order(self):
        quotes,universe=fixture()
        old={"screener":{"ranked":[{"ticker":t,"rank_eligible":True} for t in SYMS[:8]]},
             "vix_trigger_policy":{"latest_vix_close":25.64,"latest_vix_date":"2026-11-06"}}
        p=update_paper_state(None,old,quotes,"2026-11-06")
        self.assertEqual(len(p["pending"]["weights"]),8)
        enhanced={**old,"autonomous_universe":universe}
        upgraded=update_paper_state(p,enhanced,quotes,"2026-11-06")
        self.assertEqual(len(upgraded["pending"]["weights"]),40)
        self.assertEqual(upgraded["trade_count"],0)
        self.assertEqual(upgraded["cash"],1000)
        self.assertEqual(upgraded,update_paper_state(upgraded,enhanced,quotes,"2026-11-06"))

if __name__=="__main__":unittest.main()
