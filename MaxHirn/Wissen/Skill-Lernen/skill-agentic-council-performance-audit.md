---
name: skill-agentic-council-performance-audit
description: Sucht Engpässe über Ausführungszeit, Datenmenge und Abhängigkeiten und legt eine Messreihe mit Priorität fest. Für die Suche im Vault-Index bei wachsender Notizenzahl im Chat skizziert, ohne Messung.
metadata:
  type: reference
---

**Zweck:** Findet, wo ein Ablauf langsam wird, bevor es spürbar wird, und legt fest, wie man es misst.

**Wann nutzen:** Wenn ein Ablauf mit der Datenmenge wächst oder eine Schwelle erreicht. Nicht für einmalige Vorgänge.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Engpass der Suche im Vault-Index bei wachsender Notizenzahl skizzieren und Messung beschreiben. Keine Messung ausgeführt, keine Datei.

**Ergebnis:** Die Suche liest die Indexdatei vollständig, Laufzeit wächst also linear mit der Zeilenzahl. Der Engpass liegt in der Dateigröße, nicht in der Rechenarbeit. Messung: Kopie der Indexdatei mit zweihundert, tausend und fünftausend Zeilen anlegen, jeweils dieselbe Suche zehnmal laufen lassen, Median notieren. Spürbar wird es erst bei mehreren tausend Zeilen. Empfehlung: Messung erst, wenn der Index deutlich über dreihundert Zeilen liegt.

**Gelernt:**
- Die Messung braucht eine Kopie, damit der echte Index nicht verändert wird.
- Die Zeilenzahl ist der richtige Messwert, nicht die Anzahl der Suchen pro Tag.

**Grenzen:**
- Keine Messung ausgeführt, keine Zeitangaben.
- Der Skill verlangt Profiling von Rendering, Netzwerk und Datenbank. Für eine Textdatei entfallen diese Teile.
