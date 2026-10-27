"""Vertraege der getrennten, konservativen Optimierungslanes."""
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

HANDEL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HANDEL))
from optimierung import strategie, verbesserung
from optimierung.zyklus import _rotation, fuehre_zyklus_aus


ROOT = HANDEL.parents[1]
STAND = datetime(2026, 10, 25, 12, tzinfo=timezone.utc)


class GetrennteLanes(unittest.TestCase):
    def test_discovery_erzeugt_keine_kandidaten_aus_journalzeilen(self):
        traces = tuple(strategie._registry())
        self.assertEqual(strategie.finde_strategiekandidaten(traces, datenstand=STAND), [])
        self.assertEqual(verbesserung.finde_technische_verbesserungen(traces, datenstand=STAND), [])

    def test_discovery_nutzt_uebergebenes_zielregister(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "Agenten" / "Handel"
            base.mkdir(parents=True)
            (base / "dauerlauf.py").write_text(
                'SPUREN = {"eigene_spur": {"ordner": "eigene_spur"}}\n', encoding="utf-8")
            self.assertEqual(strategie.finde_strategiekandidaten(
                ["eigene_spur"], datenstand=STAND, repo=root), [])
            self.assertEqual(verbesserung.finde_technische_verbesserungen(
                ["eigene_spur"], datenstand=STAND, repo=root), [])
            with self.assertRaises(KeyError):
                strategie.finde_strategiekandidaten(["xperp"], datenstand=STAND, repo=root)

    def test_falscher_datenstand_ist_keine_stille_luecke(self):
        with self.assertRaises(TypeError):
            strategie.finde_strategiekandidaten([], datenstand="heute")
        with self.assertRaises(TypeError):
            verbesserung.finde_technische_verbesserungen([], datenstand="heute")


class RotationUndZyklus(unittest.TestCase):
    def test_rotation_ist_deterministisch_und_wechselt_taeglich(self):
        traces = tuple("spur-%d" % i for i in range(7))
        a = _rotation(traces, datetime(2026, 10, 25, tzinfo=timezone.utc))
        self.assertEqual(a, _rotation(traces, datetime(2026, 10, 25, tzinfo=timezone.utc)))
        b = _rotation(traces, datetime(2026, 10, 26, tzinfo=timezone.utc))
        self.assertNotEqual(a[0], b[0])
        self.assertEqual(set(a), set(b))

    def test_registry_spuren_in_beiden_lanes_sichtbar_und_kandidaten_getrennt(self):
        bericht = fuehre_zyklus_aus(ROOT, datenstand=STAND)
        expected = set(strategie._registry(ROOT))
        self.assertEqual({x.spur for x in bericht.strategie}, expected)
        self.assertEqual({x.spur for x in bericht.verbesserung}, expected)
        self.assertEqual(bericht.strategiekandidaten, ())
        self.assertEqual(bericht.verbesserungskandidaten, ())
        self.assertTrue(all(x.status in {"geprueft", "datenarm", "nicht_auswertbar"}
                            for x in bericht.strategie + bericht.verbesserung))
        self.assertTrue(all(x.status != "geprueft" for x in bericht.verbesserung))

    def test_zyklus_verwendet_register_des_ziel_repositories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "Agenten" / "Handel"
            (base / "neue_spur").mkdir(parents=True)
            (base / "dauerlauf.py").write_text(
                'SPUREN = {"neue_spur": {"ordner": "neue_spur", "skript": "run.py"}}\n',
                encoding="utf-8")
            (base / "neue_spur" / "run.py").write_text("pass\n", encoding="utf-8")
            report = fuehre_zyklus_aus(root, datenstand=STAND)
            self.assertEqual([x.spur for x in report.strategie], ["neue_spur"])
            self.assertEqual([x.spur for x in report.verbesserung], ["neue_spur"])
            self.assertEqual(report.verbesserung[0].status, "nicht_auswertbar")

    def test_datenqualitaetsblockaden_kommen_vor_datenarmut(self):
        bericht = fuehre_zyklus_aus(ROOT, datenstand=STAND)
        if any(x.status == "nicht_auswertbar" for x in bericht.strategie):
            self.assertIn("nicht_auswertbar:", bericht.blockaden[0])

    def test_bericht_ist_unveraenderlich_und_revisionsbelegt(self):
        bericht = fuehre_zyklus_aus(ROOT, datenstand=STAND)
        with self.assertRaises(AttributeError):
            bericht.basisrevision = "fremd"
        if bericht.basisrevision:
            self.assertEqual(bericht.revisionen, (("basis", bericht.basisrevision),))


if __name__ == "__main__":
    unittest.main()
