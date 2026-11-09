"""Cross-page Supply Alpha snapshot contract and daily-score integrity."""
import unittest
from scripts.quant_pipeline import supplier_snapshot_fingerprint

def sample():
    return {
        "as_of":"2026-11-08","price_date":"2026-11-06",
        "model_version":"v3.2-40-multihop-proxy",
        "suppliers":[
           {"ticker":"STM","alpha":None,"provisional_alpha":73.24,
            "coverage":.9,"monitor_score":68.72,"price_date":"2026-11-06"},
           {"ticker":"AMD","alpha":None,"provisional_alpha":66.30,
            "coverage":.65,"monitor_score":60.22,"price_date":"2026-11-06"}
        ]}

class CrossPageConsistencyTests(unittest.TestCase):
    def test_order_independent_canonical_signature(self):
        a=sample()
        b=sample()
        b["suppliers"].reverse()
        self.assertEqual(supplier_snapshot_fingerprint(a),
                         supplier_snapshot_fingerprint(b))
    def test_value_or_source_date_mismatch_changes_fingerprint(self):
        a=sample();base=supplier_snapshot_fingerprint(a)
        for key,value in [("provisional_alpha",66.3),("coverage",.65),
                          ("monitor_score",41.0),("price_date","2026-11-05")]:
            b=sample();b["suppliers"][0][key]=value
            self.assertNotEqual(base,supplier_snapshot_fingerprint(b),key)
        b=sample();b["as_of"]="2026-11-07"
        self.assertNotEqual(base,supplier_snapshot_fingerprint(b))
    def test_snapshot_fingerprint_does_not_include_future_alpha(self):
        a=sample()
        # Add unrelated outputs and ensure the audited fields are the only
        # components included in the comparison contract.
        b=sample();b["future_prediction"]=12
        self.assertEqual(supplier_snapshot_fingerprint(a),
                         supplier_snapshot_fingerprint(b))
