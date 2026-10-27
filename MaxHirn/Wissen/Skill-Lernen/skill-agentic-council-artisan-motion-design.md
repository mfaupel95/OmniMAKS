---
name: skill-agentic-council-artisan-motion-design
description: Legt Bewegungssprache fest (Dauer, Kurve, Reihenfolge, Alternative bei reduzierter Bewegung). Für die Frage, ob Animation in der Terminal-Ausgabe von Claude Code sinnvoll ist, im Chat erprobt, ohne Code.
metadata:
  type: reference
---

**Zweck:** Entscheidet, wo Bewegung Bedeutung trägt, und legt Dauer und Alternative fest.

**Wann nutzen:** Bei grafischen Oberflächen mit Übergängen und Rückmeldungen. Nicht für statische Ausgaben.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Bewegung in der Terminal-Ausgabe von Claude Code skizzieren, ob sinnvoll oder störend. Keine Datei.

**Ergebnis:** Im Terminal ist Bewegung außer einem Ladeindikator kaum sinnvoll. Ausgaben werden kopiert, durchsucht und in Protokollen gelesen, Animation stört dabei. Empfehlung: Ladeindikator behalten, weil er Zustand zeigt; keine weiteren Übergänge. Falls eine Oberfläche entsteht, Bewegung nur mit Alternative bei reduzierter Bewegung und unter fünfhundert Millisekunden.

**Gelernt:**
- Bewegung ist Information nur, wenn sie einen Zustand anzeigt. Ein Spinner zeigt Arbeit, ein Einblenden zeigt nichts.
- Im Text-Medium ist die beste Bewegung keine.

**Grenzen:**
- Keine Oberfläche geprüft, kein Code gelesen.
- Der Skill verlangt Bildraten, Compositing und Choreografie. Für ein Terminal sind diese Punkte nicht anwendbar.
