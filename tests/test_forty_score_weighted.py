"""Causal investability-style score-weighted historical Sharpe regression tests."""
import unittest,math
from datetime import date,timedelta
from scripts.forty_score_weighted_backtest import simulate_forty_score_weighted,trailing_signal_candidates
from scripts.quant_strategy import SECTOR_BANDS
SYMS=list(dict.fromkeys(t for v in SECTOR_BANDS.values() for t in v))
assert len(SYMS)==40

def fixture():
    days=[];d=date(2025,1,1)
    while len(days)<245:
        if d.weekday()<5:days.append(d.isoformat())
        d+=timedelta(days=1)
    q={}
    for i,t in enumerate(SYMS+["QQQ","XLK"]):
        q[t]={"bars":[(day,100*math.exp((.0002+(i%9)*.00015)*j+
                    .015*math.sin(.17*j+i*.57))) for j,day in enumerate(days)]}
    q["VIX"]={"bars":[(day,12 if j<120 else 28 if j<185 else 36) for j,day in enumerate(days)]}
    return days,q

class WeightedHistoricalTests(unittest.TestCase):
    def test_full_and_ipo_late_entries(self):
        dates,q=fixture()
        r=simulate_forty_score_weighted(q,SYMS,dates[124],vix_trigger=True)
        self.assertEqual(r["status"],"COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC")
        self.assertEqual(r["maximum_active_names"],40)
        self.assertIsNotNone(r["metrics"]["sharpe_rf0"])
        self.assertIsNotNone(r["benchmarks"]["QQQ"]["sharpe_rf0"])
        self.assertFalse(r["assumptions"]["historical_fundamental_scores_used"])
        q["GEV"]["bars"]=q["GEV"]["bars"][100:]
        r=simulate_forty_score_weighted(q,SYMS,dates[124],vix_trigger=False)
        self.assertEqual(r["status"],"COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC")
        self.assertEqual(r["minimum_active_names"],39)
        self.assertEqual(r["end_active_names"],40)
    def test_historical_signal_cannot_see_future(self):
        dates,q=fixture()
        bars={t:dict(v["bars"]) for t,v in q.items()}
        before=trailing_signal_candidates(bars,SYMS,dates,140)
        for t in SYMS:
            bars[t][dates[141]]=9999999.
        after=trailing_signal_candidates(bars,SYMS,dates,140)
        self.assertEqual(before,after)
        self.assertEqual(len(after),40)
    def test_vix_missing_strict_failure(self):
        dates,q=fixture()
        q.pop("VIX")
        r=simulate_forty_score_weighted(q,SYMS,dates[124],vix_trigger=True)
        self.assertEqual(r["status"],"INSUFFICIENT_VIX_HISTORY")
    def test_missing_held_price_strict_failure(self):
        dates,q=fixture()
        q["AMD"]["bars"]=[x for x in q["AMD"]["bars"] if x[0]!=dates[161]]
        r=simulate_forty_score_weighted(q,SYMS,dates[124],vix_trigger=False)
        self.assertEqual(r["status"],"MISSING_HELD_RETURN")
    def test_trading_cost_not_ignored(self):
        dates,q=fixture()
        low=simulate_forty_score_weighted(q,SYMS,dates[124],trade_bps=0)
        high=simulate_forty_score_weighted(q,SYMS,dates[124],trade_bps=20)
        self.assertEqual(low["status"],"COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC")
        self.assertEqual(high["status"],"COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC")
        self.assertGreater(low["metrics"]["ending_nav"],high["metrics"]["ending_nav"])
    def test_no_future_six_factor_claim(self):
        dates,q=fixture()
        r=simulate_forty_score_weighted(q,SYMS,dates[124],vix_trigger=True)
        self.assertFalse(r["assumptions"]["historical_supply_alpha_used"])
        self.assertTrue(r["assumptions"]["NOT_DIRECT_BACKTEST_OF_CURRENT_AUTONOMOUS_PAPER_SCORES"])

if __name__=="__main__":unittest.main()
