---
name: skill-agentic-council-cost-analysis
description: Modelliert Infrastrukturkosten je Komponente, Skalierung, Sparoptionen und Budgetwarnungen; für den Vault-Index als Kostenübersicht im Chat erprobt.
metadata:
  type: reference
---

**Zweck:** Erfasst laufende Kosten einer Infrastruktur je Komponente, rechnet Stückkosten und Skalierung und legt Warnschwellen fest.

**Wann nutzen:** Bei Diensten mit Gebühren pro Nutzung oder Abos. Nicht für rein lokale Werkzeuge ohne laufende Kosten.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: laufende Kosten des Vault-Index und seiner Werkzeuge im Chat, ohne Datei.

**Ergebnis:** Der Vault-Index hat keine laufenden Gebühren. Index, Suche und Notizen laufen lokal ohne Dienst. Der Speicherbedarf wächst mit dem Archiv (rund 45 GB), nicht mit dem Index. Sicherungen kosten Hardware und Strom. Die Modelle (rund 51 GB) gehören zu den Agenten, nicht zum Index. Ein Cloud-Abo wäre der erste Posten, den man monatlich sehen würde.

**Gelernt:**
- Der Skill ist für Dienste mit Rechnung gebaut. Für lokale Werkzeuge ist das Ergebnis eine Bestandsaufnahme ohne Rechnung. Der Nutzen liegt darin, zu prüfen, ob es überhaupt einen Posten gibt.
- Der Speicher ist der einzige echte Kostentreiber. Das ist schon beim Archiv bekannt.

**Grenzen:**
- Keine Zahlen in Euro. Hardwarepreise und Stromverbrauch wurden nicht gemessen.
- Keine Dateien gelesen, nur die bekannte Struktur aus `CLAUDE.md`.
- Der Skill rechnet Budgetschwellen, die hier nicht anfallen.
