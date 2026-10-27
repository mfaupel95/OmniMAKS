---
name: skill-agentic-council-isolation-review
description: Kartiert Abgrenzungen zwischen Vertrauensbereichen, prüft Übergänge und Durchsetzung und sucht Umgehungswege; für die Trennung von Vault, Archiv und Werkstatt im Chat als Prüfplan ohne Schreibtest erprobt.
metadata:
  type: reference
---

**Zweck:** Stellt fest, welche Bereiche sich gegenseitig abschirmen, an welchen Stellen Daten hinübergehen und ob die Abschirmung durch Technik oder nur durch Absprache gilt.

**Wann nutzen:** Bei Systemen mit Bereichen unterschiedlichen Vertrauens, etwa Produktion und Entwicklung oder private und geteilte Daten. Nicht für einzelne Programme ohne Abgrenzung.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Prüfung der Trennung zwischen Vault, Archiv und Werkstatt im Chat skizzieren, ohne Schreibtest.

**Ergebnis:** Drei Prüfpunkte: Schreibrechte am Dateisystem nur lesen, Schreibpfade je Werkzeug aus den Konfigurationen, Git-Whitelist ohne Archivinhalte. Ein Probeschreiben ins Archiv wurde als Verletzung der Trennung ausgeschlossen. Befund: Die Trennung gilt in der Regel, technisch durchgesetzt ist sie nur, wenn die Rechte am Dateisystem sie tragen. Nicht geprüft.

**Gelernt:**
- Die Regel auf dem Papier ist nicht die Durchsetzung. Das Gegenmittel ist eine Prüfung der Rechte, nicht ein Test durch Schreiben.
- Der wahrscheinlichste Bruch ist die Git-Whitelist. Eine Ausnahme dort öffnet Archivdaten für das Repository, ohne dass es auffällt.

**Grenzen:**
- Nur Chat-Skizze, keine Datei, keine Konfiguration gelesen.
- Der Skill verlangt Angriffstests. Für eine lokale Trennung ist ein Rechtecheck ausreichend und angemessener.
