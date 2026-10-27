import sys
import tempfile
import unittest
from pathlib import Path

HANDEL = Path(__file__).resolve().parents[1]
if str(HANDEL) not in sys.path:
    sys.path.insert(0, str(HANDEL))

import auswertung_alle as auswertung
from vergleichsbericht import _journal_source


class ZeilenStufenPfadTests(unittest.TestCase):
    def test_normales_und_abweichendes_journal_behalten_basispfad_je_stufe(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            layouts = {
                "xperp": ("xperp", "handelsjournal.csv"),
                "squeeze_eth": ("squeeze", "handelsjournal.eth.csv"),
                "nautilus_kraken_futures": (
                    "nautilus_kraken", "handelsjournal.futures.csv"),
            }
            stages = {"niedrig": None, "mittel": "mittel", "hoch": "hoch"}
            for trace, (folder, base_file) in layouts.items():
                for stage_name, suffix in stages.items():
                    filename = (base_file if suffix is None else
                                auswertung.risikostufe.datei_fuer(base_file, suffix))
                    path = root / folder / filename
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("marker\n%s-%s\n" % (trace, stage_name),
                                    encoding="utf-8")

            old_root, old_stage = auswertung.HIER, auswertung.STUFE
            try:
                auswertung.HIER = root
                for stage_name, suffix in stages.items():
                    auswertung.STUFE = suffix
                    for trace in layouts:
                        rows = auswertung.zeilen(trace)
                        self.assertEqual(rows[0]["marker"], "%s-%s" % (trace, stage_name))
            finally:
                auswertung.HIER, auswertung.STUFE = old_root, old_stage

    def test_collector_quelle_verwendet_sonderpfad_vor_stufensuffix(self):
        old_stage = auswertung.STUFE
        try:
            auswertung.STUFE = "hoch"
            root = Path("D:/synthetic-data")
            self.assertEqual(
                _journal_source(auswertung, root, "squeeze_eth"),
                str(root / "squeeze" / "handelsjournal.eth.hoch.csv"),
            )
            self.assertEqual(
                _journal_source(auswertung, root, "nautilus_kraken_futures"),
                str(root / "nautilus_kraken" / "handelsjournal.futures.hoch.csv"),
            )
        finally:
            auswertung.STUFE = old_stage


if __name__ == "__main__":
    unittest.main()
