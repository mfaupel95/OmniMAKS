"""Quant-Urteil im XPERP-Live-Pfad - Adapter zwischen handeln.py und scanner_quant/quant.py.

Reine Rechnung bis auf die Funding-Abfrage (okxf.funding_pa). Steuerung ueber den
Block "quant" in wachen.json:

    "quant": {"modus": "bericht", "mindest_score": 60,
              "dehnung_max_atr": 6.0, "ohne_urteil": "zulassen"}

modus
    "aus"      - nichts berechnen, nichts anhaengen (wie vor dem Einbau)
    "bericht"  - Urteil und Funding werden berechnet und an den Kandidaten und
                 die Journalzeile gehaengt, ENTSCHEIDEN aber nichts (Standard)
    "tor"      - zusaetzlich faellt ein Kandidat heraus, dessen Score unter
                 mindest_score liegt oder der zu_gedehnt ist
ohne_urteil
    Was gilt, wenn es kein Urteil gibt (unter LANG + LUFT Tageskerzen; gemessen
    am 07.10.2026 erreichen nur rund 40 von 181 Kontrakten 110 Tage)?
    "zulassen" (Standard) laesst den Kandidaten durch, "sperren" wirft ihn raus.
    "sperren" wuerde die Spur nahezu stilllegen - nur bewusst setzen.

Die Datei laedt scanner_quant/quant.py ueber den PFAD, nicht ueber sys.path: die
Spur hat ihren eigenen Ordner als sys.path[0], ein gleichnamiges Modul koennte
verdeckt werden (gleiche Linie wie ratschen.py in handeln.py).
"""
import os
from importlib.util import module_from_spec, spec_from_file_location

HIER = os.path.dirname(os.path.abspath(__file__))
_QUANT = os.path.join(os.path.dirname(HIER), "scanner_quant", "quant.py")

LANG = 100        # SMA-Laenge der Ordnung bei XPERP (Spot nimmt 200, s. quant.urteil)
MODI = ("aus", "bericht", "tor")


def _lade():
    spec = spec_from_file_location("quant_urteil_kern", _QUANT)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


quant = _lade()


def konfig(w):
    """Der quant-Block aus wachen.json mit Vorgaben. Unbekannter Modus -> 'aus'
    (lieber nichts tun als raten) mit Hinweis im Feld 'fehler'."""
    k = dict((w or {}).get("quant") or {})
    modus = k.get("modus", "aus")
    fehler = None
    if modus not in MODI:
        fehler, modus = "unbekannter Modus %r" % (modus,), "aus"
    ohne = k.get("ohne_urteil", "zulassen")
    if ohne not in ("zulassen", "sperren"):
        fehler, ohne = "ohne_urteil %r unbekannt" % (ohne,), "zulassen"
    return {"modus": modus,
            "mindest_score": float(k.get("mindest_score", 60)),
            "dehnung_max_atr": float(k.get("dehnung_max_atr", 6.0)),
            "ohne_urteil": ohne, "fehler": fehler}


def urteile_tageskerzen(tageskerzen):
    """Urteil fuer BEIDE Richtungen aus den Tageskerzen (ein Abruf, den
    auswahl.sammle fuer den Hebel-Deckel ohnehin macht). None je Richtung,
    wenn zu wenig Historie."""
    return {"long": quant.urteil(tageskerzen, richtung="long", lang=LANG),
            "short": quant.urteil(tageskerzen, richtung="short", lang=LANG)}


def bewerte(x, seite, cfg, funding_pa=None):
    """Urteil fuer einen Wert der Rangliste in einer Richtung.

    x ist ein Eintrag aus rangliste() mit x["quant"][seite] (ohne Funding
    berechnet). Rueckgabe: dict fuer den Kandidaten oder None, wenn kein Urteil
    vorliegt. Funding wird hier NACHTRAEGLICH eingerechnet (nur fuer die wenigen
    Kandidaten, nicht fuer alle Kontrakte): quant.funding_punkte verschiebt den
    Score, der Dehnungsdeckel gilt danach erneut.
    """
    roh = (x.get("quant") or {}).get(seite)
    if not roh:
        return None
    score = roh["quant_score"]
    punkte = None
    if funding_pa is not None:
        kosten = funding_pa if seite == "long" else -funding_pa
        punkte = quant.funding_punkte(kosten)
        score = max(0.0, min(100.0, score + punkte))
        if roh["zu_gedehnt"]:
            score = min(score, 50.0)
    return {"score": round(score, 1), "score_ohne_funding": roh["quant_score"],
            "zu_gedehnt": roh["zu_gedehnt"],
            "dehnung_atr": roh["dehnung_atr"], "ordnung": roh["ordnung"],
            "funding_pa": None if funding_pa is None else round(funding_pa, 4),
            "funding_punkte": None if punkte is None else round(punkte, 1)}


def erlaubt(q, cfg):
    """(ok, grund) fuer den Modus 'tor'. q ist das Ergebnis von bewerte()."""
    if q is None:
        if cfg["ohne_urteil"] == "sperren":
            return False, "kein Quant-Urteil (zu wenig Historie)"
        return True, ""
    if q["dehnung_atr"] > cfg["dehnung_max_atr"]:
        return False, "gedehnt (%.1f ATR)" % q["dehnung_atr"]
    if q["score"] < cfg["mindest_score"]:
        return False, "Quant-Score %.1f < %.0f" % (q["score"], cfg["mindest_score"])
    return True, ""


def text(q):
    """Kurztext fuer Journalspalte 'grund' und die Logzeile."""
    if q is None:
        return "quant n/a"
    s = "quant %.1f" % q["score"]
    if q["funding_pa"] is not None:
        s += " (Funding %+.1f%%/a, %+.1f Pkt)" % (q["funding_pa"] * 100,
                                                  q["funding_punkte"])
    if q["zu_gedehnt"]:
        s += " !gedehnt"
    return s
