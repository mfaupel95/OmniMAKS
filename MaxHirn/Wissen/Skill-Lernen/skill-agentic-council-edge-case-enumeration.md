---
name: skill-agentic-council-edge-case-enumeration
description: Listet Randfälle je Bereich (Eingabe, Zustand, Gleichzeitigkeit, Zeit, Rechte) mit erwartetem Verhalten und Priorität; für die Suche im Vault-Index im Chat erprobt.
metadata:
  type: reference
---

**Zweck:** Findet Randfälle systematisch durch Grenzwerte, Zustandskombinationen, Gleichzeitigkeit, Zeitfragen und Rechte, und ordnet jedem Fall ein erwartetes Verhalten und eine Priorität zu.

**Wann nutzen:** Vor der Umsetzung einer Funktion mit Eingabe und Zustand. Nicht für rein statische Ausgaben ohne Eingabe.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Randfälle für die Suche im Vault-Index im Chat aufzählen, ohne Datei.

**Ergebnis:** Dreizehn Randfälle in fünf Bereichen. Drei davon mit P0: Einträge mit toten Pfaden, gleichzeitiges Schreiben von Max und Skills, sowie P1 für Umlaut-Schreibweisen. Nicht geprüft wurden Suchcode und tatsächlicher Dateizustand.

**Gelernt:**
- Die Liste lebt von den Bereichen. Ohne Gleichzeitigkeit und tote Verweise würde man beim Index die wichtigsten Fehler übersehen.
- Die Umlaut-Frage ist bei Windows-Dateien meist harmlos, weil Dateinamen meist in NFC vorliegen. Dass Eingaben anders kodiert sind, kann trotzdem vorkommen.

**Grenzen:**
- Keine Tests, keine Suchfunktion gelesen.
- Die Prioritäten sind Einschätzungen, keine Messungen.
- Der Skill verlangt mindestens fünf Fälle je Bereich. Das wurde nicht überall erreicht, weil viele Bereiche für einen Index nicht zutreffen.
