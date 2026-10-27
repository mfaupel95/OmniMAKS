---
name: skill-agentic-council-pqc-readiness
description: Erfasst klassische Verschlüsselung, ersetzt sie durch quantensichere Verfahren und plant die Umstellung nach Dringlichkeit. Für verschlüsselte Datenträger und Sicherungen des Haushalts im Chat erprobt, ohne Geräte zu prüfen.
metadata:
  type: reference
---

**Zweck:** Stellt fest, welche Verfahren ein Quantencomputer brechen könnte, und in welcher Reihenfolge man sie umstellt.

**Wann nutzen:** Wenn Daten lange vertraulich bleiben müssen und ihre Schlüssel asymmetrisch geschützt sind. Nicht für Daten mit kurzer Haltbarkeit.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: prüfen, ob verschlüsselte Datenträger und Sicherungen des Haushalts eine Umstellung brauchen und wann. Keine Datei, keine Verschlüsselung geprüft.

**Ergebnis:** Symmetrische Verschlüsselung mit AES-256 bleibt nach heutigem Stand ausreichend, weil ein Quantencomputer die Schlüssellänge nur halbiert. Dringlich ist der asymmetrische Teil: Wie der Schlüssel zum Datenträger geschützt ist (Wiederherstellungsschlüssel, Hardwarechip, Konto). Dort braucht es eine Beobachtung, keine Maßnahme jetzt. Offen: welches Verfahren die Sicherung nutzt und ob der Schlüssel asymmetrisch geschützt ist.

**Gelernt:**
- Die Gefahr liegt im Schlüsselschutz, nicht in den Daten selbst. Wer das verwechselt, tauscht den falschen Teil aus.
- Ein Zeitpunkt ist ohne Bedrohungsschätzung nicht seriös zu nennen. Der Skill verlangt ihn trotzdem; hier bleibt er offen.

**Grenzen:**
- Keine Verschlüsselung geprüft, Verfahren der Sicherung unbekannt.
- Der Skill verlangt Schlüsselinventar, Protokollpfade und Migrationsphasen. Für einen Haushalt mit wenigen Datenträgern genügt die Frage nach dem Schlüsselschutz.
