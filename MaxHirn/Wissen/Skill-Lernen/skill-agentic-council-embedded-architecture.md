---
name: skill-agentic-council-embedded-architecture
description: Entwirft Firmware-Architektur für Mikrocontroller (Hardware, Echtzeitbetriebssystem, Aufgaben, Speicher, Energiezustände, Watchdog); für einen einfachen Temperatursensor im Chat als Entscheidung gegen eigene Architektur erprobt.
metadata:
  type: reference
---

**Zweck:** Legt fest, wie Firmware für ein eingebettetes Gerät aufgebaut wird: Hardwarebedarf, Betriebssystem oder ohne, Aufgabenaufteilung, Speicherplan, Energiezustände und Ausfallschutz.

**Wann nutzen:** Bei Geräten mit mehreren gleichzeitigen Aufgaben, Akkubetrieb mit langer Laufzeit oder Anforderungen an Aktualisierung aus der Ferne. Nicht für einzelne Sensoren mit fester Standard-Firmware.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: prüfen, ob ein Mikrocontroller für einen Temperatursensor eine eigene Architektur braucht oder ein fertiges Gerät reicht, im Chat, ohne Datei.

**Ergebnis:** Für einen einzelnen Temperatursensor keine eigene Architektur. Empfehlung in drei Stufen: fertiges Gerät, wenn die Daten in einer bestehenden App landen; Standard-Firmware (z. B. ESPHome auf dem ESP32), wenn die Daten selbst verarbeitet werden; eigene Architektur erst bei mehreren Sensoren, Akkulaufzeit unter einem Jahr oder hohen Ausfallanforderungen.

**Gelernt:**
- Der Skill beginnt mit Hardware und endet bei Watchdog. Für einen einfachen Sensor ist die Konfiguration einer Standard-Firmware der eigentliche Architekturschritt.
- Die Frage „fertiges Gerät oder Eigenbau“ kommt im Skill nicht vor. Sie sollte vor jedem Einsatz des Skills stehen.

**Grenzen:**
- Nur Entscheidung im Chat, keine Datei und kein Code.
- Keine konkrete Hardware geprüft. Die Angaben zu ESPHome beruhen auf allgemeinem Wissen, nicht auf einer Prüfung.
