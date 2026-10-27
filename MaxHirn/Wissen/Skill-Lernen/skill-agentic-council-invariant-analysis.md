---
name: skill-agentic-council-invariant-analysis
description: Listet Sicherheitsaussagen eines Entwurfs als Invarianten mit Annahmen und Prüfart; für den Vault-Index als fünf Invarianten mit deterministischer Prüfung im Chat erprobt.
metadata:
  type: reference
---

**Zweck:** Macht Sicherheitsaussagen prüfbar: welche Eigenschaft immer gelten soll, welche Annahmen dahinterstehen und ob sich die Eigenschaft ohne Modellprüfer kontrollieren lässt.

**Wann nutzen:** Bei Systemen mit Sicherheitszusagen, deren Verletzung Schaden anrichtet. Nicht für Abläufe ohne Schutzanspruch.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Invarianten für den Vault-Index im Chat skizzieren, ohne Datei.

**Ergebnis:** Fünf Invarianten: keine doppelten Pfade, kein toter Pfad, jede Notiz eingetragen (Lebendigkeit), kein Eintrag auf Stufe „besonders schützenswert“, Schlagwörter aus der kontrollierten Liste. Vier davon lassen sich vollständig deterministisch prüfen, ohne Modellprüfer. Die Annahmen: Umbenennen und Löschen ändern den Index zugleich, die Stufenliste ist aktuell, der Vault-Prüfer läuft regelmäßig. Der tatsächliche Zustand des Index ist unbekannt.

**Gelernt:**
- Die Trennung in Sicherheitseigenschaften (immer) und Lebendigkeit (irgendwann) hilft, Prüfungen richtig zu wählen. Lebendigkeit braucht einen Lauf, Sicherheit nur eine Prüfung im Ablauf.
- Die Annahme „Umbenennen und Löschen ändern den Index zugleich“ ist eine Gewohnheit. Sie gehört in die Prüfliste, weil sie bricht, sobald jemand direkt im Dateisystem arbeitet.

**Grenzen:**
- Nur Chat-Skizze, keine Datei, Index nicht gelesen.
- Keine Modellprüfung, weil sie für eine Datei dieser Größe übertrieben wäre.
- Der Skill verlangt Bedrohungsmodell und Angreifer-Fähigkeiten. Für einen Index ohne Gegenspieler sind diese Punkte nicht anwendbar.
