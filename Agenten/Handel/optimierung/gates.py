"""Fail-closed Bewertung von Papierkandidaten gegen eine unveraenderte Basis."""
from collections.abc import Mapping
import math

from .ergebnis import GateErgebnis, Kandidat, Messfenster


def _finite(x):
    if not isinstance(x, (int, float)) or isinstance(x, bool):
        return False
    try:
        return math.isfinite(x)
    except (OverflowError, TypeError, ValueError):
        return False


def _kandidat_form_gueltig(k):
    if not isinstance(k, Kandidat):
        return False
    try:
        return (all(isinstance(getattr(k, name), str) and bool(getattr(k, name))
                    for name in ("kennung", "strategie", "revision"))
                and type(k.daten_vollstaendig) is bool
                and type(k.reproduzierbar) is bool
                and all(hasattr(k, name) for name in ("papier", "oos", "holdout")))
    except (AttributeError, TypeError):
        return False


def _fenster_gueltig(name: str, f: Messfenster, gruende: list[str], *, min_runden: int):
    if not isinstance(f, Messfenster):
        gruende.append(f"{name}_messfenster_ungueltig")
        return
    try:
        zeit_ok = f.start is not None and f.ende is not None and f.start < f.ende
    except (AttributeError, TypeError, ValueError):
        zeit_ok = False
    if not zeit_ok:
        gruende.append(f"{name}_zeitfenster_ungueltig")
    if not _finite(f.netto_pct):
        gruende.append(f"{name}_netto_fehlt")
    if not _finite(f.max_drawdown_pct) or f.max_drawdown_pct < 0:
        gruende.append(f"{name}_drawdown_fehlt")
    if (not isinstance(f.runden_geschlossen, int) or isinstance(f.runden_geschlossen, bool)
            or f.runden_geschlossen < min_runden):
        gruende.append(f"{name}_zu_wenig_runden")
    if (not isinstance(f.runden_gepaart, int) or isinstance(f.runden_gepaart, bool)
            or f.runden_gepaart != f.runden_geschlossen):
        gruende.append(f"{name}_runden_unvollstaendig_oder_ungepaart")
    for feld, code in ((f.gebuehren_vollstaendig, "gebuehren"),
                       (f.funding_vollstaendig, "funding"),
                       (f.slippage_vollstaendig, "slippage")):
        if feld is not True:
            gruende.append(f"{name}_{code}_unvollstaendig")


def _fensterfolge_getrennt(prefix: str, fenster, gruende: list[str]):
    """Reject reused time intervals between train, OOS, and holdout stages."""
    namen = ("papier", "oos", "holdout")
    for links, rechts in zip(namen, namen[1:]):
        links_fenster = getattr(fenster, links)
        rechts_fenster = getattr(fenster, rechts)
        if not (isinstance(links_fenster, Messfenster)
                and isinstance(rechts_fenster, Messfenster)):
            continue
        try:
            disjunkt = links_fenster.ende < rechts_fenster.start
        except (TypeError, ValueError):
            disjunkt = False
        if not disjunkt:
            gruende.append(
                f"{prefix}_{links}_{rechts}_zeitfenster_nicht_disjunkt")


def _vergleichsfenster_passen(kandidat: Kandidat, basis: Kandidat,
                               gruende: list[str]):
    """Compare candidate and baseline on the same calendar intervals."""
    for name in ("papier", "oos", "holdout"):
        neu, alt = getattr(kandidat, name), getattr(basis, name)
        if not (isinstance(neu, Messfenster) and isinstance(alt, Messfenster)):
            continue
        if neu.start != alt.start or neu.ende != alt.ende:
            gruende.append(f"{name}_basis_zeitfenster_abweichend")


def bewerte_kandidat(kandidat: Kandidat, basis: Kandidat,
                      regeln: Mapping[str, object]) -> GateErgebnis:
    """Prueft Messbarkeit, Mindestumfang, Kosten, Drawdown und stabile Ueberlegenheit."""
    gruende: list[str] = []
    if not _kandidat_form_gueltig(kandidat):
        gruende.append("kandidat_eingabe_ungueltig")
    if not _kandidat_form_gueltig(basis):
        gruende.append("basis_eingabe_ungueltig")
    if gruende:
        return GateErgebnis(False, tuple(gruende))
    try:
        min_runden = regeln.get("min_runden") if isinstance(regeln, Mapping) else None
        deckel = regeln.get("max_drawdown_pct") if isinstance(regeln, Mapping) else None
    except (AttributeError, KeyError, TypeError, ValueError):
        min_runden, deckel = None, None
    if not isinstance(min_runden, int) or isinstance(min_runden, bool) or min_runden <= 0:
        gruende.append("regel_min_runden_fehlt_oder_ungueltig")
        min_runden = 1
    deckel_gueltig = _finite(deckel) and deckel >= 0
    if not deckel_gueltig:
        gruende.append("regel_drawdown_deckel_fehlt_oder_ungueltig")

    if kandidat.daten_vollstaendig is not True:
        gruende.append("daten_unvollstaendig")
    if kandidat.reproduzierbar is not True:
        gruende.append("nicht_reproduzierbar")
    if kandidat.strategie != basis.strategie:
        gruende.append("basis_strategie_abweichend")
    if kandidat.revision == basis.revision:
        gruende.append("revision_nicht_geaendert")

    _fensterfolge_getrennt("kandidat", kandidat, gruende)
    _fensterfolge_getrennt("basis", basis, gruende)
    _vergleichsfenster_passen(kandidat, basis, gruende)

    fenster = (("papier", kandidat.papier), ("oos", kandidat.oos),
               ("holdout", kandidat.holdout), ("basis_papier", basis.papier),
               ("basis_oos", basis.oos), ("basis_holdout", basis.holdout))
    for name, f in fenster:
        _fenster_gueltig(name, f, gruende,
                         min_runden=(min_runden if name.endswith("papier") else 1))
        if (isinstance(f, Messfenster) and deckel_gueltig
                and _finite(f.max_drawdown_pct) and f.max_drawdown_pct > deckel):
            gruende.append(f"{name}_drawdown_deckel_verletzt")

    for name in ("papier", "oos", "holdout"):
        neu, alt = getattr(kandidat, name), getattr(basis, name)
        if isinstance(neu, Messfenster) and isinstance(alt, Messfenster):
            if _finite(neu.netto_pct) and _finite(alt.netto_pct):
                if neu.netto_pct <= alt.netto_pct:
                    gruende.append(f"{name}_keine_verbesserung_gegen_basis")
    return GateErgebnis(not gruende, tuple(gruende))
