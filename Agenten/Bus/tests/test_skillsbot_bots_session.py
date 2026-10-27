"""Freitext im SkillsBot -> persistierte bots-Profil-CLI-Sitzung (Mehrturn).

HINTERGRUND: Freitext ging bisher per A2A an den HAUPTAGENTEN (hermes-maks-pc)
und war bewusst KONTEXTLOS (jede Nachricht ein frischer A2A-"SendMessage",
der Kontext lief nur ueber die Gateway-session_id). Ausgabe: stille
Kontextlosigkeit - Max konnte keine Folgefragen stellen, jede Nachricht begann
von vorn. Der SkillsBot nutzt schon langer hermes-CLI-Subprozesse (_bot_fragen
fuer /bot NAME); CLI-Help belegt `hermes ... chat -q TEXT -Q` und
`--resume SESSION_ID`. Deshalb geht Freitext jetzt ausschliesslich durch die
bots-Profil-CLI-Sitzung, die Mehrturn haelt:
  - erste Nachricht : `hermes -p bots chat -q TEXT -Q`
  - Folge-Nachricht : `hermes -p bots chat --resume ID -q TEXT -Q`
  - die bots-session_id wird je Chat in einer eigenen Laufzeit-State-Datei
    gesichert (BOTS_SESSION_PFAD),
  - genau EIN bots-Prozess je Chat; weitere Freitext-Nachrichten warten FIFO
    in der Chat-Warteschlange (kein zweiter Prozess parallel),
  - ist der CLI-Output nicht parsebar (keine session_id), wird der Fehler
    transparent gemeldet und der gesicherte Stand NICHT angefasst.

A2A-default bleibt fuer die anderen Funktionen (Schraegstrich-Befehle, /run)
unveraendert. /bot NAME, /bots, NAME:-Direktadressierung bleiben unveraendert.

Alle hermes-Subprozesse sind hier gemockt (subprocess.Popen); es wird nie ein
echtes hermes.exe gestartet.
"""

from __future__ import annotations

import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

BUS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUS))
import skillsbot as s                                          # noqa: E402

CHAT = 12345
ERSTE_ANTWORT = "session_id: sid-erste\nHallo, ich bin der bots-Agent.\n"


def _popen_fake(stdout, code=0, sperre=None):
    """Attrappen-hermes.exe: liefert stdout, faengt die argv ab, zaehlt aktiv.

    `sperre`: eine threading.Event-Klasse, auf der communicate() wartet - um
    einen noch laufenden Prozess zu simulieren.
    """
    ziel = {"aufrufe": [], "aktiv": 0, "max_aktiv": 0}

    def fake(argv, **kw):
        ziel["aufrufe"].append(list(argv))
        ziel["aktiv"] += 1
        ziel["max_aktiv"] = max(ziel["max_aktiv"], ziel["aktiv"])

        class R:
            returncode = code

            def communicate(self, timeout=None):
                try:
                    if sperre is not None:
                        sperre.wait(timeout)
                    return stdout, ""
                finally:
                    ziel["aktiv"] -= 1

            def kill(self):
                pass

        return R()

    return patch.object(s.subprocess, "Popen", side_effect=fake), ziel


