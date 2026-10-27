---
name: skill-agentic-council-pipeline-design
description: Entwirft Datenabläufe von der Quelle bis zum Ziel mit Musterwahl, Stapel oder Strom, Wiederholbarkeit, Qualitätsprüfungen, Herkunft und Auslösung; für das Einsortieren des Posteingangs und die Indexpflege im Chat als sieben Schritte erprobt.
metadata:
  type: reference
---

**Zweck:** Legt fest, wie Daten gelesen, verarbeitet und abgelegt werden: Schritte, Prüfungen zwischen den Schritten, Verhalten bei Wiederholung und Fehlern, Nachverfolgbarkeit der Herkunft.

**Wann nutzen:** Bei wiederkehrenden Abläufen, die Daten zwischen Speichern bewegen und dabei Fehler machen können. Nicht für einzelne Handgriffe.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Ablauf für das Einsortieren des Posteingangs und die Indexpflege im Chat skizzieren, ohne Datei.

**Ergebnis:** Sieben Schritte: Erfassen, Einordnen, Testlauf, Verschieben, Index aktualisieren, Gegenprüfung. Fehlerfall: Protokoll aller Verschiebungen vorher schreiben, Index erst am Ende ändern. Wiederholung: bereits verschobene Dateien fallen aus der Liste. Kein Orchestrator nötig, manueller Aufruf genügt. Offen: fester Ort für das Protokoll.

**Gelernt:**
- Die wichtigste Regel ist die Reihenfolge: erst das Protokoll, dann die Bewegung, und den Index zuletzt. So bleibt jeder Schritt rückgängig zu machen.
- Der Skill fragt nach Datenströmen und Orchestratoren. Für eine Menge von wenigen Dutzend Dateien am Tag ist das überdimensioniert.

**Grenzen:**
- Nur Chat-Skizze, keine Datei, nichts verschoben.
- Die Regeln von `sort_inbox.py` nicht gelesen, die Einordnung ist deshalb allgemein.
- Musterwahl (Stapel gegen Strom, ETL gegen ELT) ist nicht sinnvoll, weil es keine Datenbank gibt.
