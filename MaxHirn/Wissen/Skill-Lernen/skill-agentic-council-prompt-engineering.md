---
name: skill-agentic-council-prompt-engineering
description: Baut eine Anweisung in Schichten (Rolle, Aufgabe, Regeln, Ausgabeformat, Beispiele, Umgang mit Unklarem) und legt Versionierung fest. Für das Zusammenfassen einer Lernnotiz im Chat erprobt, so dass jede Aussage auf eine Stelle im Text zurückführbar ist.
metadata:
  type: reference
---

**Zweck:** Macht die Ausgabe eines Sprachmodells prüfbar, indem Regeln, Format und Quellenbezug fest vorgegeben sind.

**Wann nutzen:** Wenn eine Anweisung wiederholt läuft und ihr Ergebnis weiterverwendet wird. Nicht für eine einmalige Frage.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Aufbau einer Anweisung zum Zusammenfassen einer Lernnotiz skizzieren, damit das Ergebnis prüfbar bleibt. Keine Datei, kein Modell aufgerufen.

**Ergebnis:** Schichten: Rolle (Zusammenfasser ohne eigene Ergänzungen), eine Aufgabe, Regeln (nur Inhalt der Notiz, jede Aussage mit einem Stichwort aus dem Text belegen, Unklares als „nicht im Text“ kennzeichnen), festes Ausgabeformat (Kernaussage, drei Punkte, offene Fragen), zwei Beispielpaare, eine Versionsnummer im Kopf der Anweisung. Prüfbar wird die Ausgabe, wenn jeder Punkt auf eine Textstelle zurückführt.

**Gelernt:**
- Die Pflicht zur Textstelle ist wichtiger als jede Stilvorgabe. Ohne sie kann niemand erkennen, ob das Modell etwas dazugedichtet hat.
- Für kurze Notizen genügt eine Anweisung mit Format und Regeln. Die Beispiele fallen bei Routinearbeit weg.

**Grenzen:**
- Kein Modell aufgerufen, keine Ausgabe bewertet.
- Der Skill verlangt Modellwahl, Temperatur, Kostenschätzung und Evaluationsläufe. Für eine einzelne Zusammenfassung entfällt der größte Teil.
