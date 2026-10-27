---
name: skill-agentic-council-api-design
description: Entwirft Endpunktverträge mit Typen, Fehlerformat, Auth, Paginierung und Caching für eine Schnittstelle; im Chat als Abfrage-Entwurf für den Vault-Index erprobt.
metadata:
  type: reference
---

**Zweck:** Legt die Verträge zwischen Oberfläche und Dienst fest: Pfade, Methoden, Typen, Fehlercodes, Berechtigungen, Paginierung und Caching.

**Wann nutzen:** Wenn ein Dienst mehrere Clients bedient oder ein Vertrag zwischen Teilen eines Systems stabil bleiben muss. Nicht für interne Funktionsaufrufe.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Abfrage-Schnittstelle für den Vault-Index im Chat skizzieren, ohne Datei.

**Ergebnis:** Entwurf mit zwei Endpunkten (Suche nach Titel, Liste nach Schlagwort), einem Fehlertyp und begründetem Verzicht auf Paginierung (Index rund 320 Zeilen) und Auth (nur lokal). Die Frage, ob ein Werkzeug diese Schnittstelle überhaupt braucht, bleibt offen, weil die Suche heute über das Archiv-Werkzeug läuft.

**Gelernt:**
- Für einen kleinen, lokalen Bestand ist die Schnittstelle als Vertrag übertrieben. Der Skill fordert trotzdem Fehlercodes und Typen. Das ist gut, um die Form festzuhalten, aber den Aufwand sollte man vorher abwägen.
- Die Schlagwortliste im Index ist kontrolliert. Das lässt sich als Aufzählungstyp abbilden, was den Vertrag stabil hält.

**Grenzen:**
- Nur Entwurf im Chat, keine Datei und kein Code.
- Keine Prüfung gegen einen bestehenden Dienst. Der Skill sieht vor, Routen zu inventarisieren; das war hier nicht möglich.
