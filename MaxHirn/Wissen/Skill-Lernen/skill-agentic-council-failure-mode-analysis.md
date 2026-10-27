---
name: skill-agentic-council-failure-mode-analysis
description: Listet Ausfälle je Komponente mit Folgen, Gegenmaßnahmen und Erkennungssignalen; für den Vault-Ablauf (Index, Suche, Sicherung, Synchronisierung) im Chat als fünf Fälle erprobt.
metadata:
  type: reference
---

**Zweck:** Findet systematisch, wie Komponenten ausfallen können, wie sich der Ausfall ausbreitet und welche Gegenmaßnahmen und Meldungen greifen.

**Wann nutzen:** Vor dem Einführen eines Ablaufs mit mehreren Teilen oder Abhängigkeiten. Nicht für einzelne Funktionen ohne Abhängigkeiten.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: fünf wahrscheinlichste Ausfälle des Vault-Ablaufs mit je einer Gegenmaßnahme im Chat, ohne Datei.

**Ergebnis:** Fünf Fälle: toter Pfad im Index, gleichzeitiges Schreiben auf zwei Geräten, unzuverlässige Archivsuche, stiller Sicherungsfehler, Sync mit falscher Reichweite. Hauptrisiko: der stille Sicherungsfehler, weil er ohne aktive Meldung unbemerkt bleibt. Offen: welche Synchronisierung läuft.

**Gelernt:**
- Der Skill verlangt Ausbreitung und Erkennung, nicht nur Ausfallliste. Beim Sicherungsfehler liegt der Schaden in der fehlenden Meldung, nicht im Ausfall selbst.
- Die Synchronisierung ist der Punkt mit der größten Unschärfe, weil ihr Umfang nicht bekannt ist.

**Grenzen:**
- Nur Chat-Skizze, keine Datei, keine Systeme geprüft.
- Die Gegenmaßnahmen sind Vorschläge, keine getesteten Abläufe.
- Der Skill verlangt eine Rollback-Strategie. Für einen Vault wurde sie nicht ausgearbeitet, weil die Sicherung die Rückfallebene ist.
