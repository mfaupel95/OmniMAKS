"""Read-only discovery for strategy evidence.

This adapter deliberately does not invoke backtests or trading scripts. The
existing trace journals have different schemas; until a trace has a validated
paired-round adapter, discovery is a finding, never a performance candidate.
"""
from __future__ import annotations

import ast
import csv
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .ergebnis import Kandidat

HANDEL = Path(__file__).resolve().parents[1]
_JOURNAL = "handelsjournal.csv"


def _registry(repo: Path = HANDEL.parents[1]) -> dict[str, dict]:
    """Read the canonical SPUREN literal without importing the runtime loop."""
    source = (repo / "Agenten" / "Handel" / "dauerlauf.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "SPUREN" for t in node.targets):
            if isinstance(node.value, ast.Dict):
                result = {}
                for key_node, value_node in zip(node.value.keys, node.value.values):
                    key = ast.literal_eval(key_node)
                    entry = {}
                    if isinstance(value_node, ast.Dict):
                        for field_node, field_value in zip(value_node.keys, value_node.values):
                            try:
                                entry[ast.literal_eval(field_node)] = ast.literal_eval(field_value)
                            except (ValueError, TypeError):
                                # Runtime-only fields (for example an absolute
                                # interpreter path) are intentionally ignored.
                                continue
                    result[key] = entry
                return result
            break
    raise ValueError("SPUREN-Register nicht als auswertbares Literal gefunden")


def _journal(repo: Path, spur: str, eintrag: dict) -> Path:
    folder = eintrag.get("ordner")
    if not isinstance(folder, str) or not folder or Path(folder).is_absolute() or ".." in Path(folder).parts:
        raise ValueError("ungueltiger Register-Ordner")
    return repo / "Agenten" / "Handel" / folder / _JOURNAL


def _zaehle_zeilen(pfad: Path) -> int:
    """Count parseable CSV records only; this is not a count of closed rounds."""
    with pfad.open("r", encoding="utf-8-sig", newline="") as datei:
        return sum(1 for _ in csv.DictReader(datei))


def finde_strategiekandidaten(spuren: Sequence[str], *, datenstand: datetime,
                               repo: Path | None = None) -> list[Kandidat]:
    """Return no candidate without real, paired, cost-complete measurements.

    The public discovery API has no experiment/evaluator dependency yet. It
    therefore stays intentionally empty rather than manufacture a candidate
    from journal row counts or stored verdicts.
    """
    if not isinstance(datenstand, datetime):
        raise TypeError("datenstand muss datetime sein")
    # Validate requested names and the registry; callers get clear errors for
    # stale names, but this read-only pass does not execute a strategy.
    root = Path(repo).resolve() if repo is not None else HANDEL.parents[1]
    registry = _registry(root)
    unbekannt = sorted(set(spuren) - registry.keys())
    if unbekannt:
        raise KeyError("unbekannte Spuren: " + ", ".join(unbekannt))
    # No registered trace currently has a bound, read-only adapter that can
    # prove paired closed rounds, full costs, time windows and reproducibility.
    return []


def strategiebefund(repo: Path, spur: str, datenstand: datetime) -> dict:
    """Describe available evidence without asserting performance validity."""
    registry = _registry(repo)
    if spur not in registry:
        return {"spur": spur, "status": "nicht_auswertbar", "grund": "nicht im SPUREN-Register"}
    try:
        pfad = _journal(repo, spur, registry[spur])
    except ValueError as exc:
        return {"spur": spur, "status": "nicht_auswertbar", "grund": str(exc)}
    if not pfad.is_file():
        return {"spur": spur, "status": "datenarm", "grund": "kein Journal am registrierten Pfad",
                "journal": str(pfad), "datenstand": datenstand}
    try:
        zeilen = _zaehle_zeilen(pfad)
    except (OSError, UnicodeError, csv.Error) as exc:
        return {"spur": spur, "status": "nicht_auswertbar",
                "grund": "Journal nicht lesbar: " + type(exc).__name__, "journal": str(pfad)}
    return {"spur": spur, "status": "nicht_auswertbar",
            "grund": "Journalzeilen sind ohne validierten Paarungs- und Kostenadapter kein Leistungsbeleg",
            "journal": str(pfad), "journalzeilen": zeilen, "datenstand": datenstand}
