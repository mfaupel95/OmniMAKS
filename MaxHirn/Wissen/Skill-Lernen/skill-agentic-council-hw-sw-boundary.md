---
name: skill-agentic-council-hw-sw-boundary
description: Prüft die Grenze zwischen Hardware-Sicherheit und Software-Konfiguration (Speicherschutz, Speicherzugriffe, Startkette, Vertrauensmodell); für BitLocker auf dem Sicherungslaufwerk im Chat als Schlüsselübersicht erprobt.
metadata:
  type: reference
---

**Zweck:** Stellt sicher, dass Hardware-Schutzfunktionen tatsächlich eingeschaltet sind und dass das Vertrauensmodell von der Startkette bis zum Betriebssystem zusammenpasst.

**Wann nutzen:** Bei Systemen mit eigenem Betriebssystem-Kern oder Firmware-Konfiguration. Nicht für Anwendungen, die nur Verschlüsselung über ein fertiges Werkzeug nutzen.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Grenze zwischen Hardware und Software bei BitLocker und die Verteilung der Schlüssel im Chat skizzieren, ohne Konfiguration zu lesen.

**Ergebnis:** Software verschlüsselt den Datenträger (AES-XTS). Das TPM hält den Hauptschlüssel, gebunden an den Startzustand des Rechners. Der Wiederherstellungsschlüssel öffnet den Datenträger unabhängig vom TPM und ist der schwächste Punkt. BitLocker To Go auf dem externen Laufwerk nutzt ein Passwort oder eine Smartcard. Offen: ob das externe Laufwerk BitLocker To Go nutzt und wo der Wiederherstellungsschlüssel liegt.

**Gelernt:**
- Der Skill beschreibt Kernel- und Firmware-Schutz. Für BitLocker zählt vor allem die Frage, wer den Wiederherstellungsschlüssel hat. Das ist keine Kernel-Frage, aber die entscheidende.
- Die Hardwareschicht schützt nur an einem Gerät. Bei einem Datenträger, der an einen anderen Rechner angeschlossen wird, fällt sie weg.

**Grenzen:**
- Nur Chat-Skizze, keine Datei, keine Konfiguration oder Schlüssel gelesen.
- Die Details zu TPM und FVEK beruhen auf allgemeinem Wissen zu BitLocker, nicht auf einer Prüfung dieses Rechners.
- Der Skill verlangt Speicherschutz-Funktionen wie PAC oder MTE. Für einen Windows-Rechner mit BitLocker ist das nicht anwendbar.
