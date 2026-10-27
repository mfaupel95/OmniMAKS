"""SkillsBot-Freitext: Ack, Endstatus und datensparsame Async-Logs."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import skillsbot as s


class FreitextStatusTest(unittest.TestCase):
    def _lauf(self, antwort=None, fehler=None):
        gesendet = []
        logs = []
        schleuse = s.FreitextSchleuse(42)
        schleuse._schlange = ["mach die Aufgabe"]
        def frage(chat, text):
            if fehler:
                raise fehler
            return antwort
        with patch.object(s, "_bots_frage", frage), \
                patch.object(s, "sende", lambda c, t: gesendet.append(t)), \
                patch.object(s, "_log", lambda *a, **k: logs.append((a, k))), \
                patch.object(s.time, "time", side_effect=[100.0, 104.5]):
            schleuse._arbeiter()
        self.assertEqual(len(logs), 1)
        args, kwargs = logs[0]
        self.assertEqual(args[:3], (42, "mach die Aufgabe", 4.5))
        return gesendet, args, kwargs

    def test_ok_loggt_nur_status_und_zeichen(self):
        with tempfile.TemporaryDirectory() as tmp:
            pfad = Path(tmp) / "skillsbot.log"
            with patch.object(s, "LOG_PFAD", str(pfad)), \
                    patch.object(s, "_bots_frage", return_value="Antwort mit geheimem Inhalt"), \
                    patch.object(s, "sende"):
                queue = s.FreitextSchleuse(42)
                queue._schlange = ["mach die Aufgabe"]
                queue._arbeiter()
            entry = json.loads(pfad.read_text(encoding="utf-8").strip())
        self.assertEqual(entry["status"], "ok")
        self.assertEqual(entry["zeichen"], len("Antwort mit geheimem Inhalt"))
        self.assertNotIn("geheim", json.dumps(entry))

    def test_empty_meldet_nicht_erledigt_ohne_retry(self):
        sent, args, _ = self._lauf("(leere Antwort)")
        self.assertIn("NICHT erledigt", sent[0])
        self.assertIn("nicht automatisch", sent[0])
        self.assertEqual(args[3:], ("paused", 0))

    def test_paused_banner_meldet_nicht_erledigt(self):
        sent, args, _ = self._lauf("conversation is paused: previous turn did not finish")
        self.assertIn("NICHT erledigt", sent[0])
        self.assertEqual(args[3:], ("paused", 0))

    def test_cli_fehler_ist_error(self):
        sent, args, _ = self._lauf(fehler=s.SkillsBotFehler("keine session_id"))
        self.assertIn("Freitext gescheitert", sent[0])
        self.assertEqual(args[3:], ("error", 0))

    def test_logaufruf_enthaelt_keine_antwort(self):
        _, args, kwargs = self._lauf("Antwort mit geheimem Inhalt")
        self.assertEqual(args[3:], ("ok", len("Antwort mit geheimem Inhalt")))
        self.assertEqual(kwargs, {})


if __name__ == "__main__":
    unittest.main()
