---
name: skill-agentic-council-interaction-design
description: Beschreibt Zustände, Übergänge und Zugänglichkeit einer Bedienoberfläche (leer, lädt, Treffer, Fehler, Erfolg); für Suche und Notizanlage im Vault-Index als Zustandsliste im Chat erprobt.
metadata:
  type: reference
---

**Zweck:** Legt für jedes Bedienelement fest, welche Zustände es hat, wie es zwischen ihnen wechselt und was der Nutzer in jedem Zustand sieht und tun kann.

**Wann nutzen:** Bei Oberflächen mit Eingaben, Ladezeiten und Fehlern. Nicht für reine Textausgaben ohne Bedienung.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Zustände für Suche im Vault-Index und Notizanlage im Chat skizzieren, ohne Datei.

**Ergebnis:** Suche mit sechs Zuständen (leer, lädt, Treffer, kein Treffer, Fehler, veraltet), Notizanlage mit fünf (leer, gespeichert, Eintrag fehlt, Name existiert, Fehler). Zwei Regeln: jeder Zustand hat einen Ausweg, und ein Fehler verwirft keine Eingabe. „Gespeichert“ und „Eintrag fehlt“ bleiben getrennt.

**Gelernt:**
- Die Zustandsliste zwingt dazu, den Fehlerfall zu planen. Ohne sie bleibt eine Suche bei fehlender Datei still leer, und das ist der gefährlichste Ausgang.
- Der Skill verlangt Oberflächenmerkmale wie Farben, Fokus und Tastatur. Für eine Chat-Ausgabe reicht die Zustandsebene, die übrigen Punkte entfallen.

**Grenzen:**
- Nur Chat-Skizze, keine Oberfläche gebaut, keine Datei.
- Keine Prüfung von Kontrast, Tastaturbedienung oder Bildschirmleser, weil es keine Oberfläche gibt.
