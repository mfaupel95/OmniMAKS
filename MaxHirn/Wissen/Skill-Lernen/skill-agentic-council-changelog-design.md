---
name: skill-agentic-council-changelog-design
description: Entwirft Versionsprotokolle mit Änderungskategorien, Migrationsanleitungen, Versionsstrategie und Mitteilungsplan für Verbraucher; für den Vault-Index als Entscheidung gegen Versionsnummern erprobt.
metadata:
  type: reference
---

**Zweck:** Macht Änderungen für Verbraucher nachvollziehbar: Kategorien (Bruch, Funktion, Fehlerbehebung), Migrationsschritte mit Beispielen, Versionsnummer nach Semver und Mitteilungsplan.

**Wann nutzen:** Wenn ein Produkt oder eine Bibliothek von anderen eingebunden wird und Brüche auf deren Seite Arbeit verursachen. Nicht für interne Dateien ohne externe Nutzer.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Prüfen, ob der Vault-Index ein Änderungsprotokoll mit Versionsnummern braucht, im Chat, ohne Datei.

**Ergebnis:** Nein. Der Vault-Index hat keine externen Verbraucher, die sich auf eine Version verlassen. Git hält die Historie bereits fest. Eine Umbenennung in `INDEX.md` bricht nur Werkzeuge mit festem Pfad. Minimalschutz, falls ein Werkzeug den Index einbindet: eine Zeile „Format-Version“ im Kopf der Datei.

**Gelernt:**
- Der Skill setzt Verbraucher mit Versionsbindung voraus. Diese Voraussetzung prüft er nicht selbst. Der erste Schritt bei jedem Lauf sollte die Frage sein, wer die Ausgabe nutzt.
- Ein Protokoll mit Versionen ist für Werkzeuge gedacht, die den Stand fest einbinden. Bei einem einzelnen Nutzer ersetzt Git das weitgehend.

**Grenzen:**
- Nur Entscheidung im Chat, keine Datei.
- Die Frage nach einem Änderungsprotokoll für den Index selbst bleibt aus der Skizze zum Änderungsprotokoll offen.
