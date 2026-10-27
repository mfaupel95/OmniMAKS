import os
import sys
import unittest
from datetime import datetime, timezone

HANDEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HANDEL not in sys.path:
    sys.path.insert(0, HANDEL)

from vergleich_handelsspuren import vergleiche  # noqa: E402


START = "2026-10-01T00:00:00+00:00"
ENDE = "2026-10-04T00:00:00+00:00"


def quelle(spur, stufe, *, instrument="BTC-USDC", modus="papier",
           universum="spot-top20", abschnitt="a", start=START, ende=ENDE,
           startkapital=100.0, capital_at=START, pnl=10.0, open_count=1,
           curve=None, rounds=None, quality=None):
    if rounds is None:
        rounds = [{"ausstieg_zeit": "2026-10-02T00:00:00+00:00",
                   "netto": pnl, "kosten_belegt": True}]
    if curve is None:
        base = 100.0 if startkapital is None else float(startkapital)
        curve = [{"zeit": start, "wert": base},
                 {"zeit": "2026-10-02T00:00:00+00:00", "wert": base + 10.0},
                 {"zeit": ende, "wert": base + 5.0}]
    return {"spur": spur, "stufe": stufe, "instrument": instrument,
            "modus": modus, "universum": universum, "abschnitt": abschnitt,
            "einheit": "USDC", "zeitraum_start": start, "zeitraum_ende": ende,
            "runden": rounds, "startkapital": startkapital,
            "startkapital_zeitpunkt": capital_at, "equity_curve": curve,
            "offene_positionen": open_count,
            "datenqualitaet": quality or []}


