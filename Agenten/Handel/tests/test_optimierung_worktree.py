"""Worktree-Fehler bleiben auf temporäre Repositories begrenzt."""
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

HANDEL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HANDEL))
from optimierung.worktree import WorktreeFehler, lege_experiment_an


def git(path, *args):
    return subprocess.run(["git", "-C", str(path), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


class WorktreeIsolation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "--quiet", str(self.repo)], check=True)
        git(self.repo, "config", "user.name", "Unit Test")
        git(self.repo, "config", "user.email", "unit@example.invalid")
        (self.repo / "code.txt").write_text("base", encoding="utf-8")
        git(self.repo, "add", "code.txt")
        git(self.repo, "commit", "--quiet", "-m", "base")
        self.base = git(self.repo, "rev-parse", "HEAD")

    def test_erstellt_eigenen_branch_und_sibling_worktree(self):
        exp = lege_experiment_an(self.repo, kennung="test-1", basis=self.base)
        self.assertEqual(exp.branch, git(exp.pfad, "branch", "--show-current"))
        self.assertEqual(self.base, git(exp.pfad, "rev-parse", "HEAD"))
        self.assertNotEqual(exp.repo, exp.pfad)

    def test_dreckige_quelle_bleibt_unveraendert_und_diff_wird_nicht_kopiert(self):
        (self.repo / "foreign.txt").write_text("other session", encoding="utf-8")
        status_before = git(self.repo, "status", "--porcelain")
        exp = lege_experiment_an(self.repo, kennung="clean-base", basis=self.base)
        self.assertEqual(status_before, git(self.repo, "status", "--porcelain"))
        self.assertFalse((exp.pfad / "foreign.txt").exists())

    def test_branch_oder_zielkollision_blockiert_vor_aenderung(self):
        exp = lege_experiment_an(self.repo, kennung="once", basis=self.base)
        with self.assertRaises(WorktreeFehler):
            lege_experiment_an(self.repo, kennung="once", basis=self.base)
        self.assertEqual(self.base, git(self.repo, "rev-parse", "HEAD"))
        self.assertEqual(exp.branch, git(exp.pfad, "branch", "--show-current"))

    def test_ungueltiger_basis_blockiert(self):
        before = git(self.repo, "status", "--porcelain")
        with self.assertRaises(WorktreeFehler):
            lege_experiment_an(self.repo, kennung="bad-base", basis="not-a-revision")
        self.assertEqual(before, git(self.repo, "status", "--porcelain"))


if __name__ == "__main__":
    unittest.main()
