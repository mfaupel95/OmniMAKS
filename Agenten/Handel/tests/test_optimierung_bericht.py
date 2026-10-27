"""Vertraege fuer deterministische, sichere Optimierungsberichte."""
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

HANDEL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HANDEL))
from optimierung.bericht import render_bericht, schreibe_bericht
from optimierung.ergebnis import Kandidat, Messfenster
from optimierung.papierlauf import RegistrierungsBericht
from optimierung.zyklus import SpurBefund, ZyklusBericht

STAND = datetime(2026, 10, 26, 9, 45, tzinfo=timezone.utc)


def fenster(start, ende, netto=1.25, dd=2.5, runden=20):
    return Messfenster(datetime.fromisoformat(start), datetime.fromisoformat(ende),
                       netto, dd, runden, runden, True, True, True)


def kandidat():
    return Kandidat("k-17", "strategie-a", "abc123def456", fenster("2026-09-01T00:00:00+00:00", "2026-09-10T00:00:00+00:00"),
                     fenster("2026-09-11T00:00:00+00:00", "2026-09-20T00:00:00+00:00", .75, 3.0, 10),
                     fenster("2026-09-21T00:00:00+00:00", "2026-09-30T00:00:00+00:00", .25, 2.0, 8),
                     True, True)


def zyklus(*, befund=None, kandidaten=(), blockaden=()):
    return ZyklusBericht(STAND, "0123456789abcdef", (befund or SpurBefund("spur-a", "nicht_auswertbar", "Journal ohne Kostenbeleg"),),
                         (SpurBefund("spur-a", "datenarm", "Vorher-Nachher-Messung fehlt"),),
                         tuple(kandidaten), (), tuple(blockaden), (("basis", "0123456789abcdef"),))


class Bericht(unittest.TestCase):
    def test_normaler_bericht_zeigt_getrennte_lanes_basis_und_messfenster(self):
        text = render_bericht(zyklus(kandidaten=(kandidat(),)))
        self.assertIn("# Optimierungslauf", text)
        self.assertIn("Basisrevision: `0123456789abcdef`", text)
        self.assertIn("Strategie-Kandidaten: 1", text)
        self.assertIn("Netto: 0.75 %", text)
        self.assertIn("Out-of-Sample", text)
        self.assertIn("Gebühren: vollständig", text)
        self.assertIn("Funding: vollständig", text)
        self.assertIn("Slippage: vollständig", text)
        self.assertIn("Aktiviert: nein", text)

    def test_zyklus_ohne_kandidaten_wird_als_bestandsaufnahme_gekennzeichnet(self):
        text = render_bericht(zyklus())
        self.assertIn("Status: BESTANDSAUFNAHME", text)
        self.assertIn("keine gemessenen Kandidaten", text)
        self.assertIn("Journal ohne Kostenbeleg", text)

    def test_datenluecken_und_blockaden_bleiben_sichtbar(self):
        text = render_bericht(zyklus(blockaden=("strategie:datenarm:spur-a:kein Adapter",)))
        self.assertIn("Datenlücken und Blockaden", text)
        self.assertIn("strategie:datenarm:spur-a:kein Adapter", text)
        self.assertIn("nicht_auswertbar", text)

    def test_toolfehler_ergibt_keinen_erfolgsbericht_und_zeigt_keinen_exception_text(self):
        text = render_bericht(None, fehler=RuntimeError("token=topsecret --live /home/private"))
        self.assertIn("Status: FEHLER", text)
        self.assertIn("RuntimeError", text)
        self.assertNotIn("topsecret", text)
        self.assertNotIn("--live", text)
        self.assertNotIn("/home/private", text)

    def test_sicherheitsblockade_und_registrierung_behaupten_keine_aktivierung(self):
        registration = RegistrierungsBericht(True, False, "registriert_nicht_aktiviert", "deadbeef")
        text = render_bericht(zyklus(kandidaten=(kandidat(),)), registrierung=registration,
                              sicherheitsblockade="papierisolation_nicht_belegt")
        self.assertIn("Status: SICHERHEITSGESPERRT", text)
        self.assertIn("Papierisolation nicht belegt", text)
        self.assertIn("Registriert: ja", text)
        self.assertIn("Aktiviert: nein", text)

    def test_deterministisch_und_sensible_details_werden_nicht_ausgegeben(self):
        malicious = SpurBefund("spur-a", "datenarm", "Pfad C:/Users/Max/.env passwort=geheim")
        report = zyklus(befund=malicious)
        first = render_bericht(report)
        self.assertEqual(first, render_bericht(report))
        self.assertNotIn("C:/Users", first)
        self.assertNotIn("geheim", first)

    def test_atomic_write_erfordert_ausdrueckliches_ziel_im_worktree(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            dest = root / "reports" / "lauf.md"
            dest.parent.mkdir()
            written = schreibe_bericht(zyklus(), ziel=dest, worktree=root)
            self.assertEqual(written, dest)
            self.assertEqual(dest.read_text(encoding="utf-8"), render_bericht(zyklus()))
            with self.assertRaises(ValueError):
                schreibe_bericht(zyklus(), ziel=Path(outside) / "lauf.md", worktree=root)
            with self.assertRaises(ValueError):
                schreibe_bericht(zyklus(), ziel=root / "reports", worktree=root)

    def test_vorhandener_bericht_wird_nie_ueberschrieben(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dest = root / "lauf.md"
            dest.write_text("vorheriger Bericht\n", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                schreibe_bericht(zyklus(), ziel=dest, worktree=root)
            self.assertEqual(dest.read_text(encoding="utf-8"), "vorheriger Bericht\n")

    def test_symlinkziel_wird_vor_atomic_replace_abgewiesen(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target.md"
            target.write_text("keep", encoding="utf-8")
            link = root / "report.md"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks in dieser Umgebung nicht verfügbar")
            with self.assertRaises(FileExistsError):
                schreibe_bericht(zyklus(), ziel=link, worktree=root)
            self.assertEqual(target.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
