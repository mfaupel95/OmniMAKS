---
name: skill-agentic-council-ml-workflow
description: Plant ein maschinelles Lernen von der Problemdefinition über Merkmale, Experimente, Training, Bereitstellung, Vergleichstest und Überwachung; für die Frage nach einem lokalen Sprachmodell für Notizen im Chat als Entscheidung für Stichwortsuche erprobt.
metadata:
  type: reference
---

**Zweck:** Legt einen ML-Ablauf fest: was das Modell vorhersagen soll, welche Merkmale es braucht, wie Experimente nachvollziehbar bleiben, wie es bereitgestellt und überwacht wird.

**Wann nutzen:** Wenn ein Modell trainiert oder betrieben werden soll und dauerhaft Qualität liefern muss. Nicht, wenn ein fertiges Modell nur einmal befragt wird.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Lohnt sich ein kleines lokales Sprachmodell zur Zusammenfassung von Notizen oder reicht eine Stichwortsuche, im Chat, ohne Training.

**Ergebnis:** Stichwortsuche als Standard. Ein lokales Modell nur auf Anfrage, für einzelne lange Notizen, mit Verweis auf die Quelle, ohne Speichern. Kein Durchlauf über das Archiv ohne ausdrückliche Entscheidung. Prüfsatz mit bekannten Antworten vor dem Einsatz. Offen: ob Zusammenfassungen überhaupt gebraucht werden.

**Gelernt:**
- Die Problemdefinition ist der wichtigste Schritt des Skills. Ohne Zielgröße gibt es keine Bewertung. Für Notizen fehlt sie, und das ist der eigentliche Grund, nicht das Modell.
- Die Zusammenfassung ist nicht die Quelle. Das Modell kann Aussagen verschieben, deshalb braucht jede Ausgabe einen Verweis auf die Originalstelle.

**Grenzen:**
- Kein Training, kein Modell getestet, nicht geprüft, welche Modelle auf dem Rechner laufen.
- Die Empfehlung beruht auf allgemeinen Erfahrungen mit Sprachmodellen, nicht auf Messungen für diesen Vault.
- Der Skill verlangt Trainingspipelines, Modellregister und Drift-Überwachung. Für eine Notizsuche ohne Training sind diese Punkte nicht anwendbar.
