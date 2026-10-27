"""Vergleicht vor-normalisierte Spurabschnitte, ohne selbst PnL zu berechnen.

``vergleiche`` erwartet je Buch/Abschnitt ein Mapping mit:
``spur``, ``stufe``, ``instrument``, ``modus``, ``universum``, ``abschnitt``,
``einheit`` (Gruppenschlüssel); ``zeitraum_start``/``zeitraum_ende`` als
zeitzonenbewusste ISO-Zeitstempel; ``runden`` als Liste mit
``ausstieg_zeit``, bereits netto-normalisiertem ``netto`` und booleschem
``kosten_belegt``; ``startkapital`` plus exakt passendem
``startkapital_zeitpunkt``; ``equity_curve`` als Liste ``{zeit, wert}``,
``offene_positionen`` und ``datenqualitaet`` (Liste von Gründen). Die
Paarungs- und Kostenlogik bleibt bei den bestehenden Journaladaptern;
unpaarige/duplizierte Runden müssen diese im ``datenqualitaet``-Feld melden.

Unvollständige Metadaten werden nie zusammengelegt. Datenqualitätsprobleme an
Runden/Kosten/Kapital sperren die Rangzahl; fehlende offene Positionsstände
bleiben als separate Warnung sichtbar. Kleine Stichproben werden nur markiert.
Drawdown gibt es nur bei einer chronologischen Kurve mit Messpunkten exakt am
Anfang und Ende des gemeinsamen Fensters.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
from typing import Any, Iterable, Mapping

MIN_RUNDEN_HINWEIS = 8
_META = ("instrument", "modus", "universum", "abschnitt", "einheit")
OPEN_UNKNOWN_WARNING = "offene Positionen nicht belegt"


@dataclass
class Buchvergleich:
    spur: str
    stufe: str
    instrument: str | None
    modus: str | None
    universum: str | None
    abschnitt: str | None
    einheit: str | None
    zeitraum_start: datetime | None
    zeitraum_ende: datetime | None
    runden: int = 0
    netto_pnl: float | None = None
    startkapital: float | None = None
    netto_rendite_pct: float | None = None
    offene_positionen: int | None = None
    drawdown_pct: float | None = None
    drawdown_grund: str | None = None
    datenqualitaet: list[str] = field(default_factory=list)
    kleine_stichprobe: bool = False
    rang: int | None = None
    rang_grund: str | None = None


@dataclass
class Vergleichsgruppe:
    schluessel: tuple[str | None, ...]
    zeitraum_start: datetime | None
    zeitraum_ende: datetime | None
    buecher: list[Buchvergleich]
    vergleichbar: bool
    grund: str | None = None


def _zeit(wert: Any) -> datetime | None:
    if isinstance(wert, datetime):
        d = wert
    elif isinstance(wert, str):
        try:
            d = datetime.fromisoformat(wert.replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None
    if d.tzinfo is None or d.utcoffset() is None:
        return None
    return d.astimezone(timezone.utc)


def _zahl(wert: Any) -> float | None:
    if isinstance(wert, bool) or not isinstance(wert, (int, float)):
        return None
    x = float(wert)
    return x if math.isfinite(x) else None


def _qualitaet(quelle: Mapping[str, Any]) -> list[str]:
    raw = quelle.get("datenqualitaet") or []
    if isinstance(raw, str):
        raw = [raw]
    elif not isinstance(raw, (list, tuple, set)):
        raw = ["Datenqualitätsfeld ist ungültig"]
    return sorted({str(x).strip() for x in raw if str(x).strip()})


def _drawdown(curve: Any, start: datetime, end: datetime) -> tuple[float | None, str | None]:
    if not isinstance(curve, list) or len(curve) < 2:
        return None, "keine ausreichende Kapitalkurve"
    points = []
    for row in curve:
        if not isinstance(row, Mapping):
            return None, "ungültiger Kurvenpunkt"
        t, value = _zeit(row.get("zeit")), _zahl(row.get("wert"))
        if t is None or value is None:
            return None, "Kurvenzeit oder -wert fehlt/ist ungültig"
        points.append((t, value))
    if any(points[i][0] >= points[i + 1][0] for i in range(len(points) - 1)):
        return None, "Kapitalkurve ist nicht streng chronologisch"
    points = [(t, value) for t, value in points if start <= t <= end]
    if len(points) < 2 or points[0][0] != start or points[-1][0] != end:
        return None, "Kapitalkurve deckt Anfang und Ende des Vergleichsfensters nicht exakt ab"
    peak = points[0][1]
    if peak <= 0:
        return None, "nicht positives Startniveau der Kapitalkurve"
    max_dd = 0.0
    for _, value in points[1:]:
        peak = max(peak, value)
        max_dd = max(max_dd, (peak - value) / peak * 100.0)
    return max_dd, None


def _buch(quelle: Mapping[str, Any], start: datetime | None, end: datetime | None,
          cohort_size: int, duplicate_id: bool) -> Buchvergleich:
    q = _qualitaet(quelle)
    # This exact normalized warning is informative but does not invalidate
    # realized ROI. Any other adapter-provided quality finding remains blocking.
    rangblocker = [grund for grund in q if grund != OPEN_UNKNOWN_WARNING]
    spur, stufe = str(quelle.get("spur") or ""), str(quelle.get("stufe") or "")
    instrument = quelle.get("instrument")
    modus = quelle.get("modus")
    universum = quelle.get("universum")
    abschnitt = quelle.get("abschnitt")
    einheit = quelle.get("einheit")
    result = Buchvergleich(spur, stufe, instrument, modus, universum, abschnitt,
                           einheit, start, end, datenqualitaet=q)
    if not spur or not stufe:
        grund = "Spur oder Stufe fehlt"
        result.datenqualitaet.append(grund)
        rangblocker.append(grund)
    if duplicate_id:
        grund = "mehrere Quelldatensätze für dieselbe Spur/Stufe"
        result.datenqualitaet.append(grund)
        rangblocker.append(grund)
    raw_open = quelle.get("offene_positionen")
    if isinstance(raw_open, int) and not isinstance(raw_open, bool) and raw_open >= 0:
        result.offene_positionen = raw_open
    else:
        # Offene Positionen bleiben ein Pflichtbefund, betreffen aber nicht
        # die bereits realisierte Rendite-Rangzahl.
        if OPEN_UNKNOWN_WARNING not in result.datenqualitaet:
            result.datenqualitaet.append(OPEN_UNKNOWN_WARNING)

    rounds = quelle.get("runden")
    if not isinstance(rounds, list):
        rounds = []
        grund = "Rundenliste fehlt oder ist ungültig"
        result.datenqualitaet.append(grund)
        rangblocker.append(grund)
    included = []
    if start is not None and end is not None:
        for row in rounds:
            t = _zeit(row.get("ausstieg_zeit")) if isinstance(row, Mapping) else None
            if t is None:
                grund = "Runde ohne gültigen Ausstiegszeitstempel"
                result.datenqualitaet.append(grund)
                rangblocker.append(grund)
            elif start <= t <= end:
                included.append(row)
    result.runden = len(included)
    result.kleine_stichprobe = result.runden < MIN_RUNDEN_HINWEIS
    nets = []
    for row in included:
        net = _zahl(row.get("netto"))
        if row.get("kosten_belegt") is not True or net is None:
            grund = "Netto/Kosten einer Runde nicht vollständig belegt"
            result.datenqualitaet.append(grund)
            rangblocker.append(grund)
        else:
            nets.append(net)
    costs_complete = len(nets) == len(included)
    if costs_complete:
        result.netto_pnl = sum(nets)

    capital = _zahl(quelle.get("startkapital"))
    capital_at = _zeit(quelle.get("startkapital_zeitpunkt"))
    if capital is not None and capital > 0 and start is not None and capital_at == start:
        result.startkapital = capital
        curve = quelle.get("equity_curve")
        if isinstance(curve, list):
            startpoints = [row for row in curve if isinstance(row, Mapping)
                           and _zeit(row.get("zeit")) == start]
            if len(startpoints) == 1:
                curve_start = _zahl(startpoints[0].get("wert"))
                if curve_start is not None and not math.isclose(
                        curve_start, capital, rel_tol=1e-9, abs_tol=1e-9):
                    grund = "Startkapital stimmt nicht mit Kapitalkurve am Fensterbeginn überein"
                    result.datenqualitaet.append(grund)
                    rangblocker.append(grund)
    else:
        grund = "Startkapital nicht positiv oder nicht exakt zum Fensterbeginn belegt"
        result.datenqualitaet.append(grund)
        rangblocker.append(grund)
    if result.netto_pnl is not None and result.startkapital is not None:
        result.netto_rendite_pct = result.netto_pnl / result.startkapital * 100.0

    if start is not None and end is not None:
        result.drawdown_pct, result.drawdown_grund = _drawdown(
            quelle.get("equity_curve"), start, end)
    else:
        result.drawdown_grund = "kein gemeinsames Vergleichsfenster"
    # One existing quality flag is enough to withhold a rank; small samples are
    # separately flagged and intentionally don't block a rank.
    rankable = (cohort_size >= 2 and result.netto_rendite_pct is not None
                and costs_complete and not rangblocker)
    if not rankable:
        if cohort_size < 2:
            result.rang_grund = "kein zweites Buch in derselben Vergleichsgruppe"
        else:
            result.rang_grund = "Datenqualität/Kosten/Startkapital reichen nicht für eine Rangzahl"
    return result


def vergleiche(quellen: Iterable[Mapping[str, Any]], start: Any = None,
               ende: Any = None) -> list[Vergleichsgruppe]:
    """Bilde Kohorten und sortiere belastbare Bücher renditepriorisiert.

    ``quellen`` ist eine Folge der oben dokumentierten normalisierten
    Buchabschnitte. ``start``/``ende`` sind optionale, zeitzonenbewusste
    ISO-Grenzen und klemmen das ohnehin längste gemeinsame Zeitfenster ein.
    Ergebnisse bleiben reine Werte; keine Quelldatei wird gelesen oder
    verändert.
    """
    requested_start = _zeit(start) if start is not None else None
    requested_end = _zeit(ende) if ende is not None else None
    window_error = None
    if (start is not None and requested_start is None) or (ende is not None and requested_end is None):
        window_error = "angeforderte Zeitgrenze fehlt oder ist ungültig"
    elif requested_start is not None and requested_end is not None and requested_start >= requested_end:
        window_error = "angefordertes Zeitfenster ist leer oder rückwärts"
    source_rows = []
    try:
        iterator = iter(quellen)
    except TypeError as exc:
        raise TypeError("quellen muss eine Folge normalisierter Datensätze sein") from exc
    for q in iterator:
        if isinstance(q, Mapping):
            source_rows.append(q)
        else:
            source_rows.append({"datenqualitaet": ["Quelldatensatz ist ungültig"]})
    buckets: dict[tuple[Any, ...], list[tuple[int, Mapping[str, Any]]]] = {}
    for index, q in enumerate(source_rows):
        meta = tuple(q.get(k) for k in _META)
        missing = any(not isinstance(v, str) or not v.strip() for v in meta)
        key = (False, index) if missing else (True,) + meta
        buckets.setdefault(key, []).append((index, q))

    groups = []
    for key in sorted(buckets, key=lambda k: tuple(str(x) for x in k)):
        members = sorted(buckets[key], key=lambda pair: (
            str(pair[1].get("spur", "")), str(pair[1].get("stufe", "")), pair[0]))
        valid_meta = key[0] is True
        periods = [(_zeit(q.get("zeitraum_start")), _zeit(q.get("zeitraum_ende")))
                   for _, q in members]
        if valid_meta and all(a is not None and b is not None and a <= b for a, b in periods):
            common_start = max(a for a, _ in periods if a is not None)
            common_end = min(b for _, b in periods if b is not None)
            if requested_start is not None:
                common_start = max(common_start, requested_start)
            if requested_end is not None:
                common_end = min(common_end, requested_end)
        else:
            common_start = common_end = None
        if window_error:
            common_start = common_end = None
        overlap = common_start is not None and common_end is not None and common_start < common_end
        if not overlap:
            common_start = common_end = None
        cohort_size = len(members) if overlap and valid_meta else 1
        ids = [(str(q.get("spur") or ""), str(q.get("stufe") or ""))
               for _, q in members]
        duplicate_ids = {identity for identity in ids if ids.count(identity) > 1}
        books = [_buch(q, common_start, common_end, cohort_size,
                       (str(q.get("spur") or ""), str(q.get("stufe") or "")) in duplicate_ids)
                 for _, q in members]
        if not valid_meta:
            for book in books:
                source = members[0][1]
                missing = [name for name in _META
                           if not isinstance(source.get(name), str)
                           or not source.get(name, "").strip()]
                book.datenqualitaet.append("Vergleichsmetadaten fehlen: " + ", ".join(missing))
                book.rang_grund = "Instrument/Modus/Universum/Abschnitt/Einheit unvollständig"
        elif not overlap:
            for book in books:
                reason = window_error or "kein gemeinsames Vergleichszeitfenster"
                book.datenqualitaet.append(reason)
                book.rang_grund = reason
        ranked = [b for b in books if b.rang_grund is None]
        ranked.sort(key=lambda b: (-b.netto_rendite_pct, -b.netto_pnl,
                                  b.spur, b.stufe))
        for rank, book in enumerate(ranked, 1):
            book.rang = rank
        # Keep the displayed order aligned with the calculated ranking.
        books.sort(key=lambda b: (b.rang is None, b.rang or 0, b.spur, b.stufe))
        comparable = bool(overlap and valid_meta and len(members) >= 2)
        if valid_meta and len(members) < 2:
            group_reason = "kein zweites Buch in derselben Vergleichsgruppe"
        else:
            group_reason = (None if overlap and valid_meta else
                            ("fehlende Vergleichsmetadaten" if not valid_meta else
                             (window_error or "kein gemeinsames Zeitfenster")))
        if valid_meta:
            group_key = tuple(key[1:])
        else:
            # The incomplete book remains visible but cannot be merged with any
            # other unknown cohort, even when all unknown fields match.
            group_key = tuple(members[0][1].get(k) for k in _META)
        groups.append(Vergleichsgruppe(group_key, common_start, common_end,
                                       books, comparable, group_reason))
    return groups
