"""Regression tests for dated 1-hop/2-hop graph and evidence products."""
import unittest
from copy import deepcopy
from scripts.network import graph_snapshot,compute_paths,load_universe
from scripts.refresh import WEIGHTS,TICKERS

class TestGraph(unittest.TestCase):
    def test_universe(self):
        u=load_universe()
        self.assertEqual(len(u["suppliers"]),40)
        self.assertEqual(len({x["ticker"] for x in u["suppliers"]}),40)
        self.assertEqual(len(TICKERS),40)
        self.assertEqual(sum(x["cohort"]=="core" for x in u["suppliers"]),12)

    def test_multiplicative_two_hop(self):
        graph={"version":"test","hop2_discount":.7,
         "edge_types":{"disclosed":{"proxy_weight":.8},"award":{"proxy_weight":.65}},
         "edges":[
          {"supplier":"AMAT","customer":"TSM","edge_type":"award","date":"2025-12-03","source":"https://example.org/award","verified":True},
          {"supplier":"TSM","customer":"NVDA","edge_type":"disclosed","date":"2026-02-25","source":"https://example.org/filing","verified":True}]}
        d=compute_paths(graph,["AMAT","TSM"],"2026-11-07")
        p=[p for p in d["paths"] if p["supplier"]=="AMAT"]
        self.assertEqual(len(p),1)
        self.assertEqual(p[0]["path"],["AMAT","TSM","NVDA"])
        self.assertEqual(p[0]["hops"],2)
        self.assertAlmostEqual(p[0]["weight"],.65*.8*.7)
        self.assertEqual(len(p[0]["sources"]),2)

    def test_future_edge_not_allowed(self):
        _,g=graph_snapshot("2025-11-01")
        self.assertFalse(any(p["via"]=="TSM" for p in g["paths"]))
        _,g2=graph_snapshot("2026-11-07")
        self.assertGreaterEqual(len([p for p in g2["paths"] if p["via"]=="TSM"]),5)

    def test_three_hop_evidence_product(self):
        _,g=graph_snapshot("2026-11-07")
        paths=[p for p in g["paths"] if p["supplier"]=="UCTT" and p["customer"]=="NVDA" and p["hops"]==3]
        self.assertEqual(len(paths),2)
        self.assertEqual({p["via"] for p in paths},{"AMAT","LRCX"})
        self.assertEqual({tuple(p["path"]) for p in paths},{("UCTT","AMAT","TSM","NVDA"),("UCTT","LRCX","TSM","NVDA")})
        for path in paths:
            self.assertAlmostEqual(path["weight"],.8*.65*.8*.7**2)
            self.assertEqual(len(path["sources"]),3)

    def test_no_fabricated_paths_from_candidate(self):
        _,g=graph_snapshot("2026-11-07")
        self.assertEqual(g["exposures"]["VST"]["paths"],0)
        self.assertTrue(g["exposures"]["VST"]["no_path_is_unknown"])

    def test_direct_vs_indirect(self):
        _,g=graph_snapshot("2026-11-07")
        self.assertGreater(g["exposures"]["AMAT"]["indirect_customers"],0)
        self.assertEqual(g["exposures"]["AMAT"]["direct_customers"],0)
        self.assertGreater(g["exposures"]["TSM"]["direct_customers"],0)

    def test_no_change_to_six_factor_weights(self):
        self.assertAlmostEqual(sum(WEIGHTS.values()),1.0)
        self.assertEqual(WEIGHTS["acceleration"],.30)

if __name__=="__main__":
    unittest.main()
