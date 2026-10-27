"""Sanitized, read-only runtime snapshots for trading services."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Mapping
import json
import csv
import io
import subprocess

from inventar import InventarEintrag


def freqtrade_modus(bot: Mapping[str, object], effektive_config: Mapping[str, object] | None) -> str:
    if not effektive_config:
        return "Unbekannt"
    value = effektive_config.get("dry_run")
    if value is True:
        return "Papier"
    if value is False:
        return "Live"
    return "Unbekannt"


def _snapshot(text: str):
    if not text:
        return None
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return None


def _fehler_snapshot(text: str, quelle: str) -> list[InventarEintrag] | None:
    value = _snapshot(text)
    if isinstance(value, dict) and value.get("error"):
        return [InventarEintrag("runtime-fehler", quelle, "", status="unbekannt",
                quelle=quelle, hinweise=(str(value["error"]),))]
    return None


def sammle_runtime_snapshots() -> tuple[str, str, str]:
    """Fetch sanitized metadata only; never request command lines or task actions."""
    def run(args):
        try:
            return subprocess.run(args, capture_output=True, check=True, text=True,
                encoding="utf-8", errors="replace", timeout=8).stdout
        except (OSError, subprocess.SubprocessError) as exc:
            return json.dumps({"error": f"nicht verfügbar ({type(exc).__name__})"})

    docker_out = run(["docker", "ps", "-a", "--format", "{{.Names}}\t{{.State}}\t{{.CreatedAt}}"])
    docker_rows = []
    if not _fehler_snapshot(docker_out, "Docker"):
        for line in docker_out.splitlines():
            name, sep, tail = line.partition("\t")
            state, sep2, created = tail.partition("\t")
            if sep and sep2 and name:
                docker_rows.append({"name": name, "state": state, "created": created})

    task_out = run(["schtasks", "/Query", "/FO", "CSV"])
    task_rows = []
    if not _fehler_snapshot(task_out, "Aufgabenplanung"):
        try:
            for row in csv.DictReader(io.StringIO(task_out)):
                name = row.get("TaskName") or row.get("Aufgabenname")
                state = row.get("Status") or row.get("State") or "unbekannt"
                if name:
                    task_rows.append({"name": name, "state": state,
                                      "enabled": "disabled" not in state.casefold()})
        except (csv.Error, UnicodeError):
            task_out = json.dumps({"error": "Aufgabenliste konnte nicht geparst werden"})

    # tasklist exposes image names and PIDs only; command-line switches and
    # process environments are intentionally not queried.
    proc_out = run(["tasklist", "/FO", "CSV", "/NH"])
    process_rows = []
    if not _fehler_snapshot(proc_out, "Prozesse"):
        try:
            for row in csv.reader(io.StringIO(proc_out)):
                if row and row[0].casefold() in {"python.exe", "pythonw.exe", "hermes.exe", "freqtrade.exe", "omnitrade.exe"}:
                    process_rows.append({"name": row[0], "running": True})
        except (csv.Error, UnicodeError):
            proc_out = json.dumps({"error": "Prozessliste konnte nicht geparst werden"})
    docker_json = docker_out if _fehler_snapshot(docker_out, "Docker") else json.dumps(docker_rows)
    task_json = task_out if _fehler_snapshot(task_out, "Task") else json.dumps(task_rows)
    proc_json = proc_out if _fehler_snapshot(proc_out, "Prozesse") else json.dumps(process_rows)
    return docker_json, task_json, proc_json


def _stamp(value) -> str:
    if not value:
        return ""
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, timezone.utc).astimezone().isoformat(timespec="seconds")
    return str(value)


def lade_betrieb(repo: Path, *, docker_snapshot: str, task_snapshot: str,
                 prozess_snapshot: str) -> list[InventarEintrag]:
    """Build rows from caller-provided snapshots; failures stay explicitly unknown."""
    rows: list[InventarEintrag] = []
    gelesen = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    docker = _snapshot(docker_snapshot)
    failed = _fehler_snapshot(docker_snapshot, "Docker-Snapshot")
    docker_known = not failed and docker is not None
    docker_names: set[str] = set()
    if failed:
        rows.extend(failed)
    elif docker is None:
        rows.append(InventarEintrag("runtime-fehler", "Docker", str(repo), status="unbekannt",
                    quelle="Docker-Snapshot", hinweise=("Snapshot fehlt oder ungültig",)))
    else:
        items = docker if isinstance(docker, list) else docker.get("containers", []) if isinstance(docker, dict) else []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get("Name") or item.get("Names") or item.get("name") or "Container"
            docker_names.add(str(name).lstrip("/"))
            state = item.get("State") or item.get("state") or "unbekannt"
            rows.append(InventarEintrag("container", str(name), str(repo), status=str(state),
                modus="Unbekannt", aktualisiert=_stamp(item.get("CreatedAt") or item.get("created")) or gelesen,
                quelle="Docker-Snapshot", hinweise=()))
    tasks = _snapshot(task_snapshot)
    failed = _fehler_snapshot(task_snapshot, "Task-Snapshot")
    if failed:
        rows.extend(failed)
    elif tasks is None:
        rows.append(InventarEintrag("runtime-fehler", "Aufgabenplanung", str(repo), status="unbekannt",
                    quelle="Task-Snapshot", hinweise=("Snapshot fehlt oder ungültig",)))
    else:
        items = tasks if isinstance(tasks, list) else tasks.get("tasks", []) if isinstance(tasks, dict) else []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get("TaskName") or item.get("name") or "Aufgabe"
            state = item.get("State") or item.get("state") or "unbekannt"
            if item.get("Enabled") is False or item.get("enabled") is False:
                state = "deaktiviert"
            rows.append(InventarEintrag("routine", str(name), str(repo), status=str(state),
                modus="Unbekannt", aktualisiert=_stamp(item.get("LastRunTime") or item.get("last_run")) or gelesen,
                quelle="Task-Snapshot"))
    processes = _snapshot(prozess_snapshot)
    failed = _fehler_snapshot(prozess_snapshot, "Prozess-Snapshot")
    if failed:
        rows.extend(failed)
    elif processes is None:
        rows.append(InventarEintrag("runtime-fehler", "Prozesse", str(repo), status="unbekannt",
                    quelle="Prozess-Snapshot", hinweise=("Snapshot fehlt oder ungültig",)))
    else:
        items = processes if isinstance(processes, list) else processes.get("processes", []) if isinstance(processes, dict) else []
        for item in items:
            if isinstance(item, dict):
                # Deliberately ignore command lines and all arguments.
                rows.append(InventarEintrag("prozess", str(item.get("name") or item.get("Name") or "Prozess"),
                    str(repo), status="läuft" if item.get("running", True) else "gestoppt",
                    aktualisiert=gelesen, quelle="Prozess-Snapshot"))

    # Status comes through the existing sanitized bridge: only dry_run and
    # reachability are consumed, never credentials or returned config fields.
    try:
        import freqtrade_bridge
        bots = freqtrade_bridge.bots()
        if docker_known:
            for bot in bots:
                expected = str(bot.get("container") or ("freqtrade-" + str(bot.get("name", "")))).lstrip("/")
                if expected and expected not in docker_names:
                    rows.append(InventarEintrag("container", expected, str(repo), status="fehlt",
                        modus="Unbekannt", aktualisiert=gelesen, quelle="Docker-Snapshot",
                        hinweise=("Container in Bot-Registrierung vorhanden, im Docker-Snapshot fehlend",)))
        for bot in bots:
            try:
                snapshot = freqtrade_bridge.lage_fuer(bot)
                mode = freqtrade_modus(bot, snapshot if snapshot.get("erreichbar") else None)
                state = "läuft" if snapshot.get("erreichbar") else "unbekannt"
                hints = () if mode != "Unbekannt" else ("Effektiver Modus nicht bestätigt",)
            except Exception as exc:  # source failure remains visible, never inferred as paper
                mode, state, hints = "Unbekannt", "unbekannt", (f"Laufzeitabfrage fehlgeschlagen: {type(exc).__name__}",)
            rows.append(InventarEintrag("freqtrade", str(bot.get("name", "Bot")), str(repo),
                status=state, modus=mode, aktualisiert=gelesen,
                quelle="freqtrade_bridge.lage_fuer", hinweise=hints))
    except Exception as exc:
        rows.append(InventarEintrag("runtime-fehler", "Freqtrade", str(repo), status="unbekannt",
                    quelle="freqtrade_bridge", hinweise=(f"Quelle nicht verfügbar: {type(exc).__name__}",)))
    return rows
