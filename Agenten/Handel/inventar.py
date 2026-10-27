"""Read-only metadata inventory for downloads and recent project work."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Sequence
import subprocess


@dataclass(frozen=True)
class InventarEintrag:
    typ: str
    name: str
    pfad: str
    projekt: str = ""
    status: str = "unbekannt"
    modus: str = "Unbekannt"
    aktualisiert: str = ""
    quelle: str = ""
    hinweise: tuple[str, ...] = ()


def _zeit(stamp: float) -> str:
    return datetime.fromtimestamp(stamp, timezone.utc).astimezone().isoformat(timespec="seconds")


def sammle_downloads(wurzel: Path) -> list[InventarEintrag]:
    """List files and directories using stat metadata only; retain errors."""
    wurzel = Path(wurzel)
    if not wurzel.exists():
        return [InventarEintrag("fehler", wurzel.name or str(wurzel), str(wurzel),
                                status="unbekannt", quelle="Downloads",
                                hinweise=("Downloads-Ordner fehlt",))]
    result: list[InventarEintrag] = []
    try:
        paths = list(wurzel.rglob("*"))
    except OSError as exc:
        return [InventarEintrag("fehler", wurzel.name, str(wurzel), quelle="Downloads",
                                hinweise=(f"Scanfehler: {type(exc).__name__}",))]
    for path in paths:
        try:
            st = path.stat()
            result.append(InventarEintrag("verzeichnis" if path.is_dir() else "download",
                         path.name, str(path), status="vorhanden", aktualisiert=_zeit(st.st_mtime),
                         quelle="Downloads", hinweise=(f"{st.st_size} Bytes",) if path.is_file() else ()))
        except (OSError, UnicodeError) as exc:
            result.append(InventarEintrag("fehler", str(path.name), str(path), quelle="Downloads",
                                         hinweise=(f"Metadatenfehler: {type(exc).__name__}",)))
    return result


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                               check=True, text=True, encoding="utf-8", errors="replace")
    return completed.stdout


def parse_git_worktrees(text: str) -> list[InventarEintrag]:
    result = []
    block: dict[str, str] = {}
    def flush():
        if not block.get("worktree"):
            return
        path = block["worktree"]
        hints = tuple(k for k in ("bare" if "bare" in block else "", "locked" if "locked" in block else "") if k)
        result.append(InventarEintrag("worktree", Path(path).name, path,
                     status="registriert",
                     modus="Unbekannt", quelle="git worktree list",
                     hinweise=hints + (("HEAD " + block["HEAD"][:12],) if block.get("HEAD") else ())
                     + (("Branch " + block["branch"],) if block.get("branch") else ())))
    for line in text.splitlines() + [""]:
        if not line:
            flush(); block = {}; continue
        key, _, value = line.partition(" ")
        block[key] = value
    return result


def parse_git_status(text: str, wurzel: Path) -> list[InventarEintrag]:
    """Parse porcelain v1 NUL records without opening the referenced paths."""
    records = text.split("\0")
    out = []
    i = 0
    while i < len(records):
        rec = records[i]; i += 1
        if not rec:
            continue
        if len(rec) < 4:
            continue
        status, path = rec[:2], rec[3:]
        if "R" in status or "C" in status:
            if i < len(records):
                i += 1  # -z emits destination first, source second; list destination only.
        out.append(InventarEintrag("projektpfad", Path(path).name or path, str(Path(wurzel) / path),
                    projekt=str(wurzel), status="untracked" if status == "??" else "geändert",
                    aktualisiert=datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
                    quelle="git status --porcelain -z", hinweise=(status,)))
    return out


def finde_projektwurzeln(roots: Sequence[Path]) -> list[Path]:
    """Find nearby repositories, then add registered external Git worktrees."""
    found: set[Path] = set()
    for root in map(Path, roots):
        if not root.exists():
            continue
        if (root / ".git").exists():
            found.add(root.resolve())
        try:
            for child in root.iterdir():
                if child.is_dir() and (child / ".git").exists():
                    found.add(child.resolve())
        except OSError:
            continue
    # Git metadata includes external linked worktrees and does not recurse content trees.
    for root in tuple(found):
        try:
            for entry in parse_git_worktrees(_git(root, "worktree", "list", "--porcelain")):
                p = Path(entry.pfad)
                if p.exists():
                    found.add(p.resolve())
        except (OSError, subprocess.SubprocessError):
            pass
    return sorted(found, key=lambda p: str(p).casefold())


def sammle_projektstatus(roots: Sequence[Path], *, seit: datetime) -> list[InventarEintrag]:
    result = []
    for root in finde_projektwurzeln(roots):
        try:
            result.extend(parse_git_status(_git(root, "status", "--porcelain", "-z"), root))
            log = _git(root, "log", "--since=90.days", "--name-only", "-z", "--format=%ct")
            parts = log.split("\0")
            stamp = None
            for part in parts:
                if part.isdigit():
                    stamp = int(part)
                elif part and stamp is not None:
                    # With git -z --format=%ct, Git separates the commit
                    # header from the first pathname with one newline.
                    part = part[1:] if part.startswith("\n") else part
                    updated = datetime.fromtimestamp(stamp, timezone.utc)
                    if updated >= seit.astimezone(timezone.utc):
                        result.append(InventarEintrag("commitpfad", Path(part).name,
                            str(root / part), projekt=str(root), status="zuletzt bearbeitet",
                            aktualisiert=_zeit(stamp), quelle="git log --since=90.days"))
        except (OSError, subprocess.SubprocessError) as exc:
            result.append(InventarEintrag("fehler", root.name, str(root), projekt=str(root),
                           quelle="Git", hinweise=(f"Git-Quelle nicht lesbar: {type(exc).__name__}",)))
    return result
