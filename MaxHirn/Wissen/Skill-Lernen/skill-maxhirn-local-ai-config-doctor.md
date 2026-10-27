---
name: skill-maxhirn-local-ai-config-doctor
description: Trockenlauf des Skills MaxHirn:local-ai-config-doctor - Konfiguration lokaler KI-Werkzeuge prüfen und reparieren; effektive Config zuerst, Befund mit Beleg, Reparatur nur bei Eindeutigkeit; Trockenlauf, nichts repariert.
metadata:
  type: reference
---

**Zweck:** Diagnostiziert und repariert die Konfiguration lokal installierter KI-Werkzeuge (Hermes, Claude Desktop, MCP-Server, Ollama, CLI-Agenten). Die Frage „welche Konfiguration gilt tatsächlich?" steht vor jeder Diagnose.

**Wann nutzen:** Bei „hilf mir X einzurichten", „Tool sieht meine MCP-Server nicht", „Modell wird nicht gefunden" und bei jedem Einrichtungswunsch, der sich als bestehende, falsch konfigurierte Installation herausstellt.

**Lauf:** 2026-10-22, trockenlauf, Aufgabe: Übersicht des Skills. Nichts repariert, nichts geschrieben, keine Konfigurationsdatei geändert.

**Ergebnis:** Skill geladen und gelesen. Acht Schritte: Zielobjekt lokalisieren, effektive Konfiguration bestimmen, eigene Selbstprüfung des Werkzeugs nutzen, Deklariertes gegen Reales prüfen, entscheiden zwischen direkt reparieren und vorlegen, reparieren (mit Backup), verifizieren, Abschlussbericht. Die Referenzen `windows-shell.md`, `tool-map.md` und das Skript `inventory.ps1` liegen im Skill-Ordner.

**Gelernt:**
- Die effektive Konfiguration wird empirisch bestimmt: dasselbe Kommando je Kontext ausführen und die Ausgaben vergleichen. Ein Beispiel im Skill zeigt ein Profil, das die elf MCP-Server der Hauptconfig nicht sieht.
- Diagnosemeldungen aus dem falschen Kontext sind wertlos. Eine Warnung wie „config.yaml not found" zuerst dem richtigen Kontext zuordnen.
- Reparatur-Schwelle: Eine Änderung gehört in die Vorlage, wenn sie sich nicht ohne „vermutlich" begründen lässt. Strukturelle Entscheidungen, Löschungen und Kosten gehen immer vor.
- Vor dem Editieren prüfen, ob die Anwendung läuft: ein laufender Prozess schreibt seinen Zustand beim Beenden zurück und überschreibt die Änderung still.
- Bei hartnäckigen Prüffehlern die Prüffunktion im Quelltext direkt aufrufen, statt der Meldung zu glauben. Der Skill nennt ein Beispiel, bei dem eine vorgeschlagene 300-MB-Installation überflüssig war.

**Grenzen:** Trockenlauf. Ob der Skill auf diesem Rechner tatsächlich Zugriff auf Konfigurationsdateien hätte (Shell über `desktop-commander` oder `windows-mcp`), wurde nicht geprüft.

**Hinweis Dublette:** Dieselbe Skill-Beschreibung ist bereits als `anthropic-skills:local-ai-config-doctor` gelaufen, Notiz `skill-anthropic-local-ai-config-doctor.md`. Beide Einträge sind inhaltlich gleich; die Zusammenführung ist Teil der offenen Dubletten-Bereinigung und nicht hier entschieden.
