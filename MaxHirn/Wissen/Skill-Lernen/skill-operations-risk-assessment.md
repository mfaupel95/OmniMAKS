---
name: skill-operations-risk-assessment
description: Erfasst Risiken mit Wahrscheinlichkeit, Auswirkung, Stufe, Maßnahme und Verantwortlichem in einer Matrix. Für Datenverlust, Fehlbedienung und Sicherungsausfall des Vaults im Chat erprobt.
metadata:
  type: reference
---

**Zweck:** Ordnet Risiken nach Dringlichkeit, damit die wichtigsten zuerst Maßnahmen bekommen.

**Wann nutzen:** Vor einer Veränderung am System oder regelmäßig bei Systemen mit wertvollen Daten. Nicht für Risiken ohne Auswirkung.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Risiken für den Vault mit Wahrscheinlichkeit, Auswirkung und Maßnahme skizzieren. Keine Datei, nichts geprüft.

**Ergebnis:** Datenverlust durch Festplattenausfall oder Diebstahl: mittlere Wahrscheinlichkeit, hohe Auswirkung, Stufe hoch; Maßnahme Sicherung außerhalb des Rechners. Fehlbedienung durch ein Skript, das den Index überschreibt: mittel und hoch, Stufe hoch; Maßnahme Kopie vor jeder Änderung. Sicherungsausfall, der unbemerkt bleibt: mittel und hoch, Stufe hoch; Maßnahme monatlicher Wiederherstellungstest.

**Gelernt:**
- Eine Sicherung, die nie wiederhergestellt wurde, ist kein Schutz. Der Test ist die Maßnahme, nicht die Kopie.
- Die Matrix zeigt drei Risiken derselben Stufe. Die Reihenfolge entscheidet dann der Aufwand der Maßnahme.

**Grenzen:**
- Keine Sicherung geprüft, Wahrscheinlichkeiten sind Einschätzungen.
- Der Skill verlangt Risikoregister mit Eigentümern je Team und Statusverfolgung. Für einen Einzelnutzer genügt die Matrix.
