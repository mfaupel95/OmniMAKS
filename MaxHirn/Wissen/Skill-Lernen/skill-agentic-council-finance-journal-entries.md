---
name: skill-agentic-council-finance-journal-entries
description: Erstellt einen buchungsfähigen Buchungssatz mit vollständiger Kontierung, Ausgleich, Umkehrlogik und Begründung; für eine Rechnung von 119 Euro brutto mit 19 Prozent Umsatzsteuer im Chat als Beispiel erprobt, ohne Buchung.
metadata:
  type: reference
---

**Zweck:** Hält einen Geschäftsvorfall in Buchungssätzen fest, die ein Prüfer ohne Rückfragen nachvollziehen kann: Konten, Beträge, Ausgleich, Umkehrung und Quelle.

**Wann nutzen:** Bei Belegen, die buchungspflichtig sind und deren Behandlung nicht offensichtlich ist. Nicht für Vorgänge, die keine Buchung auslösen.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Beispiel-Buchungssatz für 119 € brutto mit 19 % Umsatzsteuer für ein Arbeitsmittel im Chat, ohne Buchung.

**Ergebnis:** Drei Zeilen: Aufwand netto 100,00, Vorsteuer 19,00, Verbindlichkeit 119,00. Probe stimmt. Zwei Vorbedingungen: Die Vorsteuer gibt es nur bei umsatzsteuerlicher Unternehmerstellung, sonst entfällt die Zeile und der Aufwand wird 119,00. Geringwertige Wirtschaftsgüter unterliegen einer Grenze, die vor der Buchung mit dem Steuerberater zu bestätigen ist. Nicht geprüft: Kontonummern des eigenen Kontenrahmens.

**Gelernt:**
- Der Skill verlangt Konten und Dimensionen, die man für einen privaten Beleg nicht hat. Die eigentliche Entscheidung ist die steuerliche Stellung, nicht der Buchungssatz.
- Die Probe Soll gleich Haben ist die einfachste Kontrolle, die man immer machen sollte.

**Grenzen:**
- Keine Buchung, keine Kontonummern des eigenen Kontenrahmens, keine geprüfte GWG-Grenze.
- Die Beispielkontonummer 1576 stammt aus dem Kontenrahmen SKR03 und ist nicht bestätigt.
- Der Skill verlangt Prüfverfahren und Wesentlichkeitsschwellen für Unternehmen. Für eine private Beispielbuchung sind sie nicht nötig.
