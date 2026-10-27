---
name: skill-operations-process-optimization
description: Sucht Wartezeit, Nacharbeit, Übergaben und Handarbeit in einem Ablauf und schlägt Verkürzungen vor. Für den Skill-Lern-Ablauf im Chat skizziert.
metadata:
  type: reference
---

**Zweck:** Findet Zeit, die ein Ablauf unnötig verbraucht, und schlägt vor, sie zu sparen.

**Wann nutzen:** Wenn ein Ablauf oft wiederholt wird und sich dabei Routinen häufen. Nicht für Abläufe, die selten laufen.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Zeitfresser im Skill-Lern-Ablauf finden und Verkürzungen skizzieren. Keine Datei, nichts gemessen.

**Ergebnis:** Zeitfresser: der Index wird bei jeder Dublettenprüfung vollständig gelesen; Index- und Fortschrittszeilen werden von Hand angehängt; nach jedem Block wartet der Ablauf auf eine Bestätigung; die Trockenlauf-Vorgaben werden in jeder Aufgabe neu formuliert. Verkürzung: ein Skript, das Notiz, Indexzeile und Fortschrittszeile in einem Schritt anlegt; Bestätigung nur bei Abweichung; Aufgabenkopf als feste Vorlage.

**Gelernt:**
- Die wiederholten Vorgaben sind der größte stille Kostenfaktor, weil sie bei jedem Lauf neu gelesen werden.
- Ein Skript für drei Zeilen lohnt sich erst, wenn es oft läuft. Hier läuft es über dreißig Mal.

**Grenzen:**
- Keine Zeit gemessen, keine Skripte gebaut.
- Der Skill verlangt Wertstrommodelle und Prozessmetriken. Für einen Einzelablauf genügen Zeitfresser und Verkürzung.
