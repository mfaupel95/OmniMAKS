---
name: skill-agentic-council-device-integration
description: Plant Gerätefunktionen (Kamera, Standort, Biometrie, Bluetooth, Sensoren) mit Berechtigungen, Rückfallverhalten und Stromverbrauch; für den Abruf des Vault-Index auf dem Handy im Chat erprobt.
metadata:
  type: reference
---

**Zweck:** Legt fest, welche Gerätefunktionen eine App braucht, wie die Berechtigungen angefragt werden, was bei Verweigerung passiert und welchen Akku-Verbrauch das hat.

**Wann nutzen:** Wenn eine App Gerätehardware nutzt. Nicht für reine Textdienste ohne Gerätebezug.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: prüfen, ob der Vault-Index auf dem Handy abrufbar sein sollte und welche Geräteschnittstellen nötig wären, im Chat, ohne Datei.

**Ergebnis:** Der Index braucht keine Gerätefunktionen. Nötig sind Dateizugriff (Sync oder Git) und Netzwerk für den Abgleich. Biometrie wäre nur optional für einen Zugriffsschutz sinnvoll. Die Berechtigungsfragen des Skills treffen nicht zu. Das größere Risiko ist, dass der Sync mehr als `Wissen/` mitnimmt, also auch das Archiv mit besonders schützenswerten Daten. Eine eigene Geräteschnittstelle ist nicht nötig.

**Gelernt:**
- Die Pflichtliste des Skills (Kamera, Sensoren, Bluetooth) ist für Apps mit Hardwarebezug gedacht. Für einen Text-Index ist die wichtigste Frage, welche Daten über den Sync auf das Gerät gelangen.
- Der Skill fragt nicht nach dem Datenumfang des Syncs. Dieser Punkt gehört in die Klassifikation, nicht in die Gerätefunktionen.

**Grenzen:**
- Nur Entscheidung im Chat, keine Datei.
- Der Sync-Dienst für das Handy ist nicht bekannt und nicht geprüft.
