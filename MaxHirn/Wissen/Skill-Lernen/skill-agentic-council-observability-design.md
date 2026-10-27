---
name: skill-agentic-council-observability-design
description: Legt Kennzahlen, Schwellen und Warnungen fest, mit denen ein Ablauf seinen eigenen Fehlerzustand zeigt. Für den Skill-Lern-Ablauf (Zählung, Dubletten, fehlende Notizen) im Chat skizziert, ohne Abgleich auszuführen.
metadata:
  type: reference
---

**Zweck:** Macht sichtbar, wenn ein Ablauf auseinanderläuft, bevor jemand es von Hand bemerkt.

**Wann nutzen:** Wenn ein Ablauf über längere Zeit läuft und Ergebnisse an mehreren Stellen ablegt. Nicht für einen einmaligen Vorgang.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Signale des Skill-Lern-Ablaufs skizzieren, die Fehler zeigen. Keine Datei, kein Abgleich ausgeführt.

**Ergebnis:** Vier Signale: Anzahl Notizen gleich Anzahl Indexzeilen gleich Anzahl Fortschrittszeilen mit Status trockenlauf; keine Kennung doppelt im Index; jeder Indexpfad hat eine Datei und umgekehrt; jede Fortschrittszeile hat einen Grund oder einen Pfad. Abweichung wird als Liste gemeldet, nicht still korrigiert. Der Prüfagent vault-pruefer deckt diese Punkte bereits ab und ist der natürliche Ort dafür.

**Gelernt:**
- Ein Signal ist nur brauchbar, wenn es eine Erwartung hat. Die drei Zähler müssen gleich sein, sonst bleibt die Abweichung unbemerkt.
- Eine Warnung, die still korrigiert, verbirgt den Fehler. Der Bericht muss die Abweichung nennen.

**Grenzen:**
- Kein Abgleich ausgeführt, keine Zählwerte gelesen.
- Der Skill verlangt Metriken, Ablaufverfolgung und Bereitschaftsrufe. Für einen lokalen Ablauf reicht die Zählprüfung.
