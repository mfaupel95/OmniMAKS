"""Gemeinsame, unveraenderliche Ergebnis- und Gate-Modelle."""
from .ergebnis import GateErgebnis, Kandidat, Messfenster
from .gates import bewerte_kandidat

__all__ = ["GateErgebnis", "Kandidat", "Messfenster", "bewerte_kandidat"]
