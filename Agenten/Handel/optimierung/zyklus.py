"""Deterministic, read-only orchestration for the two optimization lanes."""
from __future__ import annotations

import ast
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .ergebnis import Kandidat
from .strategie import finde_strategiekandidaten, strategiebefund
from .verbesserung import finde_technische_verbesserungen, verbesserungsbefund


@dataclass(frozen=True)
class SpurBefund:
    spur: str
    status: str
    grund: str
    details: tuple[tuple[str, object], ...] = ()


@dataclass(frozen=True)
class ZyklusBericht:
    """Immutable lane-separated report; candidates require measured evidence."""
    datenstand: datetime
    basisrevision: str | None
    strategie: tuple[SpurBefund, ...]
    verbesserung: tuple[SpurBefund, ...]
    strategiekandidaten: tuple[Kandidat, ...]
    verbesserungskandidaten: tuple[Kandidat, ...]
    blockaden: tuple[str, ...]
    revisionen: tuple[tuple[str, str], ...]


def _spuren(repo: Path) -> tuple[str, ...]:
    quelle = repo / "Agenten" / "Handel" / "dauerlauf.py"
    tree = ast.parse(quelle.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "SPUREN" for t in node.targets):
            if isinstance(node.value, ast.Dict):
                return tuple(ast.literal_eval(key) for key in node.value.keys)
            break
    raise ValueError("SPUREN-Register nicht als Literal lesbar")


def _revision(repo: Path) -> str | None:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                                capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def _rotation(spuren: tuple[str, ...], datenstand: datetime) -> tuple[str, ...]:
    if not spuren:
        return ()
    # Rotate the inspection start every calendar day, deterministically.
    index = datenstand.date().toordinal() % len(spuren)
    return spuren[index:] + spuren[:index]


def _befund(row: dict) -> SpurBefund:
    details = tuple(sorted((k, v) for k, v in row.items() if k not in {"spur", "status", "grund"}))
    return SpurBefund(row["spur"], row["status"], row["grund"], details)


def fuehre_zyklus_aus(repo: Path, *, datenstand: datetime) -> ZyklusBericht:
    """Inspect every registry trace in separate lanes; never starts a runner."""
    repo = Path(repo).resolve()
    if not isinstance(datenstand, datetime) or datenstand.tzinfo is None:
        raise ValueError("datenstand muss ein timezone-aware datetime sein")
    traces = _spuren(repo)
    ordered = _rotation(traces, datenstand)
    strategy = tuple(_befund(strategiebefund(repo, s, datenstand)) for s in ordered)
    engineering = tuple(_befund(verbesserungsbefund(repo, s, datenstand)) for s in ordered)

    # These adapters perform discovery only and cannot create measured
    # candidates. Keep their API output separate from the trace-status ledger.
    candidates_s = tuple(finde_strategiekandidaten(ordered, datenstand=datenstand, repo=repo))
    candidates_e = tuple(finde_technische_verbesserungen(ordered, datenstand=datenstand, repo=repo))
    blockers = []
    for row in strategy:
        if row.status in {"datenarm", "nicht_auswertbar"}:
            blockers.append((0 if row.status == "nicht_auswertbar" else 1,
                             f"strategie:{row.status}:{row.spur}:{row.grund}"))
    for row in engineering:
        if row.status in {"datenarm", "nicht_auswertbar"}:
            blockers.append((0 if row.status == "nicht_auswertbar" else 1,
                             f"verbesserung:{row.status}:{row.spur}:{row.grund}"))
    blockers.sort(key=lambda item: (item[0], item[1]))
    rev = _revision(repo)
    revisions = (("basis", rev),) if rev else ()
    if rev is None:
        blockers.insert(0, (-1, "basisrevision:nicht ermittelbar"))
    return ZyklusBericht(datenstand, rev, strategy, engineering,
                         candidates_s, candidates_e,
                         tuple(text for _, text in blockers), revisions)
