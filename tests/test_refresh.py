"""Offline checks for ranking and honest missing-data behavior."""
import copy
import json
import unittest
from pathlib import Path
from scripts.refresh import WEIGHTS, TICKERS, calculate, pct_rank, twenty_day_return, residual

class TestResearchPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=json.loads((Path(__file__).resolve().parents[1]/"data"/"latest.json").read_text())

    def test_fixed_universe(self):
        self.assertEqual(len(TICKERS),40)
        self.assertEqual(set(x["ticker"] for x in self.base["suppliers"]),set(TICKERS))
        self.assertAlmostEqual(sum(WEIGHTS.values()),1.)

    def test_percentile_requires_peers(self):
        self.assertIsNone(pct_rank(1, [1,2]))
        self.assertEqual(pct_rank(1,[1,2,3]),0.)
        self.assertEqual(pct_rank(2,[1,2,3]),50.)
        self.assertEqual(pct_rank(3,[1,2,3]),100.)

    def test_missing_quotes_stay_missing(self):
        data=copy.deepcopy(self.base)
        no_quotes={t:{"bars":[],"url":None,"provider":None,"error":"unavailable"} for t in TICKERS}
        result=calculate(data,no_quotes)
        self.assertEqual(result["audit"]["market_prices_present"],0)
        for stock in result["suppliers"]:
            self.assertIsNone(stock["close"])
            self.assertIsNone(stock["previous_close"])
            self.assertIsNone(stock["alpha"])
            self.assertIsNone(stock["price_source"])

    def test_twenty_session_returns(self):
        self.assertIsNone(twenty_day_return([("2020-01-01",100)]))
        bars=[(str(i),100+i) for i in range(21)]
        self.assertAlmostEqual(twenty_day_return(bars),.20)

    def test_residual_needs_synchronized_history(self):
        self.assertIsNone(residual([("a",1),("b",2)],[("a",1),("b",2)]))

    def test_missing_factors_never_issue_official_alpha(self):
        for stock in self.base["suppliers"]:
            if any(stock["factors"].get(k) is None for k in WEIGHTS):
                self.assertIsNone(stock["alpha"])

if __name__=="__main__":
    unittest.main()
