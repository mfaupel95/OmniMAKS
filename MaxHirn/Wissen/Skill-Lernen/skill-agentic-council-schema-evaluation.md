---
name: skill-agentic-council-schema-evaluation
description: Bewertet ein Datenmodell nach Körnung, Muster und Abfragen. Für die Frage, ob das Zeilenformat des Vault-Index genügt oder ein Schema mit festen Feldern nötig ist, im Chat erprobt, ohne Index zu lesen.
metadata:
  type: reference
---

**Zweck:** Prüft, ob ein Datenmodell die gewünschten Abfragen mit wenigen Verknüpfungen beantwortet und Änderungen überlebt.

**Wann nutzen:** Wenn Daten von Skripten gelesen werden, mehrere Felder brauchen oder wachsen. Nicht für eine Liste mit wenigen Einträgen.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Zeilenformat des Vault-Index gegen ein Schema mit Feldern (Kennung, Titel, Pfad, Schutzstufe, Satz) abwägen. Keine Datei, Index nicht gelesen.

**Ergebnis:** Das Zeilenformat genügt für rund zweihundert bis dreihundert Einträge, solange nur Menschen lesen und einfache Suchen laufen. Ein Schema wird nötig, sobald Skripte die Felder einzeln auswerten. Empfehlung: Textformat beibehalten, Feldreihenfolge dokumentieren, Prüfung im Vault-Prüfer ergänzen. Ein Wechsel auf JSON oder YAML als Nebendatei nur, wenn ein Skript die Felder braucht.

**Gelernt:**
- Ein Schema löst das Problem der Felder, nicht das der Konsistenz. Die Konsistenzprüfung bleibt in beiden Fällen nötig.
- Ein Textformat mit festem Muster ist für Menschen am lesbarsten und für eine einfache Prüfung ausreichend.

**Grenzen:**
- Index nicht gelesen, keine Abfragen gezählt.
- Der Skill verlangt Faktentabellen, Körnung und Datenverträge. Für einen Index mit einer Zeile je Notiz entfallen diese Punkte.
