---
name: skill-agentic-council-load-modeling
description: Modelliert Lastprofile, Engpässe, Skalierungsgrenzen, Lasttests und Kostenprognosen für Dienste mit vielen Nutzern; für die Suchlast des Vault-Index im Chat als Schätzung ohne Kapazitätsplanung erprobt.
metadata:
  type: reference
---

**Zweck:** Plant, wie ein Dienst wachsende Last aufnimmt: Verkehrsmuster, Engpässe bei Datenbank, Rechenleistung und Netz, Skalierungsschwellen und Testläufe.

**Wann nutzen:** Bei Diensten mit vielen gleichzeitigen Nutzern oder Lastspitzen, die Kapazität kosten. Nicht für Werkzeuge mit einem einzigen Nutzer.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Suchlast des Vault-Index im Chat schätzen und prüfen, ob Kapazitätsplanung nötig ist, ohne Lasttest.

**Ergebnis:** Schätzung einige Dutzend bis wenige Hundert Suchen am Tag, jede liest eine Datei mit rund 320 Zeilen. Kapazitätsplanung ist nicht nötig. Die Grenze liegt bei der Größe des Index, nicht bei der Anzahl der Suchen. Erst bei Tausenden Einträgen lohnt eine Prüfung, dieselbe Schwelle wie beim Cache. Die Zahl der Suchen ist eine Annahme, keine Messung.

**Gelernt:**
- Der Skill fragt nach dem Lastprofil, das für den Vault nicht existiert. Die nützlichste Erkenntnis ist die Frage, welcher Wert überhaupt wachsen kann: hier die Größe, nicht die Last.
- Ein Ein-Nutzer-Werkzeug hat keine Skalierungsschwelle, die es erreichen könnte.

**Grenzen:**
- Die Suchzahl beruht auf einer Schätzung, nicht auf Messung.
- Keine Lasttests, keine Infrastruktur geprüft.
- Der Skill verlangt Kostenprognosen und Benchmarks für Dienste, die es für den Vault nicht gibt.
