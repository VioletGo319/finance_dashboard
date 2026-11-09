"""Autonomous paper ledger: causal delayed fills, replay, risk and safety."""
import unittest
from datetime import date,timedelta
from scripts.autonomous_paper import update_paper_state, target_weights, paper_performance

def sample(day="2026-11-06",vix=25.64):
    symbols=["AMD","TSM","AVGO","MU","ANET","GLW","APH","VRT"]
    quotes={s:{"close":100+i*4,"price_date":day} for i,s in enumerate(symbols)}
    ranked=[{"ticker":s,"rank_eligible":True} for s in symbols]
    quant={"vix_trigger_policy":{"latest_vix_date":day,"latest_vix_close":vix},
           "screener":{"ranked":ranked}}
    return quant,quotes

class AutonomousPaperTest(unittest.TestCase):
    def test_proposal_not_filled_same_close_and_replay(self):
        q,p=sample()
        a=update_paper_state(None,q,p,"2026-11-06")
        self.assertEqual(a["cash"],1000)
        self.assertEqual(a["trade_count"],0)
        self.assertEqual(a["pending"]["signal_day"],"2026-11-06")
        self.assertEqual(a["pending"]["target_stock_exposure"],.75)
        self.assertEqual(a,update_paper_state(a,q,p,"2026-11-06"))
    def test_fills_on_new_close_then_no_duplicate(self):
        q,p=sample()
        a=update_paper_state(None,q,p,"2026-11-06")
        q2,p2=sample("2026-11-09")
        b=update_paper_state(a,q2,p2,"2026-11-09")
        self.assertGreater(b["trade_count"],0)
        self.assertEqual(b["last_fill_day"],"2026-11-09")
        self.assertGreater(b["cash"],0)
        self.assertLessEqual(b["cash"],1000)
        self.assertGreater(b["total_fees"],0)
        self.assertEqual(b,update_paper_state(b,q2,p2,"2026-11-09"))
        self.assertFalse(b["live_enabled"])
    def test_cash_only_when_vix_low(self):
        q,p=sample(vix=13)
        a=update_paper_state(None,q,p,"2026-11-06")
        self.assertEqual(a["pending"]["weights"],{})
        self.assertEqual(a["pending"]["target_stock_exposure"],0)
        self.assertEqual(a["cash"],1000)
    def test_nonexistent_vix_halting(self):
        q,p=sample()
        q["vix_trigger_policy"]["latest_vix_close"]=None
        a=update_paper_state(None,q,p,"2026-11-06")
        self.assertEqual(a["status"],"HALTED_MISSING_VIX")
        self.assertEqual(a["trade_count"],0)
    def test_risk_constraints(self):
        q,p=sample()
        w,status=target_weights(q["screener"]["ranked"],p,25.64,"2026-11-06")
        self.assertEqual(status,"READY")
        self.assertLessEqual(sum(w.values()),.75+1e-8)
        self.assertTrue(all(v<=.15+1e-8 for v in w.values()))
        groups={}
        from scripts.autonomous_paper import sector
        for s,v in w.items():groups[sector(s)]=groups.get(sector(s),0)+v
        self.assertTrue(all(v<=.40+1e-8 for v in groups.values()))
    def test_paper_sharpe_requires_observed_sessions(self):
        history=[{"date":f"2026-08-{i:02d}","equity":1000+i} for i in range(1,10)]
        result=paper_performance(history)
        self.assertIsNone(result["sharpe_rf0"])
        self.assertEqual(result["status"],"INSUFFICIENT_OBSERVED_PAPER_SESSIONS")
        long=[{"date":(date(2026,1,1)+timedelta(days=i)).isoformat(),
               "equity":1000*(1.001+0.003*((i%3)-1))**i}
              for i in range(34)]
        result=paper_performance(long)
        self.assertEqual(result["status"],"COMPUTED_FROM_FORWARD_PAPER_CLOSES")
        self.assertTrue(result["not_from_backtest"])
        self.assertIsNotNone(result["sharpe_rf0"])
    def test_duplicate_paper_dates_not_used_twice(self):
        history=[{"date":"2026-11-06","equity":1000},
                 {"date":"2026-11-06","equity":1000}]
        self.assertEqual(paper_performance(history)["observed_sessions"],1)
    def test_missing_price_prevents_fill(self):
        q,p=sample()
        a=update_paper_state(None,q,p,"2026-11-06")
        q2,p2=sample("2026-11-09")
        del p2["AMD"]
        b=update_paper_state(a,q2,p2,"2026-11-09")
        self.assertTrue(b["status"].startswith("HALTED"))
        self.assertEqual(b["trade_count"],0)

if __name__=="__main__":
    unittest.main()
