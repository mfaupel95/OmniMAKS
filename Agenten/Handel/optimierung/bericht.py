"""Deterministic, privacy-conscious Markdown reports for optimization cycles."""
from __future__ import annotations

import os
from pathlib import Path
import re
import tempfile
from typing import Iterable

from .ergebnis import Kandidat, Messfenster
from .papierlauf import RegistrierungsBericht
from .zyklus import ZyklusBericht

_SECRET = re.compile(
    r"(?i)\b(api[_-]?key|token|secret|passwort|password|credential)\s*[:=]\s*[^\s,;]+"
)
_PATH = re.compile(r"(?i)(?:[a-z]:[\\/]|/(?:home|Users|mnt|root)/)[^\s,;]+")
_FLAG = re.compile(r"(?<![\w])--[a-z][\w-]*(?:\s+[^\s,;]+)?", re.IGNORECASE)
_CONTROL = re.compile(r"[\x00-\x1f\x7f]")


def _sicher(text: object) -> str:
    """Keep useful prose while removing common secrets, paths and CLI args."""
    value = _CONTROL.sub(" ", str(text)).replace("`", "'").replace("\r", " ").replace("\n", " ")
    value = _SECRET.sub(lambda m: f"{m.group(1)}=[entfernt]", value)
    value = _FLAG.sub("[Argument entfernt]", value)
    value = _PATH.sub("[Pfad entfernt]", value)
    return " ".join(value.split())


def _wert(value: float | int | None, unit: str = "") -> str:
    if value is None:
        return "nicht belegt"
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "ungueltig"
    return f"{value:g}{unit}"


def _fenster(name: str, fenster: Messfenster) -> list[str]:
    def datum(wert):
        return wert.isoformat() if wert is not None else "nicht belegt"

    gebuehren = "vollständig" if fenster.gebuehren_vollstaendig else "unvollständig"
    funding = "vollständig" if fenster.funding_vollstaendig else "unvollständig"
    slippage = "vollständig" if fenster.slippage_vollstaendig else "unvollständig"
    return [
        f"  - {name}: {datum(fenster.start)} bis {datum(fenster.ende)}",
        f"    - Netto: {_wert(fenster.netto_pct, ' %')}; Max. Drawdown: {_wert(fenster.max_drawdown_pct, ' %')}",
        f"    - Geschlossene Runden: {fenster.runden_geschlossen}; gepaarte Runden: {fenster.runden_gepaart}",
        f"    - Gebühren: {gebuehren}; Funding: {funding}; Slippage: {slippage}",
    ]


def _kandidat(k: Kandidat) -> list[str]:
    lines = [f"- `{_sicher(k.kennung)}` — Strategie `{_sicher(k.strategie)}`, Revision `{_sicher(k.revision)}`"]
    lines.extend(_fenster("Papier", k.papier))
    lines.extend(_fenster("Out-of-Sample", k.oos))
    lines.extend(_fenster("Holdout", k.holdout))
    lines.append(f"  - Daten vollständig: {'ja' if k.daten_vollstaendig else 'nein'}; reproduzierbar: {'ja' if k.reproduzierbar else 'nein'}")
    lines.append("  - Aktiviert: nein")
    return lines


def _befunde(titel: str, rows) -> list[str]:
    lines = [f"### {titel}"]
    if not rows:
        return lines + ["- Keine Spuren im Zyklusbericht."]
    for row in rows:
        lines.append(f"- `{_sicher(row.spur)}` — {_sicher(row.status)}: {_sicher(row.grund)}")
    return lines


