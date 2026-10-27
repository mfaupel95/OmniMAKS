"""Read-only discovery for technical/operational improvement evidence."""
from __future__ import annotations

import ast
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .ergebnis import Kandidat
from .strategie import _registry


def finde_technische_verbesserungen(spuren: Sequence[str], *, datenstand: datetime,
                                    repo: Path | None = None) -> list[Kandidat]:
    """No candidate is emitted by static discovery alone.

    A code-quality observation becomes a candidate only after a reproducible
    change and independent before/after measurements exist. This first adapter
    intentionally only inventories source availability.
    """
    if not isinstance(datenstand, datetime):
        raise TypeError("datenstand muss datetime sein")
    root = Path(repo).resolve() if repo is not None else Path(__file__).resolve().parents[3]
    registry = _registry(root)
    unbekannt = sorted(set(spuren) - registry.keys())
    if unbekannt:
        raise KeyError("unbekannte Spuren: " + ", ".join(unbekannt))
    return []


def verbesserungsbefund(repo: Path, spur: str, datenstand: datetime) -> dict:
    registry = _registry(repo)
    if spur not in registry:
        return {"spur": spur, "status": "nicht_auswertbar", "grund": "nicht im SPUREN-Register"}
    folder = registry[spur].get("ordner")
    if not isinstance(folder, str) or not folder or Path(folder).is_absolute() or ".." in Path(folder).parts:
        return {"spur": spur, "status": "nicht_auswertbar", "grund": "ungueltiger Register-Ordner"}
    base = repo / "Agenten" / "Handel" / folder
    script = registry[spur].get("skript", "handeln.py")
    if not isinstance(script, str) or Path(script).name != script:
        return {"spur": spur, "status": "nicht_auswertbar", "grund": "ungueltiger Skriptname"}
    target = base / script
    if not target.is_file():
        return {"spur": spur, "status": "datenarm", "grund": "registrierter Quellpfad fehlt",
                "quelle": str(target), "datenstand": datenstand}
    # Parse syntax only: importing or running the script could trigger runtime
    # setup, external connections, or writes.
    try:
        ast.parse(target.read_text(encoding="utf-8"), filename=str(target))
    except (OSError, UnicodeError, SyntaxError) as exc:
        return {"spur": spur, "status": "nicht_auswertbar",
                "grund": "Quelltext nicht statisch pruefbar: " + type(exc).__name__,
                "quelle": str(target)}
    return {"spur": spur, "status": "nicht_auswertbar",
            "grund": "nur Syntax geprueft; Adapter fuer technische Hypothese, Vorher-Nachher-Test und Reproduzierbarkeit fehlt",
            "quelle": str(target), "datenstand": datenstand}
