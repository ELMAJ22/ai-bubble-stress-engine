import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import update_data as U  # noqa: E402

CFG = json.loads((ROOT / "data" / "config_v0.2.json").read_text())
BASE = json.loads((ROOT / "data" / "indicators_2026-10-02.json").read_text())
TODAY = dt.date(2026, 10, 3)
FRESH_CAPE = {"cape": {"value": 40.9, "obs": "2026-09", "fetched": "2026-10-02", "source": "t"}}


def composite(state):
    rows, flags = U.build_indicators(BASE, state, CFG, TODAY)
    return U.score_all(rows, CFG)["Protocol weights"], rows, flags


class Parsing(unittest.TestCase):
    def test_fred_takes_last_numeric_row(self):
        text = "observation_date,BAMLC0A0CM\n2026-09-29,0.84\n2026-09-30,0.86\n2026-10-01,.\n"
        self.assertEqual(U.parse_fred_csv(text), ("2026-09-30", 0.86))

    def test_fred_rejects_empty(self):
        with self.assertRaises(ValueError):
            U.parse_fred_csv("observation_date,X\n2026-10-01,.\n")

    def test_shiller_latest_month(self):
        hdr = ["Date", "P", "D", "E", "CPI", "", "Rate GS10", "", "", "", "", "", "Cyclically Adjusted Price Earnings Ratio P/E10 or CAPE"]
        rows = [["Title"], hdr,
                [2026.08] + [0] * 11 + [40.2],
                [2026.09] + [0] * 11 + [40.9],
                [2026.1] + [0] * 11 + [41.3],
                ["", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ""]]
        self.assertEqual(U.parse_shiller_rows(rows), ("2026-10", 41.3))
        self.assertEqual(U.parse_shiller_rows(rows[:4])[0], "2026-09")

    def test_shiller_missing_column(self):
        with self.assertRaises(ValueError):
            U.parse_shiller_rows([["a", "b"], [2026.1, 3]])


class Scoring(unittest.TestCase):
    def test_launch_values_reproduce_v01(self):
        (score, conf, _), rows, flags = composite(FRESH_CAPE)
        self.assertAlmostEqual(score, 58.0, delta=0.1)
        self.assertAlmostEqual(conf, 0.25, delta=0.01)
        self.assertEqual(len(rows), 17)
        self.assertEqual(flags, {})

    def test_credit_spread_added_and_lowers_stress(self):
        state = dict(FRESH_CAPE, ig_oas={"value": 0.9, "obs": "2026-10-02", "fetched": "2026-10-03", "source": "t"})
        (score, _, comps), rows, _ = composite(state)
        self.assertEqual(len(rows), 18)
        self.assertLess(score, 58.0)
        self.assertGreater(score, 50.0)
        self.assertLess(comps["F"]["s"], 57.4)

    def test_wide_spread_raises_financing_stress(self):
        state = dict(FRESH_CAPE, ig_oas={"value": 2.5, "obs": "x", "fetched": "2026-10-03", "source": "t"})
        (_, _, comps), _, _ = composite(state)
        self.assertGreater(comps["F"]["s"], 57.4)

    def test_stale_value_halves_confidence(self):
        state = {"cape": {"value": 40.9, "obs": "2026-05", "fetched": "2026-06-01", "source": "t"}}
        (_, conf_stale, _), rows, flags = composite(state)
        (_, conf_fresh, _), _, _ = composite(FRESH_CAPE)
        self.assertEqual(flags, {"cape": "stale"})
        self.assertLess(conf_stale, conf_fresh)

    def test_new_cape_moves_score(self):
        state = {"cape": {"value": 44.0, "obs": "x", "fetched": "2026-10-03", "source": "t"}}
        (score, _, _), _, _ = composite(state)
        self.assertGreater(score, 58.0)


class Outputs(unittest.TestCase):
    def test_snapshot_dedupes_by_date(self):
        results = U.score_all(BASE, CFG)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.csv"
            p.write_text("date,version,composite_protocol,composite_equal,composite_valuation_halved,confidence\n2026-10-02,ABSI v0.1,58.0,56.8,54.4,0.25\n")
            U.write_snapshot(p, "2026-10-03", "ABSI v0.2", results)
            U.write_snapshot(p, "2026-10-03", "ABSI v0.2", results)
            lines = p.read_text().strip().splitlines()
            self.assertEqual(len(lines), 3)
            self.assertTrue(lines[1].startswith("2026-10-02"))

    def test_readme_block_replaced_in_place(self):
        results = U.score_all(BASE, CFG)
        block = U.render_block("2026-10-03", "ABSI v0.2", results, 17, 34, {}, [])
        readme = "top\n" + U.START + "\nold\n" + U.END + "\nbottom\n"
        out = U.replace_block(readme, block)
        self.assertTrue(out.startswith("top\n"))
        self.assertTrue(out.endswith("\nbottom\n"))
        self.assertNotIn("old", out)
        self.assertIn("58 / 100", out)

    def test_failed_fetches_keep_state_and_still_write(self):
        with tempfile.TemporaryDirectory() as d:
            data = Path(d)
            for n in ("config_v0.2.json", "indicators_2026-10-02.json", "auto_state.json", "snapshots.csv"):
                (data / n).write_text((ROOT / "data" / n).read_text())
            orig = U.fetch
            U.fetch = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("offline"))
            try:
                results, errors = U.run(today=dt.date(2026, 10, 3), data=data, readme_path=data / "README.md")
            finally:
                U.fetch = orig
            self.assertEqual(len(errors), 2)
            self.assertAlmostEqual(results["Protocol weights"][0], 58.0, delta=0.1)
            self.assertEqual(json.loads((data / "latest.json").read_text())["indicators_used"], 17)


if __name__ == "__main__":
    unittest.main()
