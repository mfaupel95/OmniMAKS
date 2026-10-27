---
name: skill-agentic-council-messaging-strategy
description: Legt Aufbau, Ton und Mikrotexte einer Rückmeldung fest (Ergebnis, Belege, offene Frage). Für die Rückmeldungen des Skill-Lern-Ablaufs an den Nutzer im Chat erprobt.
metadata:
  type: reference
---

**Zweck:** Macht eine Rückmeldung in einem Blick verständlich: was passiert ist, wo es liegt, was der Nutzer jetzt entscheiden muss.

**Wann nutzen:** Wenn eine Rückmeldung mehrere Zustände trägt oder eine Entscheidung verlangt. Nicht für eine einzelne Bestätigung.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Rückmeldungen des Skill-Lern-Ablaufs im Chat formulieren (kurz, eindeutig, mit Ergebnis und offener Frage). Keine Datei.

**Ergebnis:** Aufbau in drei Teilen: ein Satz zum Ergebnis, Pfade zu den Belegen, genau eine offene Frage am Ende. Ton sachlich auf Deutsch, ohne Skill-Interna wie Plugin-Namen. Fehlermeldungen nennen Ursache und nächsten Schritt, zum Beispiel „Index nicht lesbar, Datei gesperrt; erneut versuchen oder Sicherung prüfen.“ Keine Liste mit mehr als fünf Punkten.

**Gelernt:**
- Die offene Frage gehört ans Ende, nicht in den Fließtext. Sonst bleibt unklar, ob eine Antwort nötig ist.
- Der Nutzer liest Ergebnisse schneller, wenn Pfade als Pfade stehen und nicht als Beschreibung.

**Grenzen:**
- Keine Nutzerrückmeldung geprüft, keine Lesedauer gemessen.
- Der Skill verlangt Markenstimme, Feature-Namen und Conversion-Texte. Für interne Rückmeldungen entfällt der größte Teil.
