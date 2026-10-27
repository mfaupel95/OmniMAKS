---
name: skill-agentic-council-threat-model
description: Ermittelt Bedrohungen nach Kategorien (Vorspiegelung, Manipulation, Abstreiten, Offenlegung, Dienstausfall, Rechteausweitung) mit Risikostufe und Gegenmaßnahme. Für den Vault (Verlust, Manipulation, Diebstahl, Fehlbedienung durch Skripte) im Chat erprobt, ohne Systemprüfung.
metadata:
  type: reference
---

**Zweck:** Listet, wie Werte verloren gehen oder beschädigt werden können, und ordnet jede Gefahr nach Wahrscheinlichkeit und Schaden.

**Wann nutzen:** Vor dem Aufbau eines Systems mit schützenswerten Daten. Nicht für Daten ohne Wert.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Bedrohungen für den Vault mit Eintrittswahrscheinlichkeit und Gegenmaßnahme im Chat skizzieren. Keine Datei, nichts geprüft.

**Ergebnis:** Verlust (Festplattenausfall, Diebstahl des Rechners): mittel, schwer; Gegenmaßnahme Sicherung getrennt vom Rechner. Manipulation (Skript überschreibt Index, Fehler beim Schreiben): mittel, mittel; Gegenmaßnahme Sicherungskopie mit Datum vor jeder Änderung, Probelauf. Diebstahl oder Fremdzugriff auf Daten: niedrig bis mittel, schwer; Gegenmaßnahme Festplattenverschlüsselung und Benutzerrechte. Fehlbedienung durch Skripte (Löschen im Archiv, falsche Pfade): mittel, schwer; Gegenmaßnahme Schreibrechte begrenzen, Löschen nur mit Bestätigung. Restrisiko: Synchronisations- und Cloud-Dienste, die außerhalb liegen.

**Gelernt:**
- Die Fehlbedienung durch eigene Skripte ist wahrscheinlicher als ein Angriff von außen und trifft dieselben Daten.
- Eine Sicherung außerhalb des Rechners deckt Verlust und Manipulation zugleich ab.

**Grenzen:**
- Keine Systemprüfung, keine Sicherung gelesen, Wahrscheinlichkeiten sind Einschätzungen.
- Der Skill verlangt Datenflüsse, Vertrauensgrenzen und STRIDE je Fluss. Für einen Ordner ist die Kategorienliste ausreichend.
