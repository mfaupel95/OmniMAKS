import sys
import unittest
from pathlib import Path
from unittest import mock

HANDEL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HANDEL))
import dauerlauf
import handelszentrale as hz


class HandelszentraleInventarTests(unittest.TestCase):
    def test_spurenzahl_kommt_dynamisch_aus_dauerlauf(self):
        self.assertEqual(len(hz.inventar_spuren()), len(dauerlauf.SPUREN))

    def test_spurpfad_und_unbekannter_modus_bleiben_sichtbar(self):
        rows = hz.inventar_spuren()
        self.assertTrue(all(Path(r.pfad).name == dauerlauf.SPUREN[r.name]["ordner"] for r in rows))
        self.assertTrue(all(r.modus == "Unbekannt" for r in rows))

    def test_worker_liefert_zeitstempel_und_quellfehler_ohne_fallback(self):
        class Queue:
            value = None
            def put(self, value): self.value = value
        q = Queue()
        with mock.patch.object(hz.Path, "home", return_value=Path("C:/user")), \
             mock.patch.object(hz.inventar, "sammle_downloads", return_value=[]), \
             mock.patch.object(hz.inventar, "sammle_projektstatus", return_value=[]), \
             mock.patch.object(hz.inventar_quellen, "sammle_runtime_snapshots", return_value=("[]", "[]", "[]")), \
             mock.patch.object(hz.inventar_quellen, "lade_betrieb", return_value=[
                 hz.inventar.InventarEintrag("runtime-fehler", "Docker", "", status="unbekannt",
                   quelle="Docker-Snapshot", hinweise=("Snapshot fehlt",))]):
            app = object.__new__(hz.Handelszentrale)
            app._inventar_worker(q)
        timestamp, rows, error = q.value
        self.assertTrue(timestamp.isoformat())
        self.assertFalse(error)
        runtime = [r for r in rows if r.typ == "runtime-fehler"]
        self.assertEqual(runtime[0].status, "unbekannt")
        self.assertEqual(runtime[0].hinweise, ("Snapshot fehlt",))
        self.assertTrue(all(r.aktualisiert for r in rows))


if __name__ == "__main__":
    unittest.main()
