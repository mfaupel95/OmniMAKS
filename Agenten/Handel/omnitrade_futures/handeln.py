"""Handelsspur `omnitrade_futures` - das Hebel-Bein der omnitrade-Spur.

AUFTRAG MAX (30.09.2026): "hebel x7 fuer den anfang, aggressiver dann weniger,
kleine positionsgroessen zuerst."

WOHER DAS SIGNAL KOMMT
----------------------
Identisch mit der Spot-Spur `omnitrade`: die Rust-Laeufe in
`Werkstatt/omnitrade/status/` entscheiden (ihre .omni-Skripte), diese Spur
spiegelt die POSITION. quelle/signal/ausstieg_grund werden NICHT abgeschrieben,
sondern aus `omnitrade/handeln.py` ueber den Pfad geladen - eine Rechnung, zwei
Ausfuehrungen. Ein eigener Entschluss hier waere eine zweite Strategie.

WAS ANDERS IST
--------------
Die Ausfuehrung: Kraken FUTURES statt Spot, Hebel 7 (wachen-Feld `hebel`), Stop
als stp-Order an der Boerse (ueberlebt Neustarts), Basismengen nach der
Instrument-Praezision abgerundet (PF_XBTUSD: 0,0001 BTC; PF_SOLUSD: 0,01 SOL).
Der Nominaldeckel bleibt 130 USD; es wird nie auf eine groessere Groesse
aufgerundet. Eigene Spur statt zweiter Boerse in der Spot-Spur, weil ein Buch
EINE Waehrung fuehrt - die Spot-Spur rechnet in USDC, Futures in USD.

`handel_erlaubt=true` in der Wache ist allein keine Freigabe: ohne offenes
Freigabefenster und Mindestguthaben bleibt jeder Zyklus Papier. Kraken Futures
kennt keinen Demo-Modus - Papier heisst hier ausschliesslich Buch.

NOCH OFFEN (T-Listen): Der erste echte End-to-End-Lauf fehlt als Beleg fuer
Order, Kraken-Stop und Exit. Der Trailing-Stop ist bereits im Zyklus verdrahtet
und durch Tests abgedeckt; die effektive Hebelgrenze laeuft ueber
`/leveragepreferences` (der `leverage`-Parameter in `/sendorder` wird ignoriert).
Der Live-Lauf bleibt bis Freigabefenster und Mindestguthaben gesperrt.

Aufruf:
  ../scanner/.venv/Scripts/python.exe handeln.py --vorschau | --papier | --live
"""

import argparse
import importlib.util
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
HANDEL = os.path.dirname(HIER)
for p in (HANDEL, os.path.join(HANDEL, "scanner"), HIER):
    if p not in sys.path:
        sys.path.insert(0, p)

import spur_buch as buch  # noqa: E402

# spur_buch ZUERST (legt Agenten/Bus auf sys.path), dann die Spot-Spur laden
# und ihre Rechnung WIEDER VERWENDEN - nicht kopieren.
_omni_spec = importlib.util.spec_from_file_location(
    "omnitrade_handeln", os.path.join(HANDEL, "omnitrade", "handeln.py"))
# Die Statusdatei GEpinnt lesen (Naht OMNITRADE_STATUS in omnitrade/lesen.py).
# Ohne das nimmt lesen.dateien() ALLE live_*.json im Statusordner - und im
# Ordner laeuft adx_macd ausser auf BTC noch auf ETH. Diese Spur ist eine
# MONOstrategie-Spur: sie spiegelt genau einen Lauf.
_status_name = ""
try:
    with open(os.path.join(HIER, "wachen.json"), encoding="utf-8") as _fh:
        _status_name = (json.load(_fh) or {}).get("statusdatei") or ""
except Exception:                                            # noqa: BLE001
    _status_name = ""
if _status_name:
    # HIER ist Agenten/Handel/omnitrade_futures, ../.. waere Agenten und
    # ../Werkstatt gibt es nicht - erst ../.. ../.. ist die Repo-Wurzel.
    _status_pfad = os.path.normpath(os.path.join(
        HIER, "..", "..", "..", "Werkstatt", "omnitrade", "status",
        _status_name))
    os.environ["OMNITRADE_STATUS"] = _status_pfad

omni = importlib.util.module_from_spec(_omni_spec)
sys.modules[_omni_spec.name] = omni
_omni_spec.loader.exec_module(omni)

# Der Futures-Weg ist ein eigener Boersenname in spur_buch.orderweg(); der
# Hebel kommt aus der wachen und wird vor dem Zyklus gesetzt.
_weg = None


def boerse_binden(w):
    global _weg
    import weg
    _weg = weg
    hebel = weg.setze_hebel(w)
    # Der Hebel gehoert am KONTRAKT, nicht in die Order (gemessen 01.10.2026:
    # Kraken ignoriert den leverage-Parameter von /sendorder). Erst im
    # Live-Zweig setzen - Papier soll die Boerse nicht anfassen.
    if w.get("handel_erlaubt"):
        weg.hebel_vorbereiten(w.get("instrument") or "PF_SOLUSD", hebel)
    return hebel


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vorschau", action="store_const", const="vorschau", dest="modus")
    ap.add_argument("--papier", action="store_const", const="papier", dest="modus")
    ap.add_argument("--live", action="store_const", const="live", dest="modus")
    ap.add_argument("--wachen", action="store_const", const="wachen", dest="modus")
    ap.set_defaults(modus="papier")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    w = buch.lade_wachen(buch.pfade(HIER)[0])
    boerse_binden(w)

    return buch.zyklus(HIER, omni.quelle, omni.signal, a.modus,
                       "handel/omnitrade_futures",
                       zusatz_ausstieg=omni.ausstieg_grund)


if __name__ == "__main__":
    raise SystemExit(main())
