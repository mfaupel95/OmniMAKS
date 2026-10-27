---
name: skill-agentic-council-codebase-context
description: Erstellt einen Kontextbrief über ein Projekt (Technik, Aufbau, Muster, Datenmodell, Konventionen, Grenzen, Schnittstellen) als gemeinsame Grundlage für andere Werkzeuge; für den Vault-Index als Gliederung im Chat erprobt.
metadata:
  type: reference
---

**Zweck:** Beschreibt ein Projekt schreibgeschützt, damit andere Werkzeuge darauf aufbauen können, ohne es selbst zu erkunden.

**Wann nutzen:** Vor größeren Änderungen oder bei neuen Werkzeugen, die auf ein bestehendes Projekt zugreifen. Nicht für kleine Einzeländerungen.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Angaben für einen Kontextbrief über den Vault-Index im Chat skizzieren, ohne Datei.

**Ergebnis:** Gliederung mit sieben Punkten: Zweck und Ebene, Aufbau, Index-Regeln, Werkzeuge, Regeln mit Grenzen, Pflegeablauf, bekannte Schwächen. Die bekannte Schwäche ist das Auseinanderlaufen von Index und Dateien, dazu die Zugangsdaten mit zu niedriger Stufe. Der Brief soll kurz bleiben.

**Gelernt:**
- Der Skill ist für Software mit Quellcode gebaut (Routing, Komponenten, Datenmodell). Für einen Vault passt nur die Ordnerstruktur und die Regeln. Die Abschnitte zu Datenbank und Routing entfallen.
- Der Punkt „bekannte Schwächen“ ist der wertvollste für andere Werkzeuge, weil sie sonst dieselben Fehler machen.

**Grenzen:**
- Keine Dateien gelesen, nur die Struktur aus `CLAUDE.md`.
- Nur Gliederung, kein fertiger Brief.
