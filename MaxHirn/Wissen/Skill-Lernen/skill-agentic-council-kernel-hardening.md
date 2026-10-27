---
name: skill-agentic-council-kernel-hardening
description: Prüft die Härtung eines Betriebssystem-Kerns (Speicherschutz, Systemaufrufe, Integrität, Module); für einen Windows-Rechner mit Vault im Chat als Maßnahmenliste erprobt, ohne Kernel-Prüfung.
metadata:
  type: reference
---

**Zweck:** Prüft, ob ein Betriebssystem-Kern so konfiguriert ist, dass Angriffe auf Speicher, Systemaufrufe und Module erschwert werden, und ob die Schutzmechanismen zur Laufzeit wirken.

**Wann nutzen:** Bei eigenen Kernen oder Servern mit Linux-Konfiguration. Nicht für Desktop-Rechner, deren Schutz über Betriebssystem-Einstellungen läuft.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Härtungsmaßnahmen für den Windows-Rechner, die den Vault schützen, im Chat skizzieren, ohne Datei.

**Ergebnis:** Maßnahmenliste mit sieben Bereichen: Rechte (Alltagskonto, Archivordner nur für das eigene Konto), Dienste (Fernzugriff nur bei Bedarf), Verschlüsselung (BitLocker intern und extern), Updates, Anmeldung, Protokoll. Die Kernel-Maßnahmen des Skills entfallen, weil sie für Linux-Kerne gelten. Wichtigster Punkt: Verschlüsselung und Rechte. Nicht geprüft: Konten und laufende Dienste des Rechners.

**Gelernt:**
- Der Skill ist auf Linux-Kerne zugeschnitten. Auf Windows lässt sich die Grundidee übertragen: Speicherschutz und Modulsignatur entsprechen Systemeinstellungen, nicht Kernel-Optionen.
- Die Rechtetrennung war der größte Gewinn. Ein Alltagskonto ohne Administratorrechte begrenzt den Schaden von Schadsoftware am stärksten.

**Grenzen:**
- Keine Konfiguration des Rechners gelesen, nichts geprüft.
- Die Maßnahmen beruhen auf allgemeinem Wissen zu Windows-Sicherheit.
- Der Skill verlangt eine Kernel-Konfigurationsdatei. Die gibt es für Windows nicht in dieser Form.