class VergleichTests(unittest.TestCase):
    def test_netto_rendite_nutzt_belegtes_startkapital_nicht_einsatz(self):
        a = quelle("a", "niedrig", pnl=20.0, startkapital=200.0)
        a["runden"][0]["einsatz"] = 10.0
        gruppe = vergleiche([a, quelle("b", "mittel", pnl=10.0)])[0]
        self.assertEqual(gruppe.buecher[0].netto_rendite_pct, 10.0)
        self.assertEqual(gruppe.buecher[0].netto_pnl, 20.0)

    def test_fehlendes_startkapital_bleibt_ohne_rangzahl(self):
        gruppe = vergleiche([quelle("a", "niedrig", startkapital=None),
                             quelle("b", "mittel")])[0]
        a = next(b for b in gruppe.buecher if b.spur == "a")
        self.assertIsNone(a.netto_rendite_pct)
        self.assertIsNone(a.rang)
        self.assertTrue(any("Startkapital" in x for x in a.datenqualitaet))

    def test_unbekannter_offener_bestand_blockiert_realisierten_roi_nicht(self):
        rows = [quelle("a", "niedrig", open_count=None,
                       quality=["offene Positionen nicht belegt"]),
                quelle("b", "mittel")]
        book = next(b for b in vergleiche(rows)[0].buecher if b.spur == "a")
        self.assertIsNone(book.offene_positionen)
        self.assertIn("offene Positionen nicht belegt", book.datenqualitaet)
        self.assertIsNotNone(book.netto_rendite_pct)
        self.assertIsNotNone(book.rang)

    def test_startkapital_muss_mit_kurve_am_fensterbeginn_uebereinstimmen(self):
        a = quelle("a", "niedrig", startkapital=200.0,
                   curve=[{"zeit": START, "wert": 100.0},
                          {"zeit": "2026-10-02T00:00:00+00:00", "wert": 110.0},
                          {"zeit": ENDE, "wert": 105.0}])
        group = vergleiche([a, quelle("b", "mittel")])[0]
        book = next(b for b in group.buecher if b.spur == "a")
        self.assertIn("Startkapital stimmt nicht", book.datenqualitaet[0])
        self.assertIsNone(book.rang)

    def test_kosten_nur_wenn_belegt_und_netto_fehlt_bleibt_unbekannt(self):
        rounds = [{"ausstieg_zeit": "2026-10-02T00:00:00+00:00",
                   "netto": 5.0, "kosten_belegt": True},
                  {"ausstieg_zeit": "2026-10-03T00:00:00+00:00",
                   "netto": None, "kosten_belegt": False}]
        gruppe = vergleiche([quelle("a", "niedrig", rounds=rounds),
                             quelle("b", "mittel")])[0]
        book = next(b for b in gruppe.buecher if b.spur == "a")
        self.assertEqual(book.runden, 2)
        self.assertIsNone(book.netto_pnl)
        self.assertIsNone(book.rang)
        self.assertIn("Netto/Kosten einer Runde nicht vollständig belegt", book.datenqualitaet)

    def test_modus_instrument_universum_abschnitt_und_einheit_trennen(self):
        rows = [quelle("a", "niedrig"),
                quelle("b", "mittel", modus="live"),
                quelle("c", "hoch", instrument="ETH-USDC"),
                quelle("d", "niedrig", universum="all"),
                quelle("e", "mittel", abschnitt="wechsel-1"),
                quelle("f", "hoch")]
        rows[-1]["einheit"] = "USD"
        groups = vergleiche(rows)
        self.assertEqual(len(groups), len(rows))
        self.assertTrue(all(not g.vergleichbar for g in groups))

    def test_laengster_gemeinsamer_zeitraum_und_rundenfenster(self):
        a = quelle("a", "niedrig", rounds=[
            {"ausstieg_zeit": "2026-10-01T12:00:00+00:00", "netto": 1.0, "kosten_belegt": True},
            {"ausstieg_zeit": "2026-10-02T12:00:00+00:00", "netto": 2.0, "kosten_belegt": True},
            {"ausstieg_zeit": "2026-10-04T00:00:00+00:00", "netto": 4.0, "kosten_belegt": True}])
        b = quelle("b", "mittel", start="2026-10-02T00:00:00+00:00",
                   ende="2026-10-03T00:00:00+00:00", rounds=[
                       {"ausstieg_zeit": "2026-10-02T12:00:00+00:00", "netto": 3.0, "kosten_belegt": True}])
        group = vergleiche([a, b])[0]
        self.assertEqual(group.zeitraum_start, datetime(2026, 10, 2, tzinfo=timezone.utc))
        self.assertEqual(group.zeitraum_ende, datetime(2026, 10, 3, tzinfo=timezone.utc))
        self.assertEqual(next(x for x in group.buecher if x.spur == "a").runden, 1)

    def test_keine_ueberlappung_bleibt_unrangiert(self):
        rows = [quelle("a", "niedrig", ende="2026-10-02T00:00:00+00:00"),
                quelle("b", "mittel", start="2026-10-03T00:00:00+00:00")]
        group = vergleiche(rows)[0]
        self.assertFalse(group.vergleichbar)
        self.assertIsNone(group.zeitraum_start)
        self.assertTrue(all(b.rang is None for b in group.buecher))

    def test_kleine_stichprobe_markiert_aber_nicht_entfernt(self):
        rows = [quelle("a", "niedrig", pnl=5.0), quelle("b", "mittel", pnl=1.0)]
        group = vergleiche(rows)[0]
        self.assertEqual(len(group.buecher), 2)
        self.assertTrue(all(b.kleine_stichprobe for b in group.buecher))
        self.assertTrue(any(b.rang is not None for b in group.buecher))

    def test_fehlender_rundenzeitstempel_ist_qualitaetsfehler(self):
        rows = [quelle("a", "niedrig", rounds=[{"netto": 1.0, "kosten_belegt": True}]),
                quelle("b", "mittel")]
        book = next(b for b in vergleiche(rows)[0].buecher if b.spur == "a")
        self.assertIn("Runde ohne gültigen Ausstiegszeitstempel", book.datenqualitaet)
        self.assertIsNone(book.rang)

    def test_unpaarige_oder_duplizierte_runden_sperren_rangzahl(self):
        rows = [quelle("a", "niedrig", quality=["unpaariger Einstieg", "doppeltes Ereignis"]),
                quelle("b", "mittel")]
        book = next(b for b in vergleiche(rows)[0].buecher if b.spur == "a")
        self.assertEqual(book.datenqualitaet, ["doppeltes Ereignis", "unpaariger Einstieg"])
        self.assertIsNone(book.rang)

    def test_drawdown_nur_mit_vollstaendiger_chronologischer_kurve(self):
        rows = [quelle("a", "niedrig"), quelle("b", "mittel")]
        group = vergleiche(rows)[0]
        a = next(b for b in group.buecher if b.spur == "a")
        self.assertAlmostEqual(a.drawdown_pct, 100.0 * 5.0 / 110.0)
        rows[0]["equity_curve"] = [
            {"zeit": "2026-10-02T00:00:00+00:00", "wert": 100.0},
            {"zeit": "2026-10-03T00:00:00+00:00", "wert": 105.0}]
        a = next(b for b in vergleiche(rows)[0].buecher if b.spur == "a")
        self.assertIsNone(a.drawdown_pct)
        self.assertIn("deckt Anfang und Ende", a.drawdown_grund)

    def test_rangfolge_rendite_vorrang_dann_netto_pnl(self):
        rows = [quelle("niedrig", "basis", pnl=15.0, startkapital=100.0),
                quelle("mittel", "mittel", pnl=12.0, startkapital=100.0),
                quelle("hoch", "hoch", pnl=30.0, startkapital=300.0)]
        group = vergleiche(rows)[0]
        self.assertEqual([b.spur for b in group.buecher], ["niedrig", "mittel", "hoch"])
        self.assertEqual([b.rang for b in group.buecher], [1, 2, 3])

    def test_unvollstaendige_metadata_wird_nie_zusammengelegt(self):
        a, b = quelle("a", "niedrig", universum=None), quelle("b", "mittel", universum=None)
        groups = vergleiche([a, b])
        self.assertEqual(len(groups), 2)
        self.assertTrue(all(not g.vergleichbar for g in groups))

    def test_identische_eingabe_ergibt_identische_sortierung(self):
        rows = [quelle("b", "hoch", pnl=3.0), quelle("a", "mittel", pnl=5.0)]
        def signature(data):
            return [(g.schluessel, [(b.spur, b.netto_pnl, b.rang) for b in g.buecher])
                    for g in vergleiche(data)]
        self.assertEqual(signature(rows), signature(list(reversed(rows))))

    def test_quellen_keine_iterable_raises_typeerror(self):
        with self.assertRaisesRegex(TypeError, "Folge normalisierter Datensätze"):
            vergleiche(None)

    def test_ungueltige_einzelquelle_bleibt_sichtbar(self):
        group = vergleiche([None])[0]
        self.assertIn("Quelldatensatz ist ungültig", group.buecher[0].datenqualitaet)


if __name__ == "__main__":
    unittest.main()
