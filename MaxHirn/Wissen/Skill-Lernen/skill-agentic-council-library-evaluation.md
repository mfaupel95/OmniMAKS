---
name: skill-agentic-council-library-evaluation
description: Vergleicht Bibliotheken gewichtet nach Abhängigkeiten, Pflege, Lizenz, Funktionsumfang und Umlauten; für die Volltextsuche des Vault-Index im Chat erprobt (SQLite FTS5 gegen Whoosh), ohne Installation und ohne Live-Daten.
metadata:
  type: reference
---

**Zweck:** Macht eine Abhängigkeitsentscheidung nachvollziehbar: Kandidaten, Kriterien mit Gewicht, Bewertung und Empfehlung mit Risiken.

**Wann nutzen:** Vor dem Hinzufügen einer Abhängigkeit, die später schwer zu entfernen ist. Nicht für Bibliotheken, die man einmalig ausprobiert.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Whoosh und SQLite FTS5 für die Volltextsuche des Vault-Index im Chat bewerten, ohne Installation.

**Ergebnis:** Empfehlung SQLite FTS5, weil es ohne zusätzliches Paket auskommt und Pflege und Lizenz gut sind. Der wichtigste Befund: Für den Index selbst (rund 320 Zeilen) braucht es keine Bibliothek. Für das Archiv gibt es schon `ArchivSuche`. Entscheidung: keine neue Bibliothek. Pflegezustand von Whoosh nicht live geprüft.

**Gelernt:**
- Der Skill fragt zuerst nach dem Bedarf. Der Befund „keine Bibliothek nötig“ ist für den Vault wertvoller als der Vergleich selbst.
- Eine zweite Suche neben einer bestehenden erzeugt einen zweiten Index, der auseinanderlaufen kann.

**Grenzen:**
- Keine Live-Daten zu Downloads, Commits oder Lizenzen abgerufen. Die Pflegeeinschätzung von Whoosh ist ungeprüft.
- Keine Installation, keine Messung.
- Der Skill verlangt Downloadzahlen und Bündelgrößen, die für Python-Bibliotheken auf dem Rechner nicht gelten.
