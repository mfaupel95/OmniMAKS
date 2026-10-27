---
name: skill-agentic-council-architect-schema-design
description: Entwirft Tabellen, Schlüssel, Beziehungen, Indizes und Migration für eine relationale Datenbank. Für das Frontmatter der Lernnotizen (name, description, metadata.type) mit Pflichtfeldern und erlaubten Werten im Chat erprobt, ohne Datei.
metadata:
  type: reference
---

**Zweck:** Legt Felder, Typen und Regeln für strukturierte Daten fest, mit Rückweg für Änderungen.

**Wann nutzen:** Wenn Daten eine feste Form brauchen und von Werkzeugen gelesen werden. Nicht für Freitext ohne Auswertung.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Schema für das Frontmatter der Lernnotizen skizzieren. Keine Datei, keine Notiz gelesen.

**Ergebnis:** Pflichtfelder: name (muss dem Dateinamen ohne Endung entsprechen, Kleinbuchstaben mit Bindestrich), description (eine Zeile, nicht leer, möglichst unter zweihundert Zeichen), metadata.type (fester Wert reference für Lernnotizen). Keine weiteren Felder nötig. Änderungen am Schema nur mit Prüfregel im Vault-Prüfer, damit alte Notizen nicht stillschweigend ungültig werden.

**Gelernt:**
- Das Feld name ist die Verbindung zum Dateinamen. Ohne Prüfung driftet es unbemerkt, sobald eine Datei umbenannt wird.
- Ein Schema mit einem einzigen erlaubten Typwert ist eine Feststellung, kein Schema. Es lohnt sich erst, wenn mehrere Typen dazukommen.

**Grenzen:**
- Keine Notiz gelesen, keine Migration erstellt.
- Der Skill verlangt Indizes, Fremdschlüssel, Zeilensicherheit und Rückwärtsmigration. Für Textdateien ohne Datenbank entfallen diese Teile.
