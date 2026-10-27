"""Isolation und Promotion benötigen ausdrückliche, überprüfbare Belege."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from dataclasses import replace

HANDEL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HANDEL))
from optimierung.ergebnis import GateErgebnis
from optimierung.papierlauf import (pruefe_papierisolation, registriere_papier_kandidat,
                                    schreibe_rollback_vermerk)
from optimierung.worktree import lege_experiment_an


def git(path, *args):
    return subprocess.run(["git", "-C", str(path), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


class PapierIsolation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "--quiet", str(self.repo)], check=True)
        git(self.repo, "config", "user.name", "Unit Test")
        git(self.repo, "config", "user.email", "unit@example.invalid")
        (self.repo / "code.py").write_text("pass\n", encoding="utf-8")
        git(self.repo, "add", "code.py")
        git(self.repo, "commit", "--quiet", "-m", "base")
        self.exp = lege_experiment_an(self.repo, kennung="paper-test", basis=git(self.repo, "rev-parse", "HEAD"))
        self.target = Path(self.tmp.name) / "paper-slot"
        self.target.mkdir()
        (self.exp.pfad / "runner.py").write_text("# isolated paper runner\n", encoding="utf-8")
        (self.target / "runner.py").write_text("# dedicated paper runner\n", encoding="utf-8")
        self.exp_state = self.exp.pfad / ".papierlauf-daten" / "state.json"
        self.exp_journal = self.exp.pfad / ".papierlauf-daten" / "journal.csv"
        self.target_state = self.target / "state" / "state.json"
        self.target_journal = self.target / "journal" / "journal.csv"
        self.cmd = (f"python {self.exp.pfad / 'runner.py'} --papier --state-path {self.exp_state} "
                    f"--journal-path {self.exp_journal}")
        self.target_cmd = (f"python {self.target / 'runner.py'} --papier --state-path {self.target_state} "
                           f"--journal-path {self.target_journal}")
        self.process = {"pid": 321, "command_line": self.cmd}

    def process_command(self, pid):
        return {321: self.cmd, 322: self.target_cmd}.get(pid)

    def isolation_manifest(self, **overrides):
        data = {"schema": 1, "modus": "papier", "live_modus": False,
                "orders_enabled": False, "code_root": str(self.exp.pfad),
                "state_path": str(self.exp_state), "journal_path": str(self.exp_journal),
                "entrypoint": str(self.exp.pfad / "runner.py"),
                "process": self.process}
        data.update(overrides)
        (self.exp.pfad / ".papierlauf-isolation.json").write_text(
            json.dumps(data), encoding="utf-8")

    def target_marker(self, **overrides):
        data = {"schema": 1, "typ": "dedicated-paper-only", "live_enabled": False,
                "root": str(self.target), "state_path": str(self.target_state),
                "journal_path": str(self.target_journal),
                "entrypoint": str(self.target / "runner.py")}
        data.update(overrides)
        self.target_cmd = (f"python {self.target / 'runner.py'} --papier --state-path {data['state_path']} "
                           f"--journal-path {data['journal_path']}")
        data["process"] = {"pid": 322, "command_line": self.target_cmd}
        (self.target / ".paper-only.json").write_text(json.dumps(data), encoding="utf-8")

    def test_no_manifest_fails_closed(self):
        result = pruefe_papierisolation(self.exp)
        self.assertFalse(result.promotion_erlaubt)
        self.assertIn("papier_isolationsbeleg_fehlt_oder_ungueltig", result.gruende)

    def test_same_state_and_journal_path_block(self):
        same = str(self.exp.pfad / ".papierlauf-daten" / "shared.json")
        self.isolation_manifest(state_path=same, journal_path=same)
        with patch("optimierung.papierlauf._prozess_befehl", side_effect=self.process_command):
            result = pruefe_papierisolation(self.exp)
        self.assertFalse(result.promotion_erlaubt)
        self.assertIn("papier_zustand_oder_journal_nicht_getrennt", result.gruende)

    def test_process_command_line_must_prove_paper_and_code_root(self):
        self.isolation_manifest()
        with patch("optimierung.papierlauf._prozess_befehl",
                   return_value=f"python {self.exp.pfad / 'runner.py'} --not-papier --state-path {self.exp_state} --journal-path {self.exp_journal}"):
            result = pruefe_papierisolation(self.exp)
        self.assertFalse(result.promotion_erlaubt)
        self.assertIn("papier_prozessidentitaet_oder_modus_nicht_belegt", result.gruende)


class KandidatenRegistrierung(unittest.TestCase):
    def setUp(self):
        self.iso = PapierIsolation()
        self.iso.setUp()
        self.addCleanup(self.iso.doCleanups)

    def test_gate_nein_and_unmarked_target_do_not_write(self):
        before = list(self.iso.target.iterdir())
        result = registriere_papier_kandidat(self.iso.exp,
                                             gate=GateErgebnis(False, ("holdout_fail",)),
                                             ziel=self.iso.target)
        self.assertFalse(result.registriert)
        self.assertFalse(result.aktiviert)
        self.assertEqual(list(self.iso.target.iterdir()), before)

    def test_missing_isolation_or_target_proof_blocks_without_mutation(self):
        before = list(self.iso.target.iterdir())
        result = registriere_papier_kandidat(self.iso.exp, gate=GateErgebnis(True, ()), ziel=self.iso.target)
        self.assertFalse(result.registriert)
        self.assertFalse(result.aktiviert)
        self.assertEqual(list(self.iso.target.iterdir()), before)

    def test_registration_is_append_only_idempotent_and_never_activates(self):
        self.iso.isolation_manifest()
        self.iso.target_marker()
        with patch("optimierung.papierlauf._prozess_befehl", side_effect=self.iso.process_command):
            first = registriere_papier_kandidat(self.iso.exp, gate=GateErgebnis(True, ()), ziel=self.iso.target)
            second = registriere_papier_kandidat(self.iso.exp, gate=GateErgebnis(True, ()), ziel=self.iso.target)
            rollback = schreibe_rollback_vermerk(self.iso.target, registrierung=first)
        self.assertTrue(first.registriert)
        self.assertFalse(first.aktiviert)
        self.assertEqual(first.grund, "registriert_nicht_aktiviert")
        payload = json.loads(first.beleg.read_text(encoding="utf-8"))
        self.assertFalse(payload["aktiviert"])
        self.assertEqual(payload["typ"], "candidate-registration")
        self.assertFalse((self.iso.target / "active-revision.json").exists())
        self.assertFalse(self.iso.target_state.exists())
        self.assertFalse(self.iso.target_journal.exists())
        self.assertTrue(second.idempotent)
        self.assertFalse(second.aktiviert)
        self.assertTrue(rollback.registriert)
        self.assertFalse(rollback.aktiviert)
        self.assertTrue(first.beleg.is_file(), "Ablehnungsvermerk löscht keinen Beleg")

    def test_forged_experiment_identifier_cannot_escape_registration_directory(self):
        self.iso.isolation_manifest()
        self.iso.target_marker()
        forged = replace(self.iso.exp, kennung="../../escape", branch="optimierung/../../escape")
        with patch("optimierung.papierlauf._prozess_befehl", side_effect=self.iso.process_command):
            result = registriere_papier_kandidat(forged, gate=GateErgebnis(True, ()), ziel=self.iso.target)
        self.assertFalse(result.registriert)
        self.assertFalse((self.iso.target.parent / "escape").exists())

    def test_external_state_path_in_marker_blocks(self):
        outside = str(self.iso.target.parent / "outside.json")
        self.iso.target_marker(state_path=outside)
        self.iso.isolation_manifest()
        with patch("optimierung.papierlauf._prozess_befehl", side_effect=self.iso.process_command):
            result = registriere_papier_kandidat(self.iso.exp, gate=GateErgebnis(True, ()), ziel=self.iso.target)
        self.assertFalse(result.registriert)
        self.assertEqual(result.grund, "papierzielpfade_nicht_getrennt")

    def test_registration_directory_cannot_overlap_state_or_journal(self):
        self.iso.isolation_manifest()
        self.iso.target_marker(state_path=str(self.iso.target / "candidate-registrations" / "state.json"))
        with patch("optimierung.papierlauf._prozess_befehl", side_effect=self.iso.process_command):
            result = registriere_papier_kandidat(self.iso.exp, gate=GateErgebnis(True, ()), ziel=self.iso.target)
        self.assertFalse(result.registriert)
        self.assertEqual(result.grund, "registrierungsordner_ueberlappt_mit_papierdaten")

    def test_duplicate_manifest_keys_are_rejected(self):
        self.iso.isolation_manifest()
        (self.iso.target / ".paper-only.json").write_text(
            '{"schema":1,"schema":1,"typ":"dedicated-paper-only"}', encoding="utf-8")
        with patch("optimierung.papierlauf._prozess_befehl", side_effect=self.iso.process_command):
            result = registriere_papier_kandidat(self.iso.exp, gate=GateErgebnis(True, ()), ziel=self.iso.target)
        self.assertFalse(result.registriert)
        self.assertEqual(result.grund, "dediziertes_papierziel_nicht_belegt")

    def test_registration_directory_symlink_is_rejected(self):
        self.iso.isolation_manifest()
        self.iso.target_marker()
        outside = self.iso.target.parent / "outside"
        outside.mkdir()
        link = self.iso.target / "candidate-registrations"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Verzeichnis-Symlinks auf diesem Windows-System nicht verfügbar")
        with patch("optimierung.papierlauf._prozess_befehl", side_effect=self.iso.process_command):
            result = registriere_papier_kandidat(self.iso.exp, gate=GateErgebnis(True, ()), ziel=self.iso.target)
        self.assertFalse(result.registriert)
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