def render_bericht(zyklus: ZyklusBericht | None, *,
                   registrierung: RegistrierungsBericht | None = None,
                   blockaden: Iterable[str] = (), fehler: BaseException | str | None = None,
                   sicherheitsblockade: str | None = None) -> str:
    """Render a deterministic report; exception messages and detail fields are omitted."""
    if zyklus is not None and not isinstance(zyklus, ZyklusBericht):
        raise TypeError("zyklus muss ZyklusBericht oder None sein")
    if fehler is not None and zyklus is not None:
        raise ValueError("Fehlerbericht darf keinen abgeschlossenen Zyklus enthalten")
    if zyklus is None and fehler is None and sicherheitsblockade is None:
        raise ValueError("ohne Zyklus muss Fehler oder Sicherheitsblockade angegeben sein")

    strategie_n = len(zyklus.strategiekandidaten) if zyklus else 0
    verbesserung_n = len(zyklus.verbesserungskandidaten) if zyklus else 0
    if sicherheitsblockade is not None:
        status = "SICHERHEITSGESPERRT"
    elif fehler is not None:
        status = "FEHLER"
    elif strategie_n + verbesserung_n == 0:
        status = "BESTANDSAUFNAHME"
    else:
        status = "AUSWERTUNG"

    lines = ["# Optimierungslauf", "", f"Status: {status}"]
    if zyklus is not None:
        lines.append(f"Datenstand: {zyklus.datenstand.isoformat()}")
        lines.append(f"Basisrevision: `{_sicher(zyklus.basisrevision) if zyklus.basisrevision else 'nicht ermittelbar'}`")
    if fehler is not None:
        error_type = type(fehler).__name__ if isinstance(fehler, BaseException) else "Laufzeitfehler"
        lines.append(f"Fehlerklasse: `{_sicher(error_type)}`; Meldung aus Sicherheitsgründen ausgelassen.")
    if sicherheitsblockade is not None:
        grund = _sicher(sicherheitsblockade).replace("_", " ")
        lines.append(f"Sicherheitsblockade: {grund[:1].upper() + grund[1:]}")

    if zyklus is not None:
        lines.extend(["", "## Spuren", ""])
        lines.extend(_befunde("Strategieoptimierung", zyklus.strategie))
        lines.append("")
        lines.extend(_befunde("Technische Verbesserung", zyklus.verbesserung))
        lines.extend(["", "## Kandidaten", "",
                      f"Strategie-Kandidaten: {strategie_n}",
                      f"Verbesserungs-Kandidaten: {verbesserung_n}",
                      "Kostenmodell: Netto-Werte werden aus den übergebenen Messfenstern übernommen. Gebühren, Funding und Slippage werden als Vollständigkeitsmerkmale ausgewiesen; hier findet keine Nachberechnung statt."])
        if strategie_n + verbesserung_n == 0:
            lines.append("Es liegen keine gemessenen Kandidaten vor; Discovery allein ist kein Leistungs- oder Promotionbeleg.")
        if zyklus.strategiekandidaten:
            lines.extend(["", "### Strategie-Kandidaten"])
            for candidate in zyklus.strategiekandidaten:
                lines.extend(_kandidat(candidate))
        if zyklus.verbesserungskandidaten:
            lines.extend(["", "### Verbesserungs-Kandidaten"])
            for candidate in zyklus.verbesserungskandidaten:
                lines.extend(_kandidat(candidate))

    reasons = list(zyklus.blockaden) if zyklus is not None else []
    reasons.extend(blockaden)
    if reasons:
        lines.extend(["", "## Datenlücken und Blockaden", ""])
        lines.extend(f"- {_sicher(reason)}" for reason in reasons)
    if registrierung is not None:
        lines.extend(["", "## Papierregistrierung", "",
                      f"Registriert: {'ja' if registrierung.registriert else 'nein'}",
                      f"Aktiviert: {'ja' if registrierung.aktiviert else 'nein'}",
                      f"Grund: {_sicher(registrierung.grund)}"])
        if registrierung.aktiviert:
            lines.append("WARNUNG: Die Registrierung meldet Aktivierung; dies ist keine erwartete Task-3-Ausgabe.")
    if status == "BESTANDSAUFNAHME":
        lines.extend(["", "Hinweis: Ohne gemessene Kandidaten bedeutet dieser Bericht nur eine Bestandsaufnahme, keinen Optimierungserfolg."])
    return "\n".join(lines).rstrip() + "\n"


def schreibe_bericht(zyklus: ZyklusBericht | None, *, ziel: Path, worktree: Path,
                     registrierung: RegistrierungsBericht | None = None,
                     blockaden: Iterable[str] = (), fehler: BaseException | str | None = None,
                     sicherheitsblockade: str | None = None) -> Path:
    """Atomically write to an explicit absolute path inside the caller's worktree."""
    target = Path(ziel)
    root = Path(worktree)
    if not target.is_absolute():
        raise ValueError("Berichtsziel muss ein absoluter, ausdrücklicher Pfad sein")
    try:
        root = root.resolve(strict=True)
        parent = target.parent.resolve(strict=True)
        parent.relative_to(root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError("Berichtsziel muss in einem bestehenden Ordner des Worktrees liegen") from exc
    target = parent / target.name
    if target.is_dir():
        raise ValueError("Berichtsziel muss eine Datei innerhalb des Worktrees sein")
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Berichtsziel existiert bereits: {target.name}")

    content = render_bericht(zyklus, registrierung=registrierung, blockaden=blockaden,
                             fehler=fehler, sicherheitsblockade=sicherheitsblockade)
    fd, temp_name = tempfile.mkstemp(prefix=".bericht-", suffix=".tmp", dir=parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        # Hard-link creation is atomic and fails if another writer created the
        # destination after the preflight check; unlike replace(), it preserves
        # every previous report with the same caller-supplied path.
        os.link(temp, target)
        temp.unlink()
    except BaseException:
        try:
            temp.unlink()
        except OSError:
            pass
        raise
    return target
