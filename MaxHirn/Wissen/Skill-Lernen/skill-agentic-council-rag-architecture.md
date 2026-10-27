---
name: skill-agentic-council-rag-architecture
description: Entwirft eine Abrufkette (Dokumente zerlegen, einbetten, suchen, neu ordnen, antworten) mit Kosten und Qualitätsmaßen. Für die Frage, ob eine Suche über den Vault mit Sprachmodell oder eine Stichwortsuche reicht, im Chat erprobt.
metadata:
  type: reference
---

**Zweck:** Prüft, ob eine Antwort aus Dokumenten Abruf plus Sprachmodell braucht, und beschreibt die Kette, falls ja.

**Wann nutzen:** Wenn Fragen in freier Form an große Dokumentbestände gestellt werden. Nicht, wenn Begriffe gesucht werden, die im Text vorkommen.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Vault mit Sprachmodell (Abruf vor Antwort) gegen Stichwortsuche abwägen. Keine Datei, keine Einbettung erstellt.

**Ergebnis:** Der Vault hat rund zweihundert bis dreihundert kurze Notizen. Stichwortsuche auf Titel, Dateiname und Beschreibungszeile trifft die meisten Fragen. Empfehlung: Stichwortsuche als Standard, Umlaute und Schreibvarianten normalisieren. Ein Sprachmodell nur für einzelne, bereits gefundene Notizen zum Zusammenfassen mit Textstelle. Eine Einbettungsdatenbank lohnt erst, wenn Fragen regelmäßig ohne Stichwort gestellt werden.

**Gelernt:**
- Die Beschreibungszeile im Frontmatter ist das beste Suchfeld, das schon existiert. Sie kostet nichts extra.
- Abruf mit Sprachmodell verlagert das Problem auf die Auswahl der Ausschnitte. Bei wenigen Notizen ist das nicht nötig.

**Grenzen:**
- Keine Einbettung erstellt, keine Suchqualität gemessen.
- Der Skill verlangt Einbettungsmodelle, Vektordatenbanken, Neuordnung und Kostenmodelle. Für diesen Umfang entfällt der größte Teil.
