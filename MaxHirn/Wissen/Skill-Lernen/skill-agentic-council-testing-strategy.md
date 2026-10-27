---
name: skill-agentic-council-testing-strategy
description: Legt Testfälle, Testdaten und Prüfung auf einer Kopie für Skripte fest, mit Trennung nach Einzelprüfung und Zusammenspiel. Für die Vault-Skripte (Ablage, Index, Sicherung) im Chat skizziert, ohne Tests auszuführen.
metadata:
  type: reference
---

**Zweck:** Stellt fest, welche Fälle ein Skript überstehen muss, bevor es an echten Daten läuft.

**Wann nutzen:** Vor dem ersten Lauf eines Skripts, das Dateien verschiebt, überschreibt oder einen Index ändert. Nicht für Einzeiler ohne Schreibzugriff.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Prüfung der Vault-Skripte skizzieren (Fälle, Testdaten, Ergebnis auf einer Kopie). Keine Tests ausgeführt, keine Datei.

**Ergebnis:** Einzelprüfung: Pfadbildung und Zeilenformat des Index. Zusammenspiel: Anfügen an den Index, Verschieben, Sicherung davor. Fälle: leere Indexdatei, Umlaute im Titel, doppelte Kennung, fehlende Endzeile, Zielordner bereits vorhanden. Testdaten: eine Kopie des Index und ein Ordner mit Dummy-Notizen in einem Temp-Ordner. Ein Test auf der Kopie zeigt den Fehlerfall ohne Risiko für die echten Daten.

**Gelernt:**
- Der häufigste Fehler liegt in der Endzeile der Indexdatei und im Pfadformat, nicht in der Logik.
- Eine Kopie als Testziel ist der einzige sichere Weg, Schreibfehler zu provozieren.

**Grenzen:**
- Keine Tests ausgeführt, keine Skripte gelesen.
- Der Skill verlangt Testpyramide, Abdeckungsziele und Qualitätstore in CI. Für einzelne Skripte ohne Build entfallen diese Teile.
