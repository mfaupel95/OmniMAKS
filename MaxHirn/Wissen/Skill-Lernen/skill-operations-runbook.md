---
name: skill-operations-runbook
description: Beschreibt einen wiederkehrenden Vorgang Schritt für Schritt mit Erwartung, Fehlerfall und Rückweg. Für einen beschädigten Vault-Index (sichern, prüfen, aus Kopie wiederherstellen) im Chat skizziert.
metadata:
  type: reference
---

**Zweck:** Macht eine Notfallmaßnahme so klar, dass sie auch unter Druck richtig ausgeführt wird.

**Wann nutzen:** Bei Vorgängen, die selten, aber folgenreich sind. Nicht für Routine, die jeder kennt.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Runbook für einen beschädigten Vault-Index skizzieren. Keine Datei, nichts getestet.

**Ergebnis:** Schritte: 1. beschädigte Indexdatei zuerst mit Datum kopieren, bevor etwas ersetzt wird; 2. Zeilen prüfen (doppelte Kennungen, tote Pfade); 3. letzte gute Kopie anhand des Datums im Dateinamen finden; 4. Kopie mit dem Notizordner vergleichen; 5. Index aus den vorhandenen Notizen neu aufbauen, falls keine Kopie passt. Rückweg: die beschädigte Kopie bleibt erhalten. Eskalation: Max.

**Gelernt:**
- Das Sichern der beschädigten Datei ist der wichtigste Schritt. Ohne ihn lässt sich der Schaden nicht mehr untersuchen.
- Ein Runbook braucht eine Erwartung je Schritt, sonst merkt man nicht, dass etwas schiefgeht.

**Grenzen:**
- Nicht ausgeführt, nicht getestet, keine Sicherung geprüft.
- Der Skill verlangt Eskalationspläne mit Bereitschaftsdienst und ITSM-Anbindung. Für einen Einzelnutzer genügen Schritte und Rückweg.
