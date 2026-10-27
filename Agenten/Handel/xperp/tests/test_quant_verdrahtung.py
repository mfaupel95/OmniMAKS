"""Quant-Urteil + Funding im XPERP-Live-Pfad (26.10.2026).

Ohne Netz: okxf.funding_pa ist ersetzt. Geprueft werden die Modi der
wachen.json (aus / bericht / tor), das Verhalten ohne Urteil, die Funding-
Einrechnung, der Takt in okxf.funding_pa und der Kurztext fuer die Journalspalte.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

SPUR = Path(__file__).resolve().parents[1]
HANDEL = SPUR.parents[0]
for p in (HANDEL / "scanner", HANDEL, SPUR):
    if str(p) in sys.path:
        sys.path.remove(str(p))
    sys.path.insert(0, str(p))

import handeln as h                                                 # noqa: E402
import okxf                                                         # noqa: E402
import quant_urteil as qu                                           # noqa: E402

WACHEN = json.loads((SPUR / "wachen.json").read_text(encoding="utf-8"))


def roh(score, gedehnt=False, dehnung=2.0):
    return {"quant_score": score, "zu_gedehnt": gedehnt, "dehnung_atr": dehnung,
            "ordnung": 4}


def wert(basis="BTC", long_=None, short=None, kat="krypto"):
    return {"basis": basis, "instId": basis + "-USD_UM_XPERP-X", "kategorie": kat,
            "punkte": {"long": 80.0, "short": 60.0}, "vola": 0.5,
            "vola_tor": 1.2, "umsatz": 9e9, "mae_long": 0.01, "mae_short": 0.01,
            "quant": {"long": long_, "short": short}}


def w_mit(modus, **extra):
    w = dict(WACHEN)
    w["quant"] = dict({"modus": modus, "mindest_score": 60,
                       "dehnung_max_atr": 6.0, "ohne_urteil": "zulassen"}, **extra)
    return w


class KonfigTest(unittest.TestCase):
    def test_standard_in_wachen_json_ist_bericht(self):
        self.assertEqual(qu.konfig(WACHEN)["modus"], "bericht")

    def test_ohne_block_ist_aus(self):
        self.assertEqual(qu.konfig({})["modus"], "aus")

    def test_unbekannter_modus_wird_aus_mit_fehler(self):
        k = qu.konfig({"quant": {"modus": "scharf"}})
        self.assertEqual(k["modus"], "aus")
        self.assertIn("scharf", k["fehler"])


class KandidatenTest(unittest.TestCase):
    def setUp(self):
        patch = mock.patch.object(okxf, "funding_pa", return_value=0.0)
        patch.start()
        self.addCleanup(patch.stop)

    def _lauf(self, modus, werte, **extra):
        return h.kandidaten(werte, w_mit(modus, **extra))

    @staticmethod
    def _seite(kand, seite):
        return [x for x in kand if x["seite"] == seite]

    def test_aus_aendert_nichts_und_haengt_nichts_an(self):
        with mock.patch.object(okxf, "funding_pa") as f:
            k = self._lauf("aus", [wert(long_=roh(10.0))])
        self.assertTrue(k)
        self.assertTrue(all("quant" not in x for x in k))
        f.assert_not_called()

    def test_bericht_haengt_an_sperrt_aber_nicht(self):
        k = self._lauf("bericht", [wert(long_=roh(10.0, dehnung=9.0, gedehnt=True))])
        long_ = self._seite(k, "long")
        self.assertEqual(len(long_), 1)
        self.assertEqual(long_[0]["quant"]["score"], 10.0)

    def test_tor_sperrt_unter_mindest_score(self):
        k = self._lauf("tor", [wert(long_=roh(40.0))])
        self.assertEqual(self._seite(k, "long"), [])

    def test_tor_laesst_ueber_mindest_score_durch(self):
        k = self._lauf("tor", [wert(long_=roh(75.0))])
        self.assertEqual(len(self._seite(k, "long")), 1)

    def test_tor_sperrt_gedehnt_trotz_hohem_score(self):
        k = self._lauf("tor", [wert(long_=roh(75.0, gedehnt=True, dehnung=7.0))])
        self.assertEqual(self._seite(k, "long"), [])

    def test_tor_ohne_urteil_zulassen_ist_standard(self):
        k = self._lauf("tor", [wert(long_=None)])
        self.assertEqual(len(self._seite(k, "long")), 1)

    def test_tor_ohne_urteil_sperren(self):
        k = self._lauf("tor", [wert(long_=None)], ohne_urteil="sperren")
        self.assertEqual(self._seite(k, "long"), [])

    def test_alte_rangliste_ohne_quant_schluessel_bricht_nicht(self):
        x = wert()
        del x["quant"]
        k = self._lauf("tor", [x])
        self.assertTrue(k)

    def test_funding_zieht_ab_und_kippt_das_tor(self):
        # Score 65 klar ueber 60; Long zahlt 50 %/a -> -15 -> 50 -> gesperrt
        with mock.patch.object(okxf, "funding_pa", return_value=0.50):
            k = self._lauf("tor", [wert(long_=roh(65.0))])
        self.assertEqual(self._seite(k, "long"), [])

    def test_funding_ausfall_rechnet_ohne_funding(self):
        with mock.patch.object(okxf, "funding_pa", side_effect=RuntimeError("netz")):
            k = self._lauf("bericht", [wert(long_=roh(65.0))])
        q = self._seite(k, "long")[0]["quant"]
        self.assertEqual(q["score"], 65.0)
        self.assertIsNone(q["funding_pa"])

    def test_short_bekommt_bei_positivem_satz_gutschrift(self):
        with mock.patch.object(okxf, "funding_pa", return_value=0.50):
            k = self._lauf("bericht", [wert(short=roh(60.0))])
        q = self._seite(k, "short")[0]["quant"]
        self.assertEqual(q["score"], 65.0)
        self.assertEqual(q["funding_punkte"], 5.0)


class TextTest(unittest.TestCase):
    def test_text_ohne_urteil(self):
        self.assertEqual(qu.text(None), "quant n/a")

    def test_text_mit_funding(self):
        t = qu.text({"score": 61.5, "funding_pa": -0.12, "funding_punkte": 3.0,
                     "zu_gedehnt": False})
        self.assertIn("quant 61.5", t)
        self.assertIn("-12.0%/a", t)


class FundingPaTest(unittest.TestCase):
    @staticmethod
    def _antwort(satz, ft, nft):
        return [{"fundingRate": satz, "fundingTime": str(ft), "nextFundingTime": str(nft)}]

    def test_acht_stunden_takt(self):
        with mock.patch.object(okxf, "_mit_wiederholung",
                               return_value=self._antwort("0.0001", 0, 8 * 3600000)):
            self.assertAlmostEqual(okxf.funding_pa("X"), 0.0001 * 1095)

    def test_vier_stunden_takt_verdoppelt_die_jahresrate(self):
        with mock.patch.object(okxf, "_mit_wiederholung",
                               return_value=self._antwort("0.0001", 0, 4 * 3600000)):
            self.assertAlmostEqual(okxf.funding_pa("X"), 0.0001 * 2190)

    def test_nicht_lesbar_ist_none(self):
        with mock.patch.object(okxf, "_mit_wiederholung", return_value=[]):
            self.assertIsNone(okxf.funding_pa("X"))
        with mock.patch.object(okxf, "_mit_wiederholung",
                               return_value=self._antwort("0.0001", 5, 5)):
            self.assertIsNone(okxf.funding_pa("X"))


if __name__ == "__main__":
    unittest.main()
