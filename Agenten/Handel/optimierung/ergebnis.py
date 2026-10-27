"""Typen fuer die evidenzbasierte Papierpromotion (keine Laufzeitaktionen)."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Messfenster:
    """Zeitlich abgegrenzte Messung; netto ist nach allen Kosten."""
    start: Optional[datetime]
    ende: Optional[datetime]
    netto_pct: Optional[float]
    max_drawdown_pct: Optional[float]
    runden_geschlossen: int
    runden_gepaart: int
    gebuehren_vollstaendig: bool
    funding_vollstaendig: bool
    slippage_vollstaendig: bool


@dataclass(frozen=True)
class Kandidat:
    kennung: str
    strategie: str
    revision: str
    papier: Messfenster
    oos: Messfenster
    holdout: Messfenster
    daten_vollstaendig: bool
    reproduzierbar: bool


@dataclass(frozen=True)
class GateErgebnis:
    promotion_erlaubt: bool
    gruende: tuple[str, ...]
