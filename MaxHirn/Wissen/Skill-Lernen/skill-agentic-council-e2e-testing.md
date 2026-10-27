---
name: skill-agentic-council-e2e-testing
description: Plant Ende-zu-Ende-Prüfungen für Abläufe über die volle Strecke (Testdaten, Stichproben, Zeitbudget, Wiederholungen); für die Sicherungsskripte des Vaults als Prüfkette im Chat übertragen.
metadata:
  type: reference
---

**Zweck:** Prüft einen Ablauf von Anfang bis Ende über alle Schritte, damit nicht nur einzelne Teile funktionieren. Gedacht für Browseroberflächen mit Benutzerreisen.

**Wann nutzen:** Bei Abläufen mit mehreren Schritten, die ein Benutzer ausführt oder die Ausgabe am Ende nutzt. Nicht für einzelne Funktionen ohne Zusammenspiel.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Ende-zu-Ende-Prüfung für die Sicherungsskripte im Chat skizzieren (Lauf, Ergebnis, Wiederherstellung), ohne Datei.

**Ergebnis:** Vier Schritte: Lauf gegen ein Testziel, Vergleich von Dateizahl, Größe und einer Stichprobe mit Prüfsummen, Wiederherstellung einer Datei, Alter des letzten Laufs. Die Prüfung soll automatisch laufen und nur bei Abweichungen melden. Offen: ob die Skripte Prüfsummen erzeugen.

**Gelernt:**
- Die Browser-Ausrichtung des Skills passt nicht. Der Kern lässt sich übertragen: Benutzerreise, Testdaten, feste Zeitbudgets, und vor allem die Wiederherstellung als Endpunkt.
- Eine Sicherung ohne Wiederherstellung ist nicht geprüft. Das gilt auch für einen Test, der nur Exit-Codes zählt.

**Grenzen:**
- Nur Chat-Skizze, keine Datei, keine Skripte gelesen.
- Keine Browser-Tests, kein Framework-Vergleich, nichts davon war nötig.