class _Basis(unittest.TestCase):
    """Setzt die temporaere State-Fixture auf und haelt sie bis Testende.

    hermes.exe existiert im frischen Worktree nicht (gitignored); der
    isfile-Schutz in _bots_frage/_bot_fragen braucht aber eine Datei, damit
    der Popen-Mock greift. Es wird nie ein echtes hermes gestartet.
    """

    def fixture(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        state = patch.object(s, "BOTS_SESSION_PFAD",
                             str(Path(d.name) / "bots-session.json"))
        exe = patch.object(s, "HERMES_EXE", str(Path(d.name) / "hermes.exe"))
        state.start()
        exe.start()
        self.addCleanup(state.stop)
        self.addCleanup(exe.stop)
        # damit der isfile-Schutz sieht, dass hermes.exe "existiert"
        Path(d.name, "hermes.exe").touch()


class Zerlegen(unittest.TestCase):
    """stdout in Antworttext + session_id zerlegen (EIN Fundort)."""

    def test_liest_session_id_und_entfernt_die_zeile(self):
        antwort, sid = s._bots_ausgabe_zerlegen("session_id: abc\nPONG\n")
        self.assertEqual(antwort, "PONG")
        self.assertEqual(sid, "abc")

    def test_letzte_session_id_gewinnt(self):
        _, sid = s._bots_ausgabe_zerlegen(
            "session_id: alt\nsession_id: neu\nText\n")
        self.assertEqual(sid, "neu")

    def test_ohne_session_id_ist_ein_fehler(self):
        """Kein Lauf ohne Resume-Moeglichkeit stillschweigend verkaufen."""
        with self.assertRaises(s.SkillsBotFehler) as k:
            s._bots_ausgabe_zerlegen("es gibt keine session id\n")
        self.assertIn("session_id", str(k.exception))


class ErsterAufruf(_Basis):
    """Freitext-Route: genau EIN -p-bots-Aufruf statt A2A-Hauptagent."""

    def test_erste_nachricht_ruft_das_bots_profil_ohne_resume(self):
        self.fixture()
        mock, ziel = _popen_fake(ERSTE_ANTWORT)
        with mock:
            antwort = s._bots_frage(CHAT, "mach irgendwas")
        self.assertEqual(
            ziel["aufrufe"],
            [[s.HERMES_EXE, "-p", "bots", "chat", "-q", "mach irgendwas", "-Q"]],
            "genau ein -p-bots-Aufruf, kein --resume beim ersten Mal")
        self.assertIn("Hallo, ich bin der bots-Agent.", antwort)
        # die Antwort-session_id ist je Chat gespeichert (Mehrturn-Grundlage)
        self.assertEqual(s._bots_session_lesen(CHAT), "sid-erste")

    def test_es_ist_nur_eine_bots_cli_und_kein_a2a_frage(self):
        """Freitext DARF den A2A-Hauptagenten (frage) nicht mehr ansprechen."""
        self.fixture()
        mock, ziel = _popen_fake(ERSTE_ANTWORT)

        def kaputt(*a, **k):
            raise AssertionError("Freitext darf nicht mehr per A2A frage laufen")

        with mock, patch.object(s, "frage", kaputt):
            s._bots_frage(CHAT, "was ist los?")
        self.assertEqual(len(ziel["aufrufe"]), 1)


class Folgeauftrag(_Basis):
    """Folge-Nachrichten reichen die gesicherte session_id als --resume weiter."""

    def test_folgeauftrag_nutzt_resume_id(self):
        self.fixture()
        # erste Nachricht liefert sid-erste und speichert sie
        with _popen_fake(ERSTE_ANTWORT)[0]:
            s._bots_frage(CHAT, "anfang")
        self.assertEqual(s._bots_session_lesen(CHAT), "sid-erste")
        # zweite Nachricht: --resume sid-erste
        mock2, ziel = _popen_fake("session_id: sid-zweite\nweiter\n")
        with mock2:
            antwort = s._bots_frage(CHAT, "und jetzt?")
        argv = ziel["aufrufe"][0]
        self.assertIn("--resume", argv)
        self.assertEqual(argv[argv.index("--resume") + 1], "sid-erste")
        self.assertEqual(antwort, "weiter")
        # die NEUE id aus der Antwort ist gespeichert (Verlauf wandert mit)
        self.assertEqual(s._bots_session_lesen(CHAT), "sid-zweite")

    def test_zwei_chats_haben_getrennte_sitzungen(self):
        self.fixture()
        mock1, z1 = _popen_fake("session_id: sid-a\nA\n")
        with mock1:
            s._bots_frage(CHAT, "a")
        mock2, z2 = _popen_fake("session_id: sid-b\nB\n")
        with mock2:
            s._bots_frage(CHAT + 1, "b")
        self.assertEqual(s._bots_session_lesen(CHAT), "sid-a")
        self.assertEqual(s._bots_session_lesen(CHAT + 1), "sid-b")


class StateSchutz(_Basis):
    """Keine stille Kontextlosigkeit: unparsebarer Output laesst Stand stehen."""

    def test_unparsebarer_output_meldet_fehler_und_laeuft_nicht_ohne_kontext(self):
        self.fixture()
        with _popen_fake(ERSTE_ANTWORT)[0]:
            s._bots_frage(CHAT, "anfang")
        vorher = s._bots_session_lesen(CHAT)
        with _popen_fake("nur text ohne session_id\n")[0]:
            with self.assertRaises(s.SkillsBotFehler):
                s._bots_frage(CHAT, "naechste")
        # der gesicherte Stand ist NICHT ueberschrieben - er ist nicht kaputt
        self.assertEqual(s._bots_session_lesen(CHAT), vorher)


class EinProzessProChat(_Basis):
    """FIFO: genau EIN bots-Prozess je Chat, weitere Nachrichten warten."""

    def test_zweite_nachricht_wartet_und_laeuft_nie_parallel(self):
        self.fixture()
        sperre = threading.Event()   # steuert, wann der laufende Prozess fertig ist
        mock, ziel = _popen_fake("session_id: sid-1\nok1\n", sperre=sperre)
        with mock, patch.object(s, "sende", lambda c, t: None):
            schleuse = s.FreitextSchleuse(CHAT)
            schleuse.stosse_an("erste")
            # warten bis der erste Prozess laeuft (blockiert auf dem Event)
            ende = time.time() + 5
            while not ziel["aufrufe"] and time.time() < ende:
                time.sleep(0.01)
            self.assertEqual(len(ziel["aufrufe"]), 1)
            # zweite Nachricht, waehrend der erste noch blockiert ist: KEIN
            # zweiter Prozess jetzt - sie wartet in der Chat-Warteschlange.
            schleuse.stosse_an("zweite")
            time.sleep(0.1)
            self.assertEqual(len(ziel["aufrufe"]), 1, "kein zweiter Prozess parallel")
            # erster Prozess darf fertig werden -> zweiter laeuft danach
            sperre.set()
            ende = time.time() + 5
            while len(ziel["aufrufe"]) < 2 and time.time() < ende:
                time.sleep(0.01)
        self.assertEqual(len(ziel["aufrufe"]), 2)
        # NIE zwei bots-Prozesse gleichzeitig am gleichen Chat
        self.assertEqual(ziel["max_aktiv"], 1)
        # die erste Nachricht kennt keine session; die zweite RESUMT sie
        self.assertNotIn("--resume", ziel["aufrufe"][0])
        self.assertEqual(ziel["aufrufe"][1][ziel["aufrufe"][1].index("--resume") + 1],
                         "sid-1")
        self.assertEqual(ziel["aufrufe"][1][0], s.HERMES_EXE)

    def test_warteschlange_ist_chronologisch(self):
        self.fixture()
        reihenfolge = []
        aktiv = {"wert": 0, "max": 0}
        sperre = threading.Lock()

        def frage(chat, text):
            with sperre:
                aktiv["wert"] += 1
                aktiv["max"] = max(aktiv["max"], aktiv["wert"])
            time.sleep(0.05)
            reihenfolge.append(text)
            with sperre:
                aktiv["wert"] -= 1
            return "ok:" + text

        with patch.object(s, "_bots_frage", frage), \
                patch.object(s, "sende", lambda c, t: None):
            schleuse = s.FreitextSchleuse(CHAT)
            schleuse.stosse_an("eins")
            schleuse.stosse_an("zwei")
            schleuse.stosse_an("drei")
            ende = time.time() + 5
            while len(reihenfolge) < 3 and time.time() < ende:
                time.sleep(0.01)
        self.assertEqual(reihenfolge, ["eins", "zwei", "drei"])
        self.assertEqual(aktiv["max"], 1)


class Bearbeite(_Basis):
    """bearbeite leitet Freitext weiterhin asynchron und mit Vorwarnung."""

    def test_freitext_startet_die_perchat_schleuse_statt_a2a(self):
        self.fixture()
        events = []
        with patch.object(s, "sende", lambda c, t: events.append(("send", t))), \
                patch.object(s, "_freitext_stosse_chat_an",
                             lambda chat, text: events.append(("queue", chat, text))):
            antwort, _ = s.bearbeite("erledige das", CHAT)
        self.assertIsNone(antwort)
        self.assertEqual(events[0][0], "send")
        self.assertEqual(events[0][1].count("Angenommen"), 1)
        self.assertEqual(events[1], ("queue", CHAT, "erledige das"))


if __name__ == "__main__":
    unittest.main()