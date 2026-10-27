"""Read-only adapter from active paper journals to the cohort comparator.

The adapter deliberately refuses to infer universe, capital, drawdown, or
missing costs. It imports only the existing reporting module (never the
duration runner) and writes reports only to an explicitly selected directory.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGES = ("niedrig", "mittel", "hoch")


def active_traces(source: Path) -> list[str]:
    """Read keys from the literal SPUREN map without importing dauerlauf.py."""
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    found = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "SPUREN" for t in node.targets):
            found = node.value
    if not isinstance(found, ast.Dict):
        raise ValueError("SPUREN ist kein direkt lesbares Mapping")
    arms_holder = any(
        isinstance(k, ast.Constant) and k.value == "llm_stunde"
        and isinstance(v, ast.Dict)
        and any(isinstance(n, ast.Constant) and n.value == "arme"
                for n in v.keys)
        for k, v in zip(found.keys, found.values)
    )
    names = [k.value for k in found.keys if isinstance(k, ast.Constant)
             and isinstance(k.value, str)
             and not (arms_holder and k.value == "llm_stunde")]
    # LLM arms are values within the active llm_stunde entry, not top-level keys.
    for key, value in zip(found.keys, found.values):
        if isinstance(key, ast.Constant) and key.value == "llm_stunde" and isinstance(value, ast.Dict):
            for k, v in zip(value.keys, value.values):
                if isinstance(k, ast.Constant) and k.value == "arme":
                    if not isinstance(v, (ast.Tuple, ast.List)):
                        raise ValueError("llm_stunde.arme kann nicht literal gelesen werden")
                    for arm in v.elts:
                        if not isinstance(arm, (ast.Tuple, ast.List)) or not arm.elts:
                            raise ValueError("llm_stunde.arme enthält einen ungültigen Eintrag")
                        name = arm.elts[0]
                        if not isinstance(name, ast.Constant) or not isinstance(name.value, str):
                            raise ValueError("llm_stunde.arme enthält keinen statischen Namen")
                        names.append(name.value)
    return list(dict.fromkeys(names))


@contextmanager
def _reader_context(adapter, root: Path, stage: str):
    old_root, old_stage = adapter.HIER, adapter.STUFE
    adapter.HIER, adapter.STUFE = root, (None if stage == "niedrig" else stage)
    try:
        yield
    finally:
        adapter.HIER, adapter.STUFE = old_root, old_stage


def _value(row, *keys):
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def _timestamp(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None
    return dt.astimezone(timezone.utc)


def _journal_source(adapter, root: Path, trace: str) -> str:
    """Resolve the journal path with the same book-then-stage mapping as zeilen()."""
    filename = "handelsjournal.csv"
    locate = getattr(adapter, "_ort", None)
    if locate is None:
        folder = trace
    else:
        folder, filename = locate(trace, filename)
    stage = getattr(adapter, "STUFE", None)
    if stage:
        filename = adapter.risikostufe.datei_fuer(filename, stage)
    return str(root / folder / filename)


def _rounds(adapter, trace, rows):
    """Use the house pairer and PnL logic; reject suspicious pairings."""
    quality = []
    warnings = []
    pairing = {}
    rounds = adapter.runden_fuer(trace, rows, stand=pairing)
    if pairing.get("unpaarig") or pairing.get("zweideutig"):
        quality.append("Journal enthält unpaarige oder mehrdeutige Ereignisse")
    if pairing.get("ohne_instrument"):
        quality.append("Ausstiegsereignisse ohne Instrument")
    if pairing.get("offen"):
        warnings.append("Journal-Paarer meldet offene Einstiege")
    return rounds, quality, warnings


def _fee_witness(adapter, trace, rows):
    """Return the known cost treatment; missing fields never become zero fees."""
    if trace == "scanner":
        # runden_spot applies the documented 0.05% each-side charge and stores
        # net proceeds in the journal's amount fields.
        return "journal-netto-scanner"
    if trace == "kraken":
        fee = adapter.gebuehr_fuer(trace)
        # Zero is valid only when an explicit fee field exists in the config.
        folder, filename = adapter._ort(trace, "wachen.json")
        try:
            config = json.loads((adapter.HIER / folder / filename).read_text("utf-8"))
        except (OSError, ValueError):
            return None
        return "journal-netto-kraken" if "gebuehr_taker" in config and fee >= 0 else None
    if trace in ("xperp", "swap"):
        # House rounds retain a per-round cost, but blank source fee/funding
        # cells must not be mistaken for explicitly evidenced zero.
        needed = ("gebuehr_pct", "funding_pct")
        if rows and all(all(str(r.get(k, "")).strip() for k in needed) for r in rows):
            return "rundenkosten-xperp"
    return None


def collect(root: Path, stages=STAGES, adapter=None, traces=None):
    """Collect normalised records; no input file is ever opened for writing."""
    if adapter is None:
        if str(HERE) not in sys.path:
            sys.path.insert(0, str(HERE))
        import auswertung_alle as adapter
    if traces is None:
        traces = active_traces(HERE / "dauerlauf.py")
    records = []
    for stage in stages:
        if stage not in ("niedrig", "mittel", "hoch"):
            raise ValueError("unbekannte Stufe: " + str(stage))
        with _reader_context(adapter, root, stage):
            for trace in traces:
                rows = adapter.zeilen(trace)
                if not rows:
                    records.append(_empty(trace, stage, "Journal fehlt oder ist leer",
                                          _journal_source(adapter, root, trace)))
                    continue
                # Instrument journals are interleaved: BTC entry, ETH entry,
                # BTC exit, ETH exit is one two-round cohort, not four regime
                # changes. First retain each instrument's event stream, then
                # split only when that instrument's own mode/universe changes.
                streams = {}
                for position, row in enumerate(rows):
                    instrument = _value(row, "inst", "paar", "symbol", "token")
                    streams.setdefault(instrument, []).append((position, row))
                segments = []
                for instrument, events in streams.items():
                    current_key = None
                    current = []
                    instrument_segment = 0
                    for position, row in events:
                        key = (instrument, _value(row, "modus", "mode"),
                               _value(row, "universum", "universe"))
                        if current and key != current_key:
                            instrument_segment += 1
                            segments.append((current[0][0], current_key,
                                             instrument_segment,
                                             [event for _, event in current]))
                            current = []
                        current_key = key
                        current.append((position, row))
                    if current:
                        instrument_segment += 1
                        segments.append((current[0][0], current_key,
                                         instrument_segment,
                                         [event for _, event in current]))
                segments.sort(key=lambda item: item[0])
                open_count = adapter.offene_positionen(trace, stage)
                for _, key, instrument_segment, part in segments:
                    instrument, mode, universe = key
                    quality = []
                    if not instrument:
                        quality.append("Instrument fehlt im Journal")
                    if not mode:
                        quality.append("Modus fehlt im Journal")
                    if not universe:
                        quality.append("Universum fehlt im Journal")
                    times = [_timestamp(r.get("zeit")) for r in part]
                    valid_times = [t for t in times if t is not None]
                    if len(valid_times) != len(times):
                        quality.append("Ereigniszeitstempel fehlen oder sind ungültig")
                    rounds, pair_quality, pair_warnings = _rounds(adapter, trace, part)
                    quality.extend(pair_quality)
                    fee_witness = _fee_witness(adapter, trace, part)
                    if fee_witness is None:
                        quality.append("Netto-Kostenbehandlung für dieses Buch nicht belegt")
                    normalized_rounds = []
                    for r in rounds:
                        t = _timestamp(r.get("zeit"))
                        result = r.get("ergebnis")
                        if fee_witness == "journal-netto-scanner" or fee_witness == "journal-netto-kraken":
                            net = result
                            evidenced = result is not None
                        elif fee_witness == "rundenkosten-xperp":
                            # Existing reporting classifies xperp/swap as
                            # journal-net. Do not subtract the diagnostic
                            # `kosten` field a second time.
                            net = result
                            evidenced = result is not None
                        else:
                            net, evidenced = None, False
                        normalized_rounds.append({"ausstieg_zeit": t.isoformat() if t else None,
                                                  "netto": net,
                                                  "kosten_belegt": evidenced})
                    start = min(valid_times).isoformat() if valid_times else None
                    end = max(valid_times).isoformat() if valid_times else None
                    record = {
                        "spur": trace, "stufe": stage,
                        "instrument": instrument, "modus": mode,
                        "universum": universe,
                        "abschnitt": "abschnitt-%03d" % instrument_segment,
                        "einheit": adapter.einheit_fuer(trace),
                        "zeitraum_start": start, "zeitraum_ende": end,
                        "runden": normalized_rounds,
                        "startkapital": None, "startkapital_zeitpunkt": None,
                        "equity_curve": None,
                        "offene_positionen": open_count,
                        "offene_positionen_stand": "Berichtszeitpunkt",
                        "datenqualitaet": sorted(set(quality)),
                        "warnungen": sorted(set(pair_warnings)),
                        "quelle": _journal_source(adapter, root, trace),
                        "kostenbeleg": fee_witness,
                    }
                    records.append(record)
    return records


def _empty(trace, stage, reason, source=None):
    return {"spur": trace, "stufe": stage, "instrument": None, "modus": None,
            "universum": None, "abschnitt": "ohne-journal", "einheit": None,
            "zeitraum_start": None, "zeitraum_ende": None, "runden": [],
            "startkapital": None, "startkapital_zeitpunkt": None,
            "equity_curve": None, "offene_positionen": None,
            "offene_positionen_stand": "Berichtszeitpunkt",
            "datenqualitaet": [reason], "warnungen": [],
            "quelle": source, "kostenbeleg": None}


def _jsonable(value):
    if hasattr(value, "__dict__"):
        return {k: _jsonable(v) for k, v in value.__dict__.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _paths_overlap(first: Path, second: Path) -> bool:
    a, b = first.resolve(), second.resolve()
    try:
        a.relative_to(b)
        return True
    except ValueError:
        pass
    try:
        b.relative_to(a)
        return True
    except ValueError:
        return False


def _report_rows(groups, records):
    """Flatten computed group and book metrics once for both text formats."""
    sources = {}
    for source in records:
        identity = tuple(source.get(key) for key in
                         ("spur", "stufe", "instrument", "modus", "universum", "abschnitt"))
        sources.setdefault(identity, []).append(source)
    rows = []
    for group_index, group in enumerate(groups, 1):
        window_start = group.zeitraum_start.isoformat() if group.zeitraum_start else None
        window_end = group.zeitraum_ende.isoformat() if group.zeitraum_ende else None
        group_key = " / ".join("" if value is None else str(value)
                              for value in group.schluessel)
        for book in group.buecher:
            identity = (book.spur, book.stufe, book.instrument, book.modus,
                        book.universum, book.abschnitt)
            source_items = sources.get(identity, [])
            rows.append({
                "gruppe": group_index,
                "gruppenschluessel": group_key,
                "vergleichbar": group.vergleichbar,
                "gruppen_grund": group.grund,
                "vergleich_start": window_start,
                "vergleich_ende": window_end,
                "spur": book.spur,
                "stufe": book.stufe,
                "instrument": book.instrument,
                "modus": book.modus,
                "universum": book.universum,
                "abschnitt": book.abschnitt,
                "einheit": book.einheit,
                "runden": book.runden,
                "netto_pnl": book.netto_pnl,
                "startkapital": book.startkapital,
                "netto_rendite_pct": book.netto_rendite_pct,
                "offene_positionen": book.offene_positionen,
                "offene_positionen_stand": "Berichtszeitpunkt",
                "drawdown_pct": book.drawdown_pct,
                "drawdown_grund": book.drawdown_grund,
                "rang": book.rang,
                "rang_grund": book.rang_grund,
                "kleine_stichprobe": book.kleine_stichprobe,
                "datenqualitaet": "; ".join(book.datenqualitaet),
                "warnungen": "; ".join(sorted({str(warning)
                                                 for source in source_items
                                                 for warning in source.get("warnungen", [])})),
                "kostenbeleg": "; ".join(sorted({str(s["kostenbeleg"])
                                                   for s in source_items
                                                   if s.get("kostenbeleg")})),
                "quelle": "; ".join(sorted({str(s["quelle"])
                                              for s in source_items if s.get("quelle")})),
            })
    return rows


def write_report(records, output_dir: Path, data_root: Path | None = None):
    """Write JSON, flat CSV, and a compact Markdown report to explicit target."""
    if not output_dir:
        raise ValueError("--output-dir ist erforderlich")
    if data_root is not None and _paths_overlap(output_dir, data_root):
        raise ValueError("--output-dir darf Datenquelle und deren Ordner nicht überlappen")
    output_dir.mkdir(parents=True, exist_ok=True)
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    from vergleich_handelsspuren import vergleiche
    groups = vergleiche(records)
    payload = {"quellen": records, "gruppen": _jsonable(groups),
               "hinweis": "Offene Positionen sind Momentaufnahmen zum Berichtszeitpunkt; fehlendes Kapital, Drawdown, Universum oder Kosten bleiben unbekannt."}
    (output_dir / "handelsspuren-vergleich.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    metric_rows = _report_rows(groups, records)
    columns = tuple(metric_rows[0]) if metric_rows else (
        "gruppe", "gruppenschluessel", "vergleichbar", "gruppen_grund",
        "vergleich_start", "vergleich_ende", "spur", "stufe", "instrument",
        "modus", "universum", "abschnitt", "einheit", "runden", "netto_pnl",
        "startkapital", "netto_rendite_pct", "offene_positionen", "drawdown_pct",
        "drawdown_grund", "rang", "rang_grund", "kleine_stichprobe", "datenqualitaet",
        "offene_positionen_stand", "kostenbeleg", "quelle")
    with (output_dir / "handelsspuren-vergleich.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(metric_rows)
    lines = ["# Handelsspurenvergleich", "",
             "Offene Positionen sind Momentaufnahmen zum Berichtszeitpunkt. Renditeränge entstehen nur bei belegtem gemeinsamem Universum, Kosten und Startkapital.", "",
             "| " + " | ".join(columns) + " |",
             "|" + "|".join("---" for _ in columns) + "|"]
    for item in metric_rows:
        lines.append("| " + " | ".join(
            "" if item[key] is None else str(item[key]).replace("|", "\\|")
            for key in columns) + " |")
    (output_dir / "handelsspuren-vergleich.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return groups


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--daten-root", required=True, type=Path,
                        help="Explizites Wurzelverzeichnis der Handelsspuren")
    parser.add_argument("--output-dir", required=True, type=Path,
                        help="Explizites Ziel für Berichte; Journale bleiben unverändert")
    args = parser.parse_args(argv)
    if not args.daten_root.is_dir():
        parser.error("--daten-root ist kein Verzeichnis")
    records = collect(args.daten_root)
    try:
        groups = write_report(records, args.output_dir, data_root=args.daten_root)
    except ValueError as exc:
        parser.error(str(exc))
    print("Berichte geschrieben: %d Spur/Stufen/Abschnitte; %d Vergleichsgruppen" %
          (len(records), len(groups)))


if __name__ == "__main__":
    main()
