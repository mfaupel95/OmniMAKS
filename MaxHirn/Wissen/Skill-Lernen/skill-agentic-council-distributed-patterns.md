---
name: skill-agentic-council-distributed-patterns
description: Bewertet verteilte Systeme nach Konsistenz, Ausfallverhalten, Replikation, Transaktionen und Betriebsbereitschaft; für den Vault auf mehreren Geräten im Chat als Konfliktanalyse erprobt.
metadata:
  type: reference
---

**Zweck:** Prüft, wie ein System mit Teilausfällen, Replikation und Konflikten umgeht, und empfiehlt Muster für Konsistenz, Wiederholung und Ausfallbehandlung.

**Wann nutzen:** Bei Diensten über mehrere Knoten oder Standorte mit echten Ausfallszenarien. Nicht für Dateien auf einem einzelnen Gerät.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: prüfen, ob der Vault gleichzeitig auf mehreren Geräten beschrieben werden kann und welche Konflikte entstehen, im Chat, ohne Datei.

**Ergebnis:** Gleichzeitiges Schreiben ist möglich, erzeugt aber Konflikte, vor allem im Index, weil alle Einträge in einer Datei stehen. Empfehlung: ein Hauptgerät schreibt den Index, die anderen lesen und gleichen vor einer Änderung ab. Last-writer-wins verliert still Text und ist zu vermeiden. Offen ist, welcher Synchronisierungsweg genutzt wird.

**Gelernt:**
- Der Skill ist für Systeme mit Netzwerkausfällen und Konsens gebaut. Für Textdateien mit wenigen Geräten reicht die Frage: Wie viele Schreiber gibt es pro Datei?
- Die Einzeldatei Index ist der Engpass. Eine Aufteilung in kleinere Dateien würde die Konflikte verringern.

**Grenzen:**
- Nur Chat-Skizze, keine Datei, kein Synchronisierungsdienst geprüft.
- Die Konfliktbehandlung beruht auf allgemeinem Wissen zu Git und Ordnersynchronisierung.
