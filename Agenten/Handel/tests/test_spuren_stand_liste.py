"""AST-basierte Extraktion der Spurenliste aus dauerlauf.py."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import spuren_stand  # noqa: E402


class SpurenlisteTest(unittest.TestCase):
    def test_liest_nur_top_level_spuren_und_auto_freigabe(self):
        quelle = '''
# SPUREN = {"kommentar": {"geschweifte": "}"}}
SPUREN = {
    "alpha": {"skript": "{ nicht die Struktur"},
    "beta": {"ordner": "beta"},
}
AUTO_FREIGABE = ("beta",)
'''
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "dauerlauf.py").write_text(quelle, encoding="utf-8")
            with patch.object(spuren_stand, "HIER", Path(tmp)):
                self.assertEqual((['alpha', 'beta'], ['beta']),
                                 spuren_stand.spurenliste())

    def test_liest_literal_auto_freigabe_als_liste(self):
        quelle = 'SPUREN = {"alpha": {}}\nAUTO_FREIGABE = ("alpha",)\n'
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "dauerlauf.py").write_text(quelle, encoding="utf-8")
            with patch.object(spuren_stand, "HIER", Path(tmp)):
                self.assertEqual((['alpha'], ['alpha']), spuren_stand.spurenliste())


if __name__ == "__main__":
    unittest.main()
