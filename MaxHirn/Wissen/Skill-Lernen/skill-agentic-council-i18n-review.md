---
name: skill-agentic-council-i18n-review
description: Prüft Lokalisierungsbereitschaft (Zeichenkodierung, Sprachwahl, Sortierung, Formate). Für Deutsch und Englisch sowie Umlaute in Notiznamen und Texten des Vaults im Chat als Regelvorschlag erprobt, ohne Dateien zu prüfen.
metadata:
  type: reference
---

**Zweck:** Stellt fest, ob Inhalte in mehreren Sprachen und Zeichensätzen verlässlich gelesen, gesucht und sortiert werden.

**Wann nutzen:** Wenn Inhalte in mehr als einer Sprache entstehen oder zwischen Systemen mit unterschiedlicher Kodierung wandern. Nicht für einsprachige Ablagen ohne Export.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Umgang des Vaults mit Deutsch und Englisch sowie Umlauten in Notiznamen und Texten skizzieren. Keine Datei, nichts geprüft.

**Ergebnis:** Texte bleiben auf Deutsch mit Umlauten, UTF-8 ohne BOM. Bezeichner in Skripten, Frontmatter-Schlüssel und Pfade bleiben englisch oder ASCII. Dateinamen ohne Umlaute (ae, oe, ue, ss) und ohne reine Groß- und Kleinschreibungsunterschiede, weil Umzüge auf andere Systeme sonst brechen. Datum im Index als ISO-Format. Schweregrad mittel: vorhandene Notiznamen mit Umlauten bleiben, neue folgen der Regel.

**Gelernt:**
- Die Trennung ist nicht Sprache gegen Sprache, sondern Anzeige gegen Kennung. Umlaute gehören in den Text, nicht in den Pfad.
- Die Regel aus dem Notiz-Skill und der Bestand widersprechen sich. Vor einer Umbenennung braucht es eine Entscheidung, nicht eine stille Änderung.

**Grenzen:**
- Keine Dateinamen gelesen, keine Kodierung geprüft.
- Der Skill verlangt Übersetzungsdateien, Pluralregeln und RTL-Layout. Für einen deutschen Vault entfallen diese Teile.
