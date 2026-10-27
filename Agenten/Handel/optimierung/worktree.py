"""Erstellt reversible, isolierte Experiment-Worktrees."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess


class WorktreeFehler(RuntimeError):
    """Worktree konnte ohne Eingriff in bestehende Dateien nicht angelegt werden."""


@dataclass(frozen=True)
class Experiment:
    kennung: str
    repo: Path
    pfad: Path
    branch: str
    basis: str


def _git(repo: Path, *args: str) -> str:
    try:
        result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                                text=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise WorktreeFehler(f"git-Aufruf fehlgeschlagen: {type(exc).__name__}") from exc
    if result.returncode:
        raise WorktreeFehler((result.stderr or "git-Aufruf fehlgeschlagen").strip())
    return result.stdout.strip()


def _status(repo: Path) -> str:
    return _git(repo, "status", "--porcelain=v1", "--untracked-files=all")


def lege_experiment_an(repo: Path, *, kennung: str, basis: str) -> Experiment:
    """Legt einen neuen Branch als sibling-Worktree an; nie kopiert User-Diffs."""
    repo = Path(repo).resolve(strict=True)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", kennung):
        raise ValueError("kennung muss 1-64 sichere ASCII-Zeichen enthalten")
    top = Path(_git(repo, "rev-parse", "--show-toplevel")).resolve(strict=True)
    if top != repo:
        raise WorktreeFehler("repo muss exakt die Git-Wurzel sein")
    commit = _git(repo, "rev-parse", "--verify", f"{basis}^{{commit}}")
    branch = f"optimierung/{kennung}"
    branch_exists = subprocess.run(["git", "-C", str(repo), "show-ref", "--verify", "--quiet",
                                    f"refs/heads/{branch}"], capture_output=True, check=False)
    if branch_exists.returncode == 0:
        raise WorktreeFehler(f"Branch existiert bereits: {branch}")
    if branch_exists.returncode != 1:
        raise WorktreeFehler("Branch-Existenz konnte nicht sicher geprüft werden")

    pfad = (repo.parent / f"{repo.name}-experimente" / kennung).resolve()
    if pfad == repo or repo in pfad.parents or pfad.exists():
        raise WorktreeFehler(f"Experimentpfad ist belegt oder nicht isoliert: {pfad}")
    status_vorher = _status(repo)
    _git(repo, "worktree", "add", "--quiet", "-b", branch, str(pfad), commit)
    # Git worktree add is the only mutation; confirm it did not alter user files.
    if _status(repo) != status_vorher:
        raise WorktreeFehler("Quellarbeitsbaum änderte sich während der Anlage; Worktree bleibt erhalten")
    if Path(_git(pfad, "rev-parse", "--show-toplevel")).resolve() != pfad:
        raise WorktreeFehler("angelegter Checkout hat unerwartete Git-Wurzel")
    if _git(pfad, "branch", "--show-current") != branch:
        raise WorktreeFehler("angelegter Checkout hat unerwarteten Branch")
    return Experiment(kennung, repo, pfad, branch, commit)
