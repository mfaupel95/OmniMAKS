import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

HANDEL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HANDEL))
import inventar


class InventarTests(unittest.TestCase):
    def test_download_missing_and_empty_are_distinct(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "missing"
            self.assertIn("fehlt", inventar.sammle_downloads(root)[0].hinweise[0])
            root.mkdir()
            self.assertEqual(inventar.sammle_downloads(root), [])

    def test_downloads_nested_unicode_metadata_only(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); target = root / "Ordner" / "Überblick.txt"
            target.parent.mkdir(); target.write_text("secret content", encoding="utf-8")
            with mock.patch.object(Path, "open", side_effect=AssertionError("content opened")):
                rows = inventar.sammle_downloads(root)
            self.assertTrue(any(r.name == "Überblick.txt" for r in rows))

    def test_worktrees_and_porcelain_paths(self):
        rows = inventar.parse_git_worktrees("worktree C:/repo\nHEAD abcdef012345\nbranch refs/heads/main\n\nworktree D:/external\nHEAD 123456789012\ndetached\n")
        self.assertEqual([r.pfad for r in rows], ["C:/repo", "D:/external"])
        dirty = inventar.parse_git_status(" M src/a.py\0 M path with spaces.txt\0?? ü.txt\0R  new.txt\0old.txt\0", Path("C:/repo"))
        self.assertEqual([r.name for r in dirty], ["a.py", "path with spaces.txt", "ü.txt", "new.txt"])
        self.assertEqual(dirty[2].status, "untracked")

    def test_discovers_roots_in_multiple_operational_roots_and_external_worktree(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d); a=base/"a"; b=base/"b"; a.mkdir(); b.mkdir()
            repo=a/"repo"; repo.mkdir(); (repo/".git").mkdir()
            ext=base/"external"; ext.mkdir()
            with mock.patch.object(inventar, "_git", return_value=f"worktree {ext}\nHEAD deadbeef\nbranch refs/heads/x\n"):
                found=inventar.finde_projektwurzeln([a,b])
            self.assertEqual(set(found), {repo.resolve(), ext.resolve()})

    def test_current_git_paths_and_recent_commit_files_are_metadata_only(self):
        root = Path("C:/repo")
        git_log = "2000000000\0\nsrc/über file.py\0zweig/datei.txt\0"
        git_log += "2000000001\0\nother/ü.txt\0"
        with mock.patch.object(inventar, "finde_projektwurzeln", return_value=[root]), \
             mock.patch.object(inventar, "_git", side_effect=["?? safe.txt\0", git_log]):
            rows = inventar.sammle_projektstatus([root], seit=datetime(2000, 1, 1, tzinfo=timezone.utc))
        self.assertEqual({r.name for r in rows}, {"safe.txt", "über file.py", "datei.txt", "ü.txt"})


if __name__ == "__main__":
    unittest.main()
