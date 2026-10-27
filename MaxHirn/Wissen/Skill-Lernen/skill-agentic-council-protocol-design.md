---
name: skill-agentic-council-protocol-design
description: Legt Nachrichtenformat, Fehlerfälle und Schreibgrenzen zwischen Systemen fest. Für den Austausch zwischen Vault und dem Archivagenten (Anfrage, Antwort, Fehler, Nur-Lese-Grenze) im Chat skizziert, ohne Agent zu prüfen.
metadata:
  type: reference
---

**Zweck:** Beschreibt, was eine Anfrage enthält, was zurückkommt, was bei einem Fehler passiert und wo der Austausch endet.

**Wann nutzen:** Wenn zwei Systeme Nachrichten austauschen und eine Seite nur lesen darf. Nicht für einen einzelnen Aufruf.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Austauschprotokoll zwischen Vault und Archivagent im Chat skizzieren. Keine Datei, Agent nicht aufgerufen.

**Ergebnis:** Anfrage: Suchbegriff oder Pfad, Anzahl der Treffer, nur Lesevorgänge. Antwort: Trefferliste mit Pfad, Ausschnitt und Schutzstufe, nie das vollständige Dokument ohne Anforderung. Fehler: Pfad nicht gefunden, Zeitüberschreitung, Archiv nicht erreichbar, jeweils mit Kennzeichen, damit der Aufrufer nicht rät. Nur-Lese-Grenze: Der Agent hat keine Schreibwerkzeuge; eine Anfrage, die Schreiben verlangt, wird abgelehnt und nicht umgedeutet.

**Gelernt:**
- Die Grenze ist am wirksamsten, wenn das Werkzeug selbst nicht schreiben kann, nicht wenn der Agent es nicht darf.
- Fehler brauchen eigene Kennzeichen, sonst wird eine fehlende Datei für eine leere Suche gehalten.

**Grenzen:**
- Agent nicht aufgerufen, Werkzeugliste nicht gegen das Protokoll geprüft.
- Der Skill verlangt Nachrichtenkodierung, Wiederholungsstrategie und Schlüsselverwaltung. Für lokale Lesezugriffe reicht das Protokoll.
