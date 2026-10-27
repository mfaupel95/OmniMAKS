---
name: skill-agentic-council-protocol-analysis
description: Modelliert ein Protokoll als Zustandsmaschine und prüft Wiederholung, Abweichung der Zustände, Sitzungsbindung und Herabstufung. Für den Abgleich zwischen Rechner und Cloud-Synchronisation des Vaults im Chat skizziert, ohne Verbindung zu prüfen.
metadata:
  type: reference
---

**Zweck:** Zeigt, wo zwei Seiten beim Austausch auseinanderlaufen können und wie sich ein Angreifer oder ein Fehler einschleichen würde.

**Wann nutzen:** Bei eigenen oder unbekannten Protokollen mit Zustandsübergängen. Nicht für einen einzelnen Aufruf ohne Antwort.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: beteiligte Protokolle beim Abgleich zwischen Rechner und Cloud-Synchronisation skizzieren und prüfen. Keine Datei, keine Verbindung untersucht.

**Ergebnis:** Beteiligt sind verschlüsselte Verbindungen (HTTPS mit TLS) zum Dienst, die Anmeldung am Konto, das proprietäre Abgleichprotokoll des Dienstes und lokale Dateiereignisse. Prüfpunkte: Konfliktregel bei gleichzeitiger Änderung (Zeitstempel, Kopie), Wiederholung nach Abbruch ohne doppelte Übernahme, Herabstufung der TLS-Version, Gerätebindung der Anmeldung, Verhalten bei abgebrochener Sitzung. Die Regeln des Dienstes sind in dieser Sitzung nicht gelesen worden.

**Gelernt:**
- Die Konfliktregel ist der Teil, der Daten kostet, nicht die Verschlüsselung. Eine Verbindung kann sicher sein und trotzdem eine Datei still überschreiben.
- Eine Wiederholung nach Abbruch muss idempotent sein; sonst entstehen Doppelungen im Index.

**Grenzen:**
- Dienst und Abgleichprotokoll nicht gelesen, keine Verbindung geprüft.
- Der Skill verlangt eine vollständige Zustandsmaschine mit Verifikation. Für einen Abgleich eines Ordners genügen die fünf Prüfpunkte.
