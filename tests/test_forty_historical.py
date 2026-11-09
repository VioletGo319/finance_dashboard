"""40-stock causal price-only Sharpe reference tests; no fabricated market data."""
import unittest
from datetime import date,timedelta
from scripts.forty_backtest import simulate_forty_price_only
from scripts.quant_strategy import SECTOR_BANDS
SYMS=list(dict.fromkeys(t for stock in SECTOR_BANDS.values() for t in stock))
class FortyHistoricalTests(unittest.TestCase):
    def quotes(self):
        dates=[];d=date(2025,1,1)
        while len(dates)<240:
            if d.weekday()<5:dates.append(d.isoformat())
            d+=timedelta(days=1)
        quotes={}
        for i,t in enumerate(SYMS+["QQQ","XLK"]):
            quotes[t]={"bars":[(day,100*(1.0001+(i%7)*.00009)**j)
                               for j,day in enumerate(dates)]}
        quotes["VIX"]={"bars":[(day,12 if j<120 else 31) for j,day in enumerate(dates)]}
        return dates,quotes
    def test_all_40_included_when_listed(self):
        dates,q=self.quotes()
        r=simulate_forty_price_only(q,SYMS,dates[120],vix_trigger=True)
        self.assertEqual(r["status"],"COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC")
        self.assertEqual(r["end_active_names"],40)
        self.assertEqual(r["minimum_active_names"],40)
        self.assertLess(r["mean_stock_exposure"],1)
        self.assertIsNotNone(r["benchmarks"]["QQQ"]["sharpe_rf0"])
    def test_recent_listing_dynamically_enters(self):
        dates,q=self.quotes()
        q["GEV"]={"bars":q["GEV"]["bars"][110:]}
        r=simulate_forty_price_only(q,SYMS,dates[120])
        self.assertEqual(r["status"],"COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC")
        self.assertEqual(r["minimum_active_names"],39)
        self.assertEqual(r["end_active_names"],40)
    def test_missing_vix_halts_vix_version(self):
        dates,q=self.quotes()
        del q["VIX"]
        r=simulate_forty_price_only(q,SYMS,dates[120],vix_trigger=True)
        self.assertEqual(r["status"],"INSUFFICIENT_VIX_HISTORY")
    def test_missing_held_close_halts(self):
        dates,q=self.quotes()
        q["AMD"]["bars"]=[x for x in q["AMD"]["bars"] if x[0]!=dates[140]]
        r=simulate_forty_price_only(q,SYMS,dates[120])
        self.assertEqual(r["status"],"MISSING_HELD_RETURN")
    def test_no_cross_time_fundamental_backfill(self):
        dates,q=self.quotes()
        r=simulate_forty_price_only(q,SYMS,dates[120])
        self.assertFalse(r["assumptions"]["historical_fundamental_scores_used"])
        self.assertFalse(r["assumptions"]["historical_estimated_factors_used"])

if __name__=="__main__": unittest.main()
