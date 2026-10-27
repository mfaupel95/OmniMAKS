"""Grenzfaelle der fail-closed Papierpromotion."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from optimierung import Kandidat, Messfenster, bewerte_kandidat

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def fenster(net, *, offset=0, dd=5, runden=20, gepaart=None, kosten=True):
    start = T0 + timedelta(days=offset)
    return Messfenster(start, start + timedelta(days=30), net, dd, runden,
                       runden if gepaart is None else gepaart,
                       kosten, kosten, kosten)


def kandidat(id, rev, paper, oos, holdout, *, komplett=True, reproduzierbar=True):
    return Kandidat(id, "grid", rev, paper, oos, holdout, komplett, reproduzierbar)


class PromotionGates(unittest.TestCase):
    def setUp(self):
        self.regeln = {"min_runden": 20, "max_drawdown_pct": 10}
        self.basis = kandidat("basis", "a1", fenster(2), fenster(1, offset=31),
                              fenster(1, offset=62))
        self.kandidat = kandidat("neu", "b2", fenster(3), fenster(2, offset=31),
                                 fenster(2, offset=62))

    def pruefe(self, **kw):
        return bewerte_kandidat(kw.get("kandidat", self.kandidat),
                                kw.get("basis", self.basis), kw.get("regeln", self.regeln))

    def test_solider_kandidat_besteht(self):
        self.assertTrue(self.pruefe().promotion_erlaubt)
        self.assertEqual((), self.pruefe().gruende)

    def test_oos_und_holdout_duerfen_trainingsdaten_nicht_wiederverwenden(self):
        k = kandidat("neu", "b2", fenster(3), fenster(2), fenster(2, offset=62))
        g = self.pruefe(kandidat=k)
        self.assertFalse(g.promotion_erlaubt)
        self.assertIn("kandidat_papier_oos_zeitfenster_nicht_disjunkt", g.gruende)

    def test_basisfenster_muessen_ebenfalls_disjunkt_sein(self):
        basis = kandidat("basis", "a1", fenster(2), fenster(1),
                         fenster(1, offset=62))
        g = self.pruefe(basis=basis)
        self.assertFalse(g.promotion_erlaubt)
        self.assertIn("basis_papier_oos_zeitfenster_nicht_disjunkt", g.gruende)

    def test_kandidat_und_basis_muessen_dieselben_vergleichszeitraeume_nutzen(self):
        k = kandidat("neu", "b2", fenster(3, offset=1),
                     fenster(2, offset=32), fenster(2, offset=63))
        g = self.pruefe(kandidat=k)
        self.assertFalse(g.promotion_erlaubt)
        self.assertIn("papier_basis_zeitfenster_abweichend", g.gruende)

    def test_zu_wenige_abgeschlossene_papier_runden_blockieren(self):
        k = kandidat("neu", "b2", fenster(3, runden=19), fenster(2), fenster(2))
        self.assertIn("papier_zu_wenig_runden", self.pruefe(kandidat=k).gruende)

    def test_oos_und_holdout_muessen_messbar_sein(self):
        k = kandidat("neu", "b2", fenster(3), fenster(None), fenster(2))
        g = self.pruefe(kandidat=k)
        self.assertFalse(g.promotion_erlaubt)
        self.assertIn("oos_netto_fehlt", g.gruende)

    def test_fehlerhafte_oder_ungepaarte_journale_sind_nicht_auswertbar(self):
        k = kandidat("neu", "b2", fenster(3, gepaart=19), fenster(2), fenster(2))
        g = self.pruefe(kandidat=k)
        self.assertFalse(g.promotion_erlaubt)
        self.assertIn("papier_runden_unvollstaendig_oder_ungepaart", g.gruende)

    def test_gebuehren_funding_und_slippage_muessen_vollstaendig_sein(self):
        k = kandidat("neu", "b2", fenster(3, kosten=False), fenster(2), fenster(2))
        g = self.pruefe(kandidat=k)
        self.assertFalse(g.promotion_erlaubt)
        self.assertTrue({"papier_gebuehren_unvollstaendig", "papier_funding_unvollstaendig",
                         "papier_slippage_unvollstaendig"}.issubset(g.gruende))

    def test_fehlende_gesamt_daten_blockieren(self):
        k = kandidat("neu", "b2", fenster(3), fenster(2), fenster(2), komplett=False)
        self.assertIn("daten_unvollstaendig", self.pruefe(kandidat=k).gruende)

    def test_drawdown_deckel_wird_geprueft(self):
        k = kandidat("neu", "b2", fenster(3, dd=10.01), fenster(2), fenster(2))
        self.assertIn("papier_drawdown_deckel_verletzt", self.pruefe(kandidat=k).gruende)

    def test_verbesserung_muss_in_papier_oos_und_holdout_stabil_sein(self):
        k = kandidat("neu", "b2", fenster(3), fenster(1), fenster(2))
        self.assertIn("oos_keine_verbesserung_gegen_basis", self.pruefe(kandidat=k).gruende)

    def test_gleichstand_ist_keine_verbesserung(self):
        k = kandidat("neu", "b2", fenster(3), fenster(2), fenster(1))
        g = self.pruefe(kandidat=k)
        self.assertFalse(g.promotion_erlaubt)
        self.assertIn("holdout_keine_verbesserung_gegen_basis", g.gruende)

    def test_fehlende_regeln_blockieren(self):
        g = self.pruefe(regeln={})
        self.assertFalse(g.promotion_erlaubt)
        self.assertIn("regel_min_runden_fehlt_oder_ungueltig", g.gruende)

    def test_unbekannte_kennzahlen_und_nicht_finite_werte_blockieren(self):
        k = kandidat("neu", "b2", fenster(float("nan")), fenster(2), fenster(2))
        self.assertIn("papier_netto_fehlt", self.pruefe(kandidat=k).gruende)

    def test_bool_ist_keine_gueltige_rundenzahl(self):
        k = kandidat("neu", "b2", fenster(3, runden=True, gepaart=True), fenster(2), fenster(2))
        g = self.pruefe(kandidat=k)
        self.assertIn("papier_zu_wenig_runden", g.gruende)
        self.assertIn("papier_runden_unvollstaendig_oder_ungepaart", g.gruende)

    def test_falsches_messfenster_objekt_blockiert_ohne_exception(self):
        k = kandidat("neu", "b2", object(), fenster(2), fenster(2))
        g = self.pruefe(kandidat=k)
        self.assertFalse(g.promotion_erlaubt)
        self.assertIn("papier_messfenster_ungueltig", g.gruende)

    def test_ungueltiger_drawdown_deckel_erzeugt_keine_verletzungsdiagnose(self):
        g = self.pruefe(regeln={"min_runden": 20, "max_drawdown_pct": None})
        self.assertIn("regel_drawdown_deckel_fehlt_oder_ungueltig", g.gruende)
        self.assertFalse(any("drawdown_deckel_verletzt" in code for code in g.gruende))

    def test_ungueltiger_kandidat_blockiert_mit_grund(self):
        g = bewerte_kandidat(object(), self.basis, self.regeln)
        self.assertFalse(g.promotion_erlaubt)
        self.assertEqual(("kandidat_eingabe_ungueltig",), g.gruende)

    def test_ungueltige_basis_blockiert_mit_grund(self):
        g = bewerte_kandidat(self.kandidat, object(), self.regeln)
        self.assertFalse(g.promotion_erlaubt)
        self.assertEqual(("basis_eingabe_ungueltig",), g.gruende)

    def test_ergebnis_ist_unveraenderlich(self):
        g = self.pruefe()
        with self.assertRaises(AttributeError):
            g.promotion_erlaubt = False


if __name__ == "__main__":
    unittest.main()
