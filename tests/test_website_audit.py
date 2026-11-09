"""Static regression guards for the November cross-page audit remediation."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class WebsiteAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=(ROOT/"index.html").read_text(encoding="utf-8")
        cls.quant=(ROOT/"quant-lab.js").read_text(encoding="utf-8")
        cls.pipeline=(ROOT/"scripts/quant_pipeline.py").read_text(encoding="utf-8")

    def test_same_supply_alpha_source_and_fail_closed(self):
        self.assertIn("window.M7_LIVE_DATA=structuredClone(fresh)",self.index)
        self.assertIn("m7-supplier-snapshot-updated",self.index)
        self.assertIn("source_alpha_by_ticker",self.quant)
        self.assertIn("sameSupplierVersion",self.quant)
        self.assertIn('const row=sameSupplierVersion?',self.quant)
        self.assertIn("supplier_snapshot_fingerprint",self.pipeline)
        self.assertIn("source_snapshot",self.pipeline)

    def test_archived_8_stocks_distinct_from_live_40(self):
        self.assertIn("ARCHIVED_8_NAME_NON_EXECUTABLE",self.pipeline)
        self.assertIn("audit_archived",self.quant)
        self.assertIn("audit_active",self.quant)
        self.assertNotIn('selected.map(x=>',self.quant)

    def test_completeness_replaces_average_alpha(self):
        self.assertIn("coverageView='high'",self.index)
        self.assertIn("coverageGroup",self.index)
        self.assertIn('coverageView===',self.index)
        self.assertIn("加权因子覆盖完整度",self.index)
        self.assertNotIn("综合 Alpha 均值 <span>",self.index)

    def test_capex_proxy_not_surprise(self):
        self.assertIn("客户资本开支同比代理",self.index)
        self.assertNotIn("客户需求超预期",self.index)
        self.assertIn("不是分析师预期惊喜",self.index)

    def test_keyboard_and_narrow_desktop(self):
        self.assertIn("aria-sort",self.index)
        self.assertIn("keydown",self.index)
        self.assertIn("tabindex=",self.index)
        self.assertIn("@media(max-width:1280px)",self.index)
        self.assertIn("flex-wrap:wrap",self.index)

    def test_backtest_gates_not_overclaimed(self):
        self.assertIn("validated_performance_claim_allowed",self.pipeline)
        self.assertIn('"status":"PENDING"',self.pipeline)
        self.assertIn("backtestValidationView",self.quant)
        self.assertIn("validation_status",self.quant)

if __name__=="__main__":
    unittest.main()
