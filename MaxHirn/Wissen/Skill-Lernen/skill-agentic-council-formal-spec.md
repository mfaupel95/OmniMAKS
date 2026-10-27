---
name: skill-agentic-council-formal-spec
description: Formalisiert ein System als Zustände, Übergänge und Eigenschaften (Sicherheit, Lebendigkeit) mit Annahmen und Grenzen; für den Lebenszyklus einer Notiz im Vault-Index als kleine Zustandsbeschreibung im Chat erprobt.
metadata:
  type: reference
---

**Zweck:** Übersetzt informelle Anforderungen in prüfbare Eigenschaften über Zustände und Übergänge, damit Fehler im Ablauf auffallen, bevor sie passieren.

**Wann nutzen:** Bei Abläufen mit Nebenläufigkeit oder sicherheitskritischen Zusagen, etwa Zugriffskontrolle oder Konsistenz zwischen zwei Speichern. Nicht für Abläufe ohne Zustandswechsel.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Zustände und Übergänge für den Ablauf „Notiz anlegen, ändern, löschen“ im Chat skizzieren, ohne Datei.

**Ergebnis:** Vier Zustände (Fehlt, Ungelistet, Gelistet, Veraltet), fünf Übergänge. Eigenschaften: nie ein Index-Eintrag ohne Datei, irgendwann jede Ungelistet-Notiz eingetragen (unter der Annahme laufender Pflege). Offen: ob Löschen und Eintragen in einem Schritt erfolgen. Eine vollständige TLA+-Datei wurde für einen Index als zu groß verworfen.

**Gelernt:**
- Die wichtigste Eigenschaft ist die Sicherheitseigenschaft „nie tote Verweise“. Sie zeigt, dass Löschen und Eintrag im selben Schritt stehen müssen.
- Lebendigkeit hängt an einer Annahme über Pflege. Der Skill verlangt diese Annahme ausdrücklich, und das ist richtig so.

**Grenzen:**
- Keine TLA+-Datei geschrieben, kein Modellprüfer ausgeführt.
- Die Zustände sind eine Vereinfachung. Zwischen Läufen des Vault-Prüfers ist der Zustand unbekannt, was die Modellierung nicht erfasst.
- Der Skill ist auf Verifikation gebaut. Für eine Notizverwaltung genügt die Zustandsliste.
