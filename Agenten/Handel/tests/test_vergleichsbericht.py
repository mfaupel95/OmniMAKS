import os
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

HANDEL = Path(__file__).resolve().parents[1]
if str(HANDEL) not in sys.path:
    sys.path.insert(0, str(HANDEL))

import vergleichsbericht as vb


class CollectorTests(unittest.TestCase):
    def test_active_map_is_parsed_without_importing_duration_module(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "dauerlauf.py"
            source.write_text(
                'SPUREN = {"alpha": {"ordner": "alpha"}, '
                '"llm_stunde": {"arme": (("llm_stunde_arm-L", os.path.join("laeufe", "L")),)}}\n',
                encoding="utf-8")
            self.assertEqual(vb.active_traces(source), ["alpha", "llm_stunde_arm-L"])

    def test_cost_witness_requires_explicit_xperp_cost_fields(self):
        adapter = SimpleNamespace()
        self.assertIsNone(vb._fee_witness(adapter, "xperp", [
            {"gebuehr_pct": "0.001", "funding_pct": ""}]))
        self.assertEqual(vb._fee_witness(adapter, "xperp", [
            {"gebuehr_pct": "0", "funding_pct": "0"}]), "rundenkosten-xperp")

    def test_context_restores_adapter_globals_after_exception(self):
        fake = SimpleNamespace(HIER=Path("old"), STUFE="alt")
        with self.assertRaises(RuntimeError):
            with vb._reader_context(fake, Path("data"), "hoch"):
                self.assertEqual(fake.HIER, Path("data"))
                self.assertEqual(fake.STUFE, "hoch")
                raise RuntimeError("stop")
        self.assertEqual(fake.HIER, Path("old"))
        self.assertEqual(fake.STUFE, "alt")

    def test_missing_universe_and_costs_remain_explicit(self):
        rows = [{"zeit": "2026-10-01T00:00:00+00:00", "inst": "BTC-USDC",
                 "modus": "papier", "universum": "", "aktion": "noop"}]
        adapter = SimpleNamespace(HIER=Path("before"), STUFE="old")
        adapter.zeilen = lambda trace: rows
        adapter.runden_fuer = lambda trace, part, stand=None: []
        adapter.offene_positionen = lambda trace, stage: 0
        adapter.einheit_fuer = lambda trace: "USDC"
        with tempfile.TemporaryDirectory() as temp:
            result = vb.collect(Path(temp), stages=("niedrig",), adapter=adapter,
                                traces=("synthetic",))
        self.assertEqual(result[0]["universum"], None)
        self.assertIn("Universum fehlt im Journal", result[0]["datenqualitaet"])
        self.assertIn("Netto-Kostenbehandlung für dieses Buch nicht belegt",
                      result[0]["datenqualitaet"])
        self.assertIsNone(result[0]["startkapital"])
        self.assertEqual(result[0]["offene_positionen_stand"], "Berichtszeitpunkt")

    def test_interleaved_instruments_keep_their_round_pairs_together(self):
        rows = [
            {"zeit": "2026-10-01T00:00:00+00:00", "inst": "BTC-USDC", "modus": "papier", "universum": "top"},
            {"zeit": "2026-10-01T00:01:00+00:00", "inst": "ETH-USDC", "modus": "papier", "universum": "top"},
            {"zeit": "2026-10-01T00:02:00+00:00", "inst": "BTC-USDC", "modus": "papier", "universum": "top"},
            {"zeit": "2026-10-01T00:03:00+00:00", "inst": "ETH-USDC", "modus": "papier", "universum": "top"},
        ]
        calls = []
        adapter = SimpleNamespace(HIER=Path("before"), STUFE=None)
        adapter.zeilen = lambda trace: rows
        def pair(trace, part, stand=None):
            calls.append([row["inst"] for row in part])
            if stand is not None:
                stand.update({"unpaarig": 0, "zweideutig": 0, "offen": 0})
            return []
        adapter.runden_fuer = pair
        adapter.offene_positionen = lambda trace, stage: 0
        adapter.einheit_fuer = lambda trace: "USDC"
        with tempfile.TemporaryDirectory() as temp:
            result = vb.collect(Path(temp), stages=("niedrig",), adapter=adapter,
                                traces=("synthetic",))
        self.assertEqual(len(result), 2)
        self.assertEqual({row["instrument"] for row in result}, {"BTC-USDC", "ETH-USDC"})
        self.assertEqual(calls, [["BTC-USDC", "BTC-USDC"], ["ETH-USDC", "ETH-USDC"]])

    def test_mode_change_splits_only_the_affected_instrument_stream(self):
        rows = [
            {"zeit": "2026-10-01T00:00:00+00:00", "inst": "BTC-USDC", "modus": "papier", "universum": "top"},
            {"zeit": "2026-10-01T00:01:00+00:00", "inst": "ETH-USDC", "modus": "papier", "universum": "top"},
            {"zeit": "2026-10-01T00:02:00+00:00", "inst": "BTC-USDC", "modus": "live", "universum": "top"},
        ]
        calls = []
        adapter = SimpleNamespace(HIER=Path("before"), STUFE=None)
        adapter.zeilen = lambda trace: rows
        def pair(trace, part, stand=None):
            calls.append([(row["inst"], row["modus"]) for row in part])
            return []
        adapter.runden_fuer = pair
        adapter.offene_positionen = lambda trace, stage: 0
        adapter.einheit_fuer = lambda trace: "USDC"
        with tempfile.TemporaryDirectory() as temp:
            result = vb.collect(Path(temp), stages=("niedrig",), adapter=adapter,
                                traces=("synthetic",))
        self.assertEqual(len(result), 3)
        self.assertEqual(calls, [[("BTC-USDC", "papier")],
                                 [("ETH-USDC", "papier")],
                                 [("BTC-USDC", "live")]])

    def test_section_numbers_are_stable_when_instrument_first_seen_order_differs(self):
        rows_by_trace = {
            "trace-a": [
                {"zeit": "2026-10-01T00:00:00+00:00", "inst": "BTC-USDC", "modus": "papier", "universum": "top"},
                {"zeit": "2026-10-01T00:01:00+00:00", "inst": "ETH-USDC", "modus": "papier", "universum": "top"},
            ],
            "trace-b": [
                {"zeit": "2026-10-01T00:00:00+00:00", "inst": "ETH-USDC", "modus": "papier", "universum": "top"},
                {"zeit": "2026-10-01T00:01:00+00:00", "inst": "BTC-USDC", "modus": "papier", "universum": "top"},
            ],
        }
        adapter = SimpleNamespace(HIER=Path("before"), STUFE=None)
        adapter.zeilen = lambda trace: rows_by_trace[trace]
        adapter.runden_fuer = lambda trace, part, stand=None: []
        adapter.offene_positionen = lambda trace, stage: 0
        adapter.einheit_fuer = lambda trace: "USDC"
        with tempfile.TemporaryDirectory() as temp:
            result = vb.collect(Path(temp), stages=("niedrig",), adapter=adapter,
                                traces=("trace-a", "trace-b"))
        btc_sections = {
            row["abschnitt"] for row in result if row["instrument"] == "BTC-USDC"
        }
        self.assertEqual(len(btc_sections), 1)
        self.assertEqual(btc_sections, {"abschnitt-001"})

    def test_unclosed_entries_are_reported_as_warning_not_rank_blocker(self):
        rows = [{"zeit": "2026-10-01T00:00:00+00:00", "inst": "BTC-USDC",
                 "modus": "papier", "universum": "top"}]
        adapter = SimpleNamespace(HIER=Path("before"), STUFE=None)
        adapter.zeilen = lambda trace: rows
        def pair(trace, part, stand=None):
            if stand is not None:
                stand.update({"unpaarig": 0, "zweideutig": 0, "offen": 1})
            return []
        adapter.runden_fuer = pair
        adapter.offene_positionen = lambda trace, stage: 1
        adapter.einheit_fuer = lambda trace: "USDC"
        with tempfile.TemporaryDirectory() as temp:
            result = vb.collect(Path(temp), stages=("niedrig",), adapter=adapter,
                                traces=("synthetic",))
        self.assertEqual(result[0]["datenqualitaet"], [
            "Netto-Kostenbehandlung für dieses Buch nicht belegt"])
        self.assertEqual(result[0]["warnungen"], [
            "Journal-Paarer meldet offene Einstiege"])

    def test_source_path_uses_special_book_mapping_and_stage_suffix(self):
        rows = [{"zeit": "2026-10-01T00:00:00+00:00", "inst": "BTC-USDC",
                 "modus": "papier", "universum": "top"}]
        adapter = SimpleNamespace(HIER=Path("before"), STUFE=None)
        adapter.zeilen = lambda trace: rows
        adapter.runden_fuer = lambda trace, part, stand=None: []
        adapter.offene_positionen = lambda trace, stage: 0
        adapter.einheit_fuer = lambda trace: "USDC"
        adapter.risikostufe = SimpleNamespace(
            datei_fuer=lambda filename, stage: filename.replace(".csv", "." + stage + ".csv"))
        def locate(trace, filename):
            if trace == "llm_stunde_ema1h-R":
                return "llm_stunde/laeufe/ema1h-R", filename
            return trace, filename
        adapter._ort = locate
        root = Path("data-root")
        with tempfile.TemporaryDirectory() as temp:
            result = vb.collect(root, stages=("mittel",), adapter=adapter,
                                traces=("llm_stunde_ema1h-R",))
        self.assertEqual(result[0]["quelle"], str(
            root / "llm_stunde/laeufe/ema1h-R/handelsjournal.mittel.csv"))

    def test_markdown_and_csv_share_computed_comparison_metrics(self):
        start = "2026-10-01T00:00:00+00:00"
        end = "2026-10-02T00:00:00+00:00"
        records = []
        for trace, net in (("a", 10.0), ("b", 20.0)):
            records.append({
                "spur": trace, "stufe": "niedrig", "instrument": "BTC-USDC",
                "modus": "papier", "universum": "top-10", "abschnitt": "seg-1",
                "einheit": "USDC", "zeitraum_start": start, "zeitraum_ende": end,
                "runden": [{"ausstieg_zeit": end, "netto": net,
                            "kosten_belegt": True}],
                "startkapital": 1000.0, "startkapital_zeitpunkt": start,
                "equity_curve": [{"zeit": start, "wert": 1000.0},
                                 {"zeit": end, "wert": 1000.0 + net}],
                "offene_positionen": 1, "datenqualitaet": [],
                "kostenbeleg": "journal-netto", "quelle": "source/" + trace,
            })
        with tempfile.TemporaryDirectory(dir=HANDEL) as temp:
            output = Path(temp) / "reports"
            groups = vb.write_report(records, output, data_root=Path(temp) / "input")
            with (output / "handelsspuren-vergleich.csv").open(encoding="utf-8-sig", newline="") as f:
                csv_rows = list(csv.DictReader(f))
            md_lines = (output / "handelsspuren-vergleich.md").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(csv_rows), 2)
        header = [part.strip() for part in md_lines[4].strip("|").split("|")]
        md_rows = [[part.strip() for part in line.strip("|").split("|")]
                   for line in md_lines[6:8]]
        self.assertEqual(header, list(csv_rows[0]))
        for csv_row, md_row in zip(csv_rows, md_rows):
            self.assertEqual(md_row, [str(csv_row[key]) for key in header])
        self.assertEqual({r["netto_pnl"] for r in csv_rows}, {"10.0", "20.0"})
        self.assertEqual({r["netto_rendite_pct"] for r in csv_rows}, {"1.0", "2.0"})
        self.assertTrue(all(r["drawdown_pct"] == "0.0" for r in csv_rows))
        self.assertTrue(all(r["rang"] for r in csv_rows))

    def test_report_directory_cannot_overlap_data_root(self):
        with tempfile.TemporaryDirectory(dir=HANDEL) as temp:
            root = Path(temp) / "data"
            root.mkdir()
            with self.assertRaisesRegex(ValueError, "überlappen"):
                vb.write_report([], root / "reports", data_root=root)


if __name__ == "__main__":
    unittest.main()
