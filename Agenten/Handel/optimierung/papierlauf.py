"""Fail-closed Vorbereitung eines Papierkandidaten ohne Laufzeitaktivierung.

Das Modul startet keine Prozesse, kopiert keinen Code und schaltet keine
Revision im Papierlauf frei. Es kann nach bestandenen Gates lediglich einen
append-only Registrierungseintrag ablegen. Aktivierung bleibt ausdrücklich
offen, bis ein Papierlauf-Consumer diese Auswahl nachweislich übernimmt.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
from dataclasses import dataclass
from typing import Any

from .ergebnis import GateErgebnis
from .worktree import Experiment


@dataclass(frozen=True)
class RegistrierungsBericht:
    registriert: bool
    aktiviert: bool
    grund: str
    revision: str | None = None
    beleg: Path | None = None
    idempotent: bool = False


def _gesperrt(*gruende: str) -> GateErgebnis:
    return GateErgebnis(False, tuple(gruende))


def _json(pfad: Path) -> dict[str, Any] | None:
    if pfad.is_symlink():
        return None
    try:
        wert = json.loads(pfad.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        return None
    return wert if isinstance(wert, dict) else None


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _innerhalb(pfad: Path, wurzel: Path) -> bool:
    try:
        pfad.resolve(strict=False).relative_to(wurzel.resolve(strict=False))
        return True
    except (OSError, ValueError):
        return False


def _ueberlappt(a: Path, b: Path) -> bool:
    return _innerhalb(a, b) or _innerhalb(b, a)


def _prozess_befehl(pid: int) -> str | None:
    """Read actual process command line; unsupported platforms fail closed."""
    if os.name == "nt":
        script = ("$p=Get-CimInstance Win32_Process -Filter 'ProcessId = " + str(pid) +
                  "'; if ($p) { $p.CommandLine }")
        try:
            r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                               capture_output=True, text=True, timeout=5, check=False)
        except (OSError, subprocess.SubprocessError):
            return None
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
    proc = Path(f"/proc/{pid}/cmdline")
    try:
        return proc.read_bytes().replace(b"\0", b" ").decode("utf-8", "strict").strip()
    except (OSError, UnicodeError):
        return None


def _papier_befehl(command: str | None, *, wurzel: Path, entrypoint: Path,
                   state: Path, journal: Path) -> bool:
    if not command:
        return False
    try:
        entrypoint = entrypoint.resolve(strict=True)
        if not _innerhalb(entrypoint, wurzel) or not entrypoint.is_file():
            return False
    except (OSError, RuntimeError, TypeError, ValueError):
        return False
    lower = command.casefold()
    return bool(str(entrypoint).casefold() in lower
                and re.search(r"(?<![\w-])--state-path(?![\w-])", lower)
                and str(state).casefold() in lower
                and re.search(r"(?<![\w-])--journal-path(?![\w-])", lower)
                and str(journal).casefold() in lower
                and re.search(r"(?<![\w-])--papier(?![\w-])", command, re.IGNORECASE)
                and not re.search(r"(?<![\w-])--live(?![\w-])", command, re.IGNORECASE))


def pruefe_papierisolation(experiment: Experiment) -> GateErgebnis:
    """Prüft Codewurzel, getrennte Schreibpfade und einen echten Papierprozess."""
    if not isinstance(experiment, Experiment):
        return _gesperrt("experiment_ungueltig")
    try:
        root = experiment.pfad.resolve(strict=True)
        repo = experiment.repo.resolve(strict=True)
        if root == repo or _innerhalb(root, repo) or _innerhalb(repo, root):
            return _gesperrt("codewurzel_nicht_isoliert")
        git_root = Path(subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10, check=True).stdout.strip()).resolve()
        branch = subprocess.run(["git", "-C", str(root), "branch", "--show-current"],
                                capture_output=True, text=True, timeout=10,
                                check=True).stdout.strip()
    except (AttributeError, OSError, RuntimeError, subprocess.SubprocessError, ValueError):
        return _gesperrt("experiment_worktree_nicht_verifizierbar")
    if git_root != root or branch != experiment.branch:
        return _gesperrt("experiment_codewurzel_oder_branch_abweichend")

    manifest = _json(root / ".papierlauf-isolation.json")
    if (not manifest or type(manifest.get("schema")) is not int
            or manifest.get("schema") != 1 or manifest.get("modus") != "papier"):
        return _gesperrt("papier_isolationsbeleg_fehlt_oder_ungueltig")
    if manifest.get("live_modus") is not False or manifest.get("orders_enabled") is not False:
        return _gesperrt("papiermodus_nicht_exklusiv_belegt")
    try:
        raw_code_root, raw_state, raw_journal, entrypoint = (Path(manifest[name])
                                                 for name in ("code_root", "state_path", "journal_path", "entrypoint"))
        if not all(path.is_absolute() for path in (raw_code_root, raw_state, raw_journal, entrypoint)):
            raise ValueError("absolute paths required")
        code_root = raw_code_root.resolve(strict=True)
        state = raw_state.resolve(strict=False)
        journal = raw_journal.resolve(strict=False)
    except (KeyError, OSError, TypeError, ValueError):
        return _gesperrt("papierpfade_fehlen_oder_ungueltig")
    if code_root != root:
        return _gesperrt("papier_codewurzel_weicht_ab")
    data_root = root / ".papierlauf-daten"
    if (not _innerhalb(state, data_root) or not _innerhalb(journal, data_root)
            or state == journal or state.exists() and state.is_dir()
            or journal.exists() and journal.is_dir()):
        return _gesperrt("papier_zustand_oder_journal_nicht_getrennt")
    process = manifest.get("process")
    if not isinstance(process, dict) or type(process.get("pid")) is not int or process["pid"] <= 0:
        return _gesperrt("papier_prozesskennung_fehlt")
    command = _prozess_befehl(process["pid"])
    if (process.get("command_line") != command
            or not _papier_befehl(command, wurzel=root, entrypoint=entrypoint,
                                  state=state, journal=journal)):
        return _gesperrt("papier_prozessidentitaet_oder_modus_nicht_belegt")
    return GateErgebnis(True, ())


def _zielbeleg(ziel: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        root = ziel.resolve(strict=True)
    except (OSError, RuntimeError):
        return None, "papierziel_existiert_nicht_oder_ist_ungueltig"
    if not root.is_dir():
        return None, "papierziel_ist_kein_ordner"
    marker = _json(root / ".paper-only.json")
    if (not marker or type(marker.get("schema")) is not int or marker.get("schema") != 1
            or marker.get("typ") != "dedicated-paper-only"
            or marker.get("live_enabled") is not False):
        return None, "dediziertes_papierziel_nicht_belegt"
    try:
        raw_root = Path(marker["root"])
        raw_state, raw_journal, entrypoint = (Path(marker[name])
                                              for name in ("state_path", "journal_path", "entrypoint"))
        if not all(path.is_absolute() for path in (raw_root, raw_state, raw_journal, entrypoint)):
            return None, "papierzielpfade_muessen_absolut_sein"
        if raw_root.resolve(strict=True) != root:
            return None, "papierzielwurzel_weicht_ab"
        state = raw_state.resolve(strict=False)
        journal = raw_journal.resolve(strict=False)
    except (KeyError, OSError, RuntimeError, TypeError, ValueError):
        return None, "papierzielpfade_fehlen_oder_ungueltig"
    if (not _innerhalb(state, root) or not _innerhalb(journal, root)
            or state == journal or state == root or journal == root):
        return None, "papierzielpfade_nicht_getrennt"
    process = marker.get("process")
    if not isinstance(process, dict) or type(process.get("pid")) is not int or process["pid"] <= 0:
        return None, "papierziel_prozesskennung_fehlt"
    command = _prozess_befehl(process["pid"])
    if (process.get("command_line") != command
            or not _papier_befehl(command, wurzel=root, entrypoint=entrypoint,
                                  state=state, journal=journal)):
        return None, "papierziel_prozessidentitaet_nicht_belegt"
    return marker, None


def registriere_papier_kandidat(experiment: Experiment, *, gate: GateErgebnis,
                                ziel: Path) -> RegistrierungsBericht:
    """Registriert einen geprüften Kandidaten; die Papierlaufrevision bleibt unverändert."""
    if not isinstance(gate, GateErgebnis) or gate.promotion_erlaubt is not True:
        return RegistrierungsBericht(False, False, "kandidat_gate_nicht_bestanden")
    if (not isinstance(experiment, Experiment)
            or not isinstance(getattr(experiment, "kennung", None), str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", experiment.kennung)
            or experiment.branch != f"optimierung/{experiment.kennung}"):
        return RegistrierungsBericht(False, False, "experiment_kennung_oder_branch_ungueltig")
    isolation = pruefe_papierisolation(experiment)
    if not isolation.promotion_erlaubt:
        return RegistrierungsBericht(False, False, "experiment_isolation_nicht_belegt: " + ",".join(isolation.gruende))
    marker, reason = _zielbeleg(Path(ziel))
    if reason:
        return RegistrierungsBericht(False, False, reason)
    target = Path(ziel).resolve(strict=True)
    if (_innerhalb(target, experiment.repo) or _innerhalb(experiment.repo, target)
            or _innerhalb(target, experiment.pfad) or _innerhalb(experiment.pfad, target)):
        return RegistrierungsBericht(False, False, "papierziel_ueberlappt_mit_experiment_oder_quellrepo")
    commit = experiment.pfad
    try:
        revision = subprocess.run(["git", "-C", str(commit), "rev-parse", "HEAD"],
                                  capture_output=True, text=True, timeout=10,
                                  check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return RegistrierungsBericht(False, False, "experiment_revision_nicht_verifizierbar")
    if not re.fullmatch(r"[0-9a-fA-F]{40,64}", revision):
        return RegistrierungsBericht(False, False, "experiment_revision_ungueltig")
    registration_dir = target / "candidate-registrations"
    if not registration_dir.exists():
        try:
            registration_dir.mkdir()
        except OSError:
            return RegistrierungsBericht(False, False, "registrierungsordner_konnte_nicht_angelegt_werden")
    if registration_dir.is_symlink() or not _innerhalb(registration_dir, target):
        return RegistrierungsBericht(False, False, "registrierungsordner_nicht_isoliert")
    name = f"{experiment.kennung}-{revision[:12]}.json"
    beleg = registration_dir / name
    if beleg.is_symlink():
        return RegistrierungsBericht(False, False, "registrierungsbeleg_symlink_blockiert", revision)
    state_path = Path(marker["state_path"]).resolve(strict=False)
    journal_path = Path(marker["journal_path"]).resolve(strict=False)
    if (_ueberlappt(registration_dir, state_path) or _ueberlappt(registration_dir, journal_path)
            or _ueberlappt(beleg, state_path) or _ueberlappt(beleg, journal_path)):
        return RegistrierungsBericht(False, False, "registrierungsordner_ueberlappt_mit_papierdaten", revision)
    payload = {"schema": 1, "typ": "candidate-registration",
               "registriert": True, "aktiviert": False,
               "kennung": experiment.kennung, "revision": revision,
               "branch": experiment.branch, "papierziel": str(target),
               "state_path": str(Path(marker["state_path"]).resolve(strict=False)),
               "journal_path": str(Path(marker["journal_path"]).resolve(strict=False))}
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if beleg.exists():
        try:
            same = beleg.read_text(encoding="utf-8") == encoded
        except (OSError, UnicodeError):
            same = False
        if same:
            return RegistrierungsBericht(True, False, "bereits_registriert_nicht_aktiviert", revision, beleg, True)
        return RegistrierungsBericht(False, False, "abweichender_registrierungsbeleg_existiert", revision, beleg)
    try:
        with beleg.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        return RegistrierungsBericht(False, False, "registrierungsbeleg_konkurrierend_angelegt", revision, beleg)
    except OSError:
        return RegistrierungsBericht(False, False, "registrierungsbeleg_konnte_nicht_geschrieben_werden", revision)
    return RegistrierungsBericht(True, False, "registriert_nicht_aktiviert", revision, beleg)


def schreibe_rollback_vermerk(ziel: Path, *, registrierung: RegistrierungsBericht) -> RegistrierungsBericht:
    """Vermerkt die Ablehnung einer Registrierung; aktiviert oder ändert nichts."""
    if (not isinstance(registrierung, RegistrierungsBericht)
            or registrierung.registriert is not True or registrierung.aktiviert is not False
            or not registrierung.beleg):
        return RegistrierungsBericht(False, False, "keine_gueltige_registrierung_zum_vermerken")
    marker, reason = _zielbeleg(Path(ziel))
    if reason:
        return RegistrierungsBericht(False, False, reason)
    target = Path(ziel).resolve(strict=True)
    if not _innerhalb(registrierung.beleg, target) or not registrierung.beleg.is_file():
        return RegistrierungsBericht(False, False, "registrierungsbeleg_nicht_im_papierziel")
    registration_dir = target / "candidate-registrations"
    if (not registration_dir.is_dir() or registration_dir.is_symlink()
            or not _innerhalb(registration_dir, target)):
        return RegistrierungsBericht(False, False, "registrierungsordner_nicht_isoliert", registrierung.revision)
    rollback = registration_dir / f"rejected-{registrierung.beleg.stem}.json"
    if rollback.is_symlink():
        return RegistrierungsBericht(False, False, "ablehnungsvermerk_symlink_blockiert", registrierung.revision)
    state_path = Path(marker["state_path"]).resolve(strict=False)
    journal_path = Path(marker["journal_path"]).resolve(strict=False)
    if _ueberlappt(rollback, state_path) or _ueberlappt(rollback, journal_path):
        return RegistrierungsBericht(False, False, "ablehnungsvermerk_ueberlappt_mit_papierdaten", registrierung.revision)
    payload = {"schema": 1, "typ": "candidate-registration-rejected",
               "registration": registrierung.beleg.name,
               "revision": registrierung.revision,
               "aktiviert": False}
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if rollback.exists():
        if rollback.read_text(encoding="utf-8") == encoded:
            return RegistrierungsBericht(True, False, "ablehnung_bereits_vermerkt", registrierung.revision, rollback, True)
        return RegistrierungsBericht(False, False, "abweichender_ablehnungsvermerk_existiert", registrierung.revision, rollback)
    try:
        with rollback.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError:
        return RegistrierungsBericht(False, False, "ablehnungsvermerk_konnte_nicht_geschrieben_werden", registrierung.revision)
    return RegistrierungsBericht(True, False, "ablehnung_vermerkt; kandidat_war_nicht_aktiviert",
                                 registrierung.revision, rollback)
