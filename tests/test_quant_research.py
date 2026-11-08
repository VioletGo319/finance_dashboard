"""Quant research engine unit tests: causality, filing cutoffs, missing data, costs.

Synthetic fixtures are confined to tests. They are NEVER exported as returns.
"""
import unittest,math
from datetime import date,timedelta
from scripts.quant_fundamentals import extract_fundamentals
from scripts.quant_strategy import simulate_daily_close,investment_score,_metrics

def mock_facts():
  annual=[
    {"start":"2024-01-01","end":"2024-12-31","filed":"2025-02-14","form":"10-K","val":100},
    {"start":"2025-01-01","end":"2025-12-31","filed":"2026-02-10","form":"10-K","val":130},
    {"start":"2025-01-01","end":"2025-12-31","filed":"2026-12-01","form":"10-K/A","val":200},
  ]
  shares=[
    {"end":"2025-12-31","filed":"2026-02-10","form":"10-K","val":100000000},
    {"end":"2026-09-30","filed":"2026-10-20","form":"10-Q","val":110000000},
  ]
  return {"facts":{
    "us-gaap":{"RevenueFromContractWithCustomerExcludingAssessedTax":{"units":{"USD":annual}}},
    "dei":{"EntityCommonStockSharesOutstanding":{"units":{"shares":shares}}}
  }}

class QuantPipelineTests(unittest.TestCase):
 def test_no_future_fundamental(self):
  f=extract_fundamentals(mock_facts(),"2025-12-31","TEST",123)
  self.assertEqual(f["revenue_fy_usd"],100)
  self.assertIsNone(f["revenue_growth_yoy"])
  f2=extract_fundamentals(mock_facts(),"2026-11-08","TEST",123)
  self.assertEqual(f2["revenue_fy_usd"],130)
  self.assertAlmostEqual(f2["revenue_growth_yoy"],.30)
  self.assertEqual(f2["shares_outstanding"],110000000)
  self.assertEqual(f2["revenue_filed"],"2026-02-10")
 def test_unavailable_fundamentals_do_not_rank(self):
  meta={t:{"close":100,"monitor_score":50,"provisional_alpha":60,"coverage":.6,"price_date":"2026-11-06"} for t in ["A","B","C"]}
  rank=investment_score(["A","B","C"],{},meta)
  self.assertEqual(sum(x["investability_score"] is not None for x in rank),0)
 def test_backtest_is_price_only_causal_and_costly(self):
  start=date(2025,1,1);days=[]
  while len(days)<150:
   d=start+timedelta(days=len(days)*2) if False else None
   break
  d=start
  while len(days)<145:
   if d.weekday()<5:days.append(d.isoformat())
   d+=timedelta(days=1)
  ticks=["TSM","AVGO","AMD","ANET","MRVL"]
  series={}
  for i,t in enumerate(ticks+["QQQ","XLK"]):
   series[t]={"bars":[(day,100*(1+(.0003+(i%5)*.0002))**j*(1+.003*math.sin(j*.3+i))) for j,day in enumerate(days)]}
  clean=simulate_daily_close(series,ticks,top_n=3,trade_bps=0)
  costly=simulate_daily_close(series,ticks,top_n=3,trade_bps=10)
  self.assertEqual(clean["status"],"COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC")
  self.assertLessEqual(costly["metrics"]["ending_nav"],clean["metrics"]["ending_nav"])
  self.assertTrue(all(x["date"]>x["signal_date"] for x in clean["trades"]))
  self.assertEqual(clean["benchmarks"]["QQQ"]["days"],clean["metrics"]["days"])
  self.assertGreater(len(clean["curve"]),20)
 def test_gap_failure_and_no_fabrication(self):
  self.assertEqual(simulate_daily_close({},["TSM"])["status"],"INSUFFICIENT_BENCHMARK_HISTORY")
 def test_metrics_not_probability(self):
  m=_metrics([.01,-.02,.005],[.5],10)
  self.assertTrue(-1<=m["max_drawdown"]<=0)
  self.assertNotIn("win_probability",m)
if __name__=="__main__":
 unittest.main()
