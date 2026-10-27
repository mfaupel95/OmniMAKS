"""Funding im Quant-Urteil: Abzug, Gutschrift, Klemmung, Deckel, Spiegelung."""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import quant                                                  # noqa: E402


def trend(n=260, steigung=0.002, spanne=0.01):
    return [[i * 86400000, c, c * (1 + spanne), c * (1 - spanne), c, 1000.0]
            for i, c in enumerate(100.0 * math.exp(steigung * i) for i in range(n))]


def fall(n=260):
    return [[i * 86400000, c, c * 1.01, c * 0.99, c, 1000.0]
            for i, c in enumerate(100.0 * math.exp(-0.002 * i) for i in range(n))]


class FundingPunkteTest(unittest.TestCase):
    def test_null_aendert_nichts(self):
        self.assertEqual(quant.funding_punkte(0.0), 0.0)

    def test_zahlen_kostet_bis_zum_abzug(self):
        self.assertAlmostEqual(quant.funding_punkte(0.25), -7.5)
        self.assertAlmostEqual(quant.funding_punkte(0.50), -quant.FUNDING_ABZUG)
        self.assertAlmostEqual(quant.funding_punkte(3.0), -quant.FUNDING_ABZUG)  # geklemmt

    def test_bekommen_gibt_weniger_als_zahlen_kostet(self):
        self.assertAlmostEqual(quant.funding_punkte(-0.50), quant.FUNDING_GUTSCHRIFT)
        self.assertAlmostEqual(quant.funding_punkte(-9.0), quant.FUNDING_GUTSCHRIFT)
        self.assertLess(quant.FUNDING_GUTSCHRIFT, quant.FUNDING_ABZUG)


class UrteilFundingTest(unittest.TestCase):
    def test_ohne_funding_unveraendert_und_ohne_felder(self):
        u = quant.urteil(trend(), richtung="long")
        self.assertNotIn("funding_pa", u)
        self.assertNotIn("funding_punkte", u)

    def test_long_zahlt_wird_abgezogen(self):
        k = trend(steigung=0.0015)
        roh = quant.urteil(k, richtung="long")["quant_score"]
        mit = quant.urteil(k, richtung="long", funding_pa=0.50)
        self.assertEqual(mit["funding_punkte"], -quant.FUNDING_ABZUG)
        self.assertAlmostEqual(mit["quant_score"], max(0.0, roh - quant.FUNDING_ABZUG),
                               places=1)

    def test_short_bekommt_bei_positivem_satz(self):
        # positiver Satz: Long zahlt an Short -> der Short BEKOMMT
        k = fall()
        roh = quant.urteil(k, richtung="short")["quant_score"]
        mit = quant.urteil(k, richtung="short", funding_pa=0.50)
        self.assertEqual(mit["funding_punkte"], quant.FUNDING_GUTSCHRIFT)
        self.assertAlmostEqual(mit["quant_score"],
                               min(100.0, roh + quant.FUNDING_GUTSCHRIFT), places=1)

    def test_short_zahlt_bei_negativem_satz(self):
        mit = quant.urteil(fall(), richtung="short", funding_pa=-0.50)
        self.assertEqual(mit["funding_punkte"], -quant.FUNDING_ABZUG)

    def test_score_bleibt_in_0_bis_100(self):
        u = quant.urteil(trend(spanne=0.0001), richtung="long", funding_pa=-5.0)
        self.assertLessEqual(u["quant_score"], 100.0)
        u = quant.urteil(fall(), richtung="long", funding_pa=5.0)
        self.assertGreaterEqual(u["quant_score"], 0.0)

    def test_gutschrift_hebt_eine_spitze_nicht_ueber_den_deckel(self):
        # Rampe am Ende -> weit ueber 6 ATR gedehnt: Deckel 50 gilt auch mit Guthaben.
        basis = trend(n=240, steigung=0.0005)
        c0 = basis[-1][4]
        rampe = [[(240 + j) * 86400000, c, c * 1.01, c * 0.99, c, 1000.0]
                 for j, c in enumerate((c0 * (1.0 + 0.04 * (j + 1)) for j in range(30)))]
        u = quant.urteil(basis + rampe, richtung="long", funding_pa=-5.0)
        self.assertTrue(u["zu_gedehnt"])
        self.assertLessEqual(u["quant_score"], 50.0)


if __name__ == "__main__":
    unittest.main()
