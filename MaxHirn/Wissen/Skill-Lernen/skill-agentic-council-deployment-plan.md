---
name: skill-agentic-council-deployment-plan
description: Plant die Auslieferung von Änderungen über Umgebungen mit Prüfstufen, Umstellung, Rückweg, Funktionsschaltern und Datenbank-Migration; für die Sicherungsskripte des Vaults als dreistufiger Ausrollplan im Chat erprobt.
metadata:
  type: reference
---

**Zweck:** Legt fest, wie eine Änderung von der Entwicklung bis in den Betrieb kommt: Umgebungen, Pipeline, Umstellungsstrategie, Rückweg, Gesundheitsprüfungen und Migration.

**Wann nutzen:** Bei Diensten mit Nutzern oder Diensten, die nicht ohne Risiko neu gestartet werden können. Für einzelne Skripte mit Rückweg reicht oft ein kleiner Ausrollplan.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Ausrollen einer Änderung an den Sicherungsskripten des Vaults (Test, Probelauf, Rückweg), im Chat, ohne Datei.

**Ergebnis:** Dreistufiger Ausrollplan. Stufe 1: Test in einem Probeordner, möglichst mit einer Trockenlauf-Option. Stufe 2: Probelauf nur an der Zweitkopie, Vergleich von Dateizahl und Größe mit dem letzten Lauf. Stufe 3: Umstellung mit datiertem Backup der alten Fassung. Rückweg: Backup zurückkopieren. Ob die Skripte eine Trockenlauf-Option haben, ist nicht geprüft.

**Gelernt:**
- Die Stufen des Skills (Umgebungen, Pipeline, Funktionsschalter) sind für Teams gebaut. Für Skripte auf einem Rechner bleibt der Kern: Probelauf, Vergleich, Rückweg.
- Der Rückweg muss die Frage beantworten, was schon geschrieben wurde. Bei Sicherungen ist das der heikle Punkt.

**Grenzen:**
- Die Skripte wurden nicht gelesen. Die Annahme zu bereits geschriebenen Sicherungen ist ungeprüft.
- Keine Datenbank-Migration im Spiel, deshalb entfallen diese Pflichtpunkte.
