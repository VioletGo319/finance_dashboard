"""Point-in-time validation for energy, power and battery storage labels."""
import json
import unittest
from pathlib import Path
from scripts.refresh import load_infrastructure_attributes

ROOT=Path(__file__).resolve().parents[1]

class TestInfrastructure(unittest.TestCase):
    def test_three_dimensions(self):
        d=load_infrastructure_attributes("2026-11-08")
        self.assertEqual(set(x["id"] for x in d["dimensions"]),{"energy","power","storage"})
        self.assertTrue(d["unverified_is_unknown"])

    def test_product_claims_not_customer_contracts(self):
        d=load_infrastructure_attributes("2026-11-08")
        self.assertGreaterEqual(len(d["exposures"]),5)
        for x in d["exposures"]:
            self.assertEqual(x["status"],"verified_product")
            self.assertIs(x["customer_verified"],False)
            self.assertTrue(x["source"].startswith("https://"))
            self.assertLessEqual(x["verified_on"],"2026-11-08")

    def test_dated_evidence_is_not_used_before_publication(self):
        d=load_infrastructure_attributes("2020-01-01")
        self.assertEqual(d["exposures"],[])

    def test_missing_is_not_zero(self):
        d=load_infrastructure_attributes("2026-11-08")
        self.assertNotIn(("MU","storage"),{(e["ticker"],e["dimension"]) for e in d["exposures"]})
        self.assertEqual(d["handling"]["missing"],"unknown_not_zero")

    def test_alpha_weights_unchanged(self):
        from scripts.refresh import WEIGHTS
        self.assertAlmostEqual(sum(WEIGHTS.values()),1.0)
        self.assertEqual(WEIGHTS["acceleration"],.30)
        self.assertEqual(WEIGHTS["policy"],.10)

if __name__=="__main__":
    unittest.main()
