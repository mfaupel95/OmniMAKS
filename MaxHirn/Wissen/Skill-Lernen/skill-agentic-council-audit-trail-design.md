---
name: skill-agentic-council-audit-trail-design
description: Entwirft Audit-Protokolle mit Ereigniskatalog, Schema, Aufbewahrung, Unveränderlichkeit, Zugriff und Berichten; im Chat als Änderungsprotokoll für den Vault-Index erprobt.
metadata:
  type: reference
---

**Zweck:** Legt fest, welche Ereignisse protokolliert werden, in welchem Format, wie lange sie bleiben, wie sie vor Veränderung geschützt sind und wer sie lesen darf.

**Wann nutzen:** Bei Systemen mit Nachweispflicht oder personenbezogenen Daten. Nicht für Entwicklerlogs ohne Verantwortlichkeit.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Protokollzeilen für ein Änderungsprotokoll des Vault-Index im Chat skizzieren, ohne Datei.

**Ergebnis:** Entwurf mit einer JSON-Zeile je Änderung: Zeit (UTC), Akteur (Max, Skill oder Vault-Prüfer), Aktion aus drei Werten, Ziel, Vorher/Nachher und Grund. Offen ist, ob ein eigenes Protokoll nötig ist, weil Git die Änderungen bereits festhält. Der einzige Zusatz wäre der Akteur.

**Gelernt:**
- Der Skill ist für Systeme mit Rechten und Daten gebaut. Für einen Index reicht ein kleiner Ausschnitt. Die Pflichtbereiche Aufbewahrung, Unveränderlichkeit und Berichte sind hier überdimensioniert.
- Der Akteur ist der wichtigste Zusatz gegenüber Git. Das ist ein brauchbarer Maßstab, um zu entscheiden, ob ein eigenes Protokoll gebraucht wird.

**Grenzen:**
- Nur Skizze im Chat, keine Datei.
- Die Frage nach dem Nutzen gegenüber Git ist nicht entschieden.
