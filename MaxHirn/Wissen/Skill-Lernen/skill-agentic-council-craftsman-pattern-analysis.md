---
name: skill-agentic-council-craftsman-pattern-analysis
description: Erfasst wiederkehrende Muster im Code (Benennung, Struktur, Datenzugriff, Fehlerbehandlung) und prüft neue Änderungen auf Einheitlichkeit mit Empfehlungen zum Angleichen. Für die Skripte im Vault (Ablage, Index, Sicherung) im Chat als Mustersammlung erprobt, ohne Lesen der Dateien.
metadata:
  type: reference
---

**Zweck:** Stellt fest, welche Konventionen im Bestand gelten, und zeigt, wo neuer Code davon abweicht, mit Dateibeispielen.

**Wann nutzen:** Vor einer größeren Änderung oder wenn mehrere Skripte ähnlich aussehen und ein gemeinsamer Helfer infrage kommt. Nicht für einzelne Zeilen.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: wiederkehrende Muster in den Vault-Skripten (Ablage, Index, Sicherung) im Chat skizzieren und einschätzen, ob sich eine Vereinheitlichung lohnt. Keine Datei gelesen.

**Ergebnis:** Muster aus den Arbeitsschritten dieser Sitzung, nicht aus dem Quelltext: Pfade in Git-Bash-Form (/c/...) gegenüber Windows-Python (C:/...); Schreiben als UTF-8 ohne BOM; Indexzeilen im festen Format; Sicherung als Kopie mit Datum vor jeder Änderung; Probelauf vor dem Schreiben. Vorschlag: ein kleiner gemeinsamer Helfer für Index-Anfügen und Sicherung, nur wenn mehr als zwei Skripte ihn brauchen. Offen: welche Skripte es tatsächlich gibt.

**Gelernt:**
- Der Skill verlangt Dateibeispiele. Ohne Lesen bleibt jede Aussage Vermutung. Die wichtigste Erkenntnis ist deshalb die Pfadfrage, weil sie in dieser Sitzung zu einem echten Fehler geführt hat.
- Vereinheitlichen lohnt erst ab mehreren gleichartigen Stellen. Ein Helfer für ein einziges Skript ist Mehraufwand.

**Grenzen:**
- Keine Skripte gelesen, keine Muster gezählt.
- Die Empfehlung beruht auf Erinnerung an die Arbeitsschritte, nicht auf dem Bestand.
- Der Skill ist für Anwendungscode mit Frameworks gebaut (Komponenten, Hooks, Zustandsverwaltung). Für Skripte im Vault ist nur der Teil über Namen und Fehlerbehandlung anwendbar.
