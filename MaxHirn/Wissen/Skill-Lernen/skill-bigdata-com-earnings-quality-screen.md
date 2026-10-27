---
name: skill-bigdata-com-earnings-quality-screen
description: Prüft, ob ausgewiesener Gewinn durch Zahlungsflüsse gedeckt ist (Cashflow gegen Gewinn, Forderungen, Rückstellungen, Nicht-GAAP-Ausgleich). Für die Frage nach Gewinndeckung über mehrere Jahre im Chat skizziert, ohne Datenabfrage.
metadata:
  type: reference
---

**Zweck:** Zeigt, ob ein Gewinn auf Geld oder auf Schätzungen beruht, und wie sich das über die Zeit entwickelt.

**Wann nutzen:** Wenn man den Zahlen einer Firma nicht traut oder eine Position groß werden soll. Nicht für eine einzelne Quartalszahl.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Prüfen, ob der Gewinn durch Zahlungsflüsse gedeckt ist (Cashflow gegen Gewinn, Sonderposten). Keine Datenabfrage, keine Datei.

**Ergebnis:** Entscheidend ist der Trend über mehrere Jahre, nicht ein Quartal. Ein Verhältnis von operativem Cashflow zu Gewinn unter 0,6 oder eine wachsende Lücke ist ein Warnsignal. Dazu: Forderungen, die schneller wachsen als der Umsatz; Nicht-GAAP-Bereinigungen, die nur in eine Richtung wirken; wiederkehrende Sonderposten. Ergebnis ist eine Note mit Begründung, keine Anschuldigung.

**Gelernt:**
- Ein Gewinn ohne Cashflow ist häufig, aber nicht immer ein Fehler. Die Frage ist, ob die Lücke sich schließt.
- Wiederkehrende Sonderposten sind keine Sonderposten mehr.

**Grenzen:**
- Keine Daten abgefragt, keine Firma geprüft.
- Der Skill verlangt Mehrjahresdaten, Accrual-Kennzahlen und einen Beneish-Score. Für eine Haushaltsentscheidung genügt die Trendprüfung.
