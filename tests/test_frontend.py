"""Regression checks for interactive chart initialisation.

These guard against a previous bug where querySelector() was followed by
.forEach(), aborting the main render() before factors and network loaded.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TestDashboardFrontend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_no_single_element_selector_iteration(self):
        # $() returns querySelector (single element). Only $$() returns an array.
        bad = re.findall(r"(?<!\$)\$\(\s*['\"][^'\"]+['\"]\s*\)\.forEach\s*\(", self.html)
        self.assertEqual(bad, [], f"Single-element selector used as iterable: {bad}")

    def test_render_charts_are_called(self):
        render = re.search(r"function render\(\)\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(render)
        body = render.group(1)
        for name in ("renderFactorHeatmap", "renderContrib", "renderNetwork",
                     "renderPaths", "renderInfrastructure"):
            self.assertIn(name + "()", body)

    def test_page_elements_exist(self):
        for element in ("factorHeatmap","contribChart","networkSvg",
                        "networkFilter","pathRows","infraRows"):
            self.assertIn('id="' + element + '"',self.html)

    def test_multiple_nodes_are_selected_as_a_collection(self):
        for selector in ("#infraFilters [data-dim]","#infraRows tr[data-infra]",
                         "#pathRows [data-path-index]"):
            self.assertIn("$$('" + selector + "').forEach",self.html)

if __name__ == "__main__":
    unittest.main()
