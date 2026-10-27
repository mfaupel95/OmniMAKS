---
name: skill-agentic-council-fleet-management
description: Plant die Verwaltung vieler Geräte mit Zuordnung, Stand, Aktualisierung und Konfliktbehandlung. Für einen Vault auf mehreren Rechnern des Haushalts im Chat als Gerätezuordnung mit einem führenden Gerät erprobt, ohne Synchronisation einzurichten.
metadata:
  type: reference
---

**Zweck:** Stellt sicher, dass viele Geräte denselben Stand haben und Änderungen nicht verloren gehen.

**Wann nutzen:** Wenn dieselben Daten auf mehreren Geräten bearbeitet werden. Nicht für einen einzelnen Rechner.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Vault auf mehreren Rechnern gleich halten (Gerätezuordnung, Konflikte, Stand) im Chat skizzieren. Keine Datei, keine Synchronisation eingerichtet.

**Ergebnis:** Ein Gerät ist führend und schreibt den Index. Andere Geräte lesen, bearbeiten Notizen nur über den führenden Stand. Konflikt entsteht, wenn zwei Geräte dieselbe Indexdatei ändern; das Synchronisationsprogramm legt dann eine Kopie an, die von Hand zusammengeführt werden muss. Stand wird über Zeitstempel der letzten Synchronisation geprüft. Offen: ob überhaupt mehrere Geräte im Einsatz sind.

**Gelernt:**
- Der Indexkonflikt ist der wahrscheinlichste Schaden, weil er eine Datei betrifft, die alle Einträge trägt.
- Ein führendes Gerät ist einfacher als gleichberechtigtes Schreiben auf allen Geräten.

**Grenzen:**
- Keine Geräte und keine Synchronisation geprüft.
- Der Skill verlangt Flottenbetrieb mit Zertifikaten, Firmware-Updates und Telemetrie. Für einige Rechner entfällt der größte Teil.
