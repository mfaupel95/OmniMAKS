# Handelsinventar und Handelszentrale Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Die vorhandene Handelszentrale wird zur aktuellen, rein lesenden Übersicht über Downloads, bearbeitete Projekt-/Worktree-Arbeit und den Betrieb aller Handelsagenten.

**Architecture:** Neue Inventar- und Quellenmodule liefern ein normalisiertes, belegtes Statusmodell. Die bestehende Tk-Handelszentrale erhält einen Inventar-Reiter und bleibt reine Leseoberfläche; unbekannte Betriebsarten bleiben sichtbar unbekannt.

**Tech Stack:** Python 3.13, Standardbibliothek, Tkinter, vorhandene Windows-/Docker-/Git-Schnittstellen.

**Spec:** `Agenten/Handel/docs/superpowers/specs/2026-10-25-handelsuebersicht-autonome-optimierung-design.md`

## Global Constraints

- Keine Schreibzugriffe auf Handelsjournale, Zustände, Wachen, Downloads oder fremde Arbeitsbäume.
- Keine Inhalte aus Zugangs- oder Geheimnisdateien lesen; für Download-/Projektinventar nur Pfad und Dateimetadaten verwenden.
- `registriert`, `startbar`, `geplant`, `läuft`, `deaktiviert` und `unbekannt` sind getrennte Zustände.
- Ein unbekannter Freqtrade-Modus gilt nicht als Papiermodus.
- Keine Zugangsdaten, Prozessargumente oder Secrets in Ausgabe oder Report schreiben.
- Vorhandene Handelszentrale und ihre Lesegrenze erhalten.

## Review Focus

- Fehlender Downloads-Ordner: Inventar liefert einen klaren Quellenfehler statt leerem Erfolg (Test in Task 1).
- Lesefehler/Unicode in Dateinamen: einzelne Einträge dürfen den Scan nicht abbrechen (Test in Task 1).
- Dirty Git-Worktree: Pfadstatus wird nur als Metadatum abgebildet, Inhalte werden nicht gelesen (Test in Task 1).
- Docker-/Task-Snapshot unvollständig: Status wird `unbekannt`, nie `Papier` oder `bereit` (Test in Task 2).
- UI kann nicht auf Laufzeitquelle zugreifen: Fehler bleibt sichtbar und es gibt keinen Schreib-Fallback (Test in Task 3).

---

### Task 1: Reines Inventarmodell und Projektquellen

**Files:**
- Create: `Agenten/Handel/inventar.py`
- Create: `Agenten/Handel/tests/test_inventar.py`

**Interfaces:**
- Produces: `InventarEintrag(typ, name, pfad, projekt, status, modus, aktualisiert, quelle, hinweise)` als unveränderliches Datenmodell.
- Produces: `sammle_downloads(wurzel: Path) -> list[InventarEintrag]`, rekursiv über Dateien/Verzeichnisse, nur Metadaten.
- Produces: `finde_projektwurzeln(roots: Sequence[Path]) -> list[Path]`, entdeckt Git-Repositories an den operativen BrainFiles-Wurzeln und ergänzt registrierte externe Worktrees ohne Rekursion durch große Inhaltsbäume.
- Produces: `sammle_projektstatus(roots: Sequence[Path], *, seit: datetime) -> list[InventarEintrag]`, kombiniert aktuelle Git-Änderungen mit Datei-/Commit-Metadaten der letzten 90 Tage.
- Produces: `parse_git_worktrees(text: str) -> list[InventarEintrag]` und `parse_git_status(text: str, wurzel: Path) -> list[InventarEintrag]`; keine Dateiinhalte lesen.

- [ ] **Step 1: Tests schreiben** für leeren/nicht vorhandenen Downloads-Ordner, Umlaute, verschachtelte Einträge, Repositories in mehreren operativen Wurzeln, registrierte externe Worktrees, jüngste Commit-Pfade und dirty/untracked Pfade; sicherstellen, dass Eintragsinhalt nie geöffnet wird.
- [ ] **Step 2: Tests ausführen** mit dem Handel-Interpreter; erwartete Fehlschläge müssen die fehlende Implementierung bezeichnen.
- [ ] **Step 3: `inventar.py` implementieren** mit `pathlib`, `subprocess` nur für `git worktree list`/`git status --porcelain -z` sowie `git log --since=90.days --name-only`; Inhalte nicht lesen. Fehler je Quelle als Hinweis im Ergebnis erfassen.
- [ ] **Step 4: Tests ausführen**; alle Metadatenfälle bestehen, kein Quellinhalt wurde gelesen.
- [ ] **Step 5: Commit** `feat: add read-only project inventory`.

### Task 2: Betriebssnapshot für Spuren, Bots und Routinen

**Files:**
- Create: `Agenten/Handel/inventar_quellen.py`
- Create: `Agenten/Handel/tests/test_inventar_quellen.py`
- Reference: `Agenten/Handel/dauerlauf.py`, `Agenten/Handel/freqtrade/bots.json`, bestehende `freqtrade_bridge.py`

**Interfaces:**
- Consumes: `InventarEintrag` aus Task 1.
- Produces: `lade_betrieb(repo: Path, *, docker_snapshot: str, task_snapshot: str, prozess_snapshot: str) -> list[InventarEintrag]`.
- Produces: `freqtrade_modus(bot: Mapping[str, object], effektive_config: Mapping[str, object] | None) -> str`; Rückgabe nur `Papier`, `Live` oder `Unbekannt`.

- [ ] **Step 1: Tests schreiben** für exakt 47 registrierte Spur-Schlüssel (Zahl aus Datenquelle lesen, nicht fest codieren), gestartete/fehlende Container, drei explizite Papier-Overlays, fehlende effektive Konfiguration, deaktivierte Verbesserer-Aufgaben und leere Prozess-Snapshots.
- [ ] **Step 2: Tests ausführen**; unbestätigte Modi müssen `Unbekannt` liefern.
- [ ] **Step 3: `inventar_quellen.py` implementieren**; Docker- und Aufgabenlisten nur mit Name/Zustand/Startzeit parsen. Effektiven Freqtrade-Modus aus vorhandener abgesicherter Schnittstelle nur als Bool/Status abfragen, niemals Schlüssel oder vollständige Config ausgeben.
- [ ] **Step 4: Tests ausführen**; unbekannte Datenquellen bleiben als Warnung sichtbar.
- [ ] **Step 5: Commit** `feat: add trading runtime inventory`.

### Task 3: Inventar-Reiter in die Handelszentrale integrieren

**Files:**
- Modify: `Agenten/Handel/handelszentrale.py`
- Create: `Agenten/Handel/tests/test_handelszentrale_inventar.py`
- Reference: `Agenten/Handel/tests/test_handelszentrale_rein_lesend.py`, `test_handelszentrale_struktur.py`

**Interfaces:**
- Consumes: `sammle_downloads()` und `lade_betrieb()`.
- Produces: neuer Reiter `Inventar` mit Tabellen für Downloads/Projekte und Runtime-Status; jede Zeile enthält Quelle, Zeitstempel und Warnung.

- [ ] **Step 1: Tests schreiben** für dynamische Spurenzahl, Link-/Pfadanzeige, unbekannten Modus, Aktualisierungszeit und lesenden Betrieb.
- [ ] **Step 2: gezielte Handelszentrale-Tests ausführen** und sicherstellen, dass neue Prüfungen zunächst scheitern.
- [ ] **Step 3: Reiter ergänzen**; vorhandene Spuren-, Freqtrade- und OmniTrade-Ansichten unverändert lassen, Netzwerk-/Docker-Abfrage im UI-Hintergrund halten.
- [ ] **Step 4: relevante Handelstest-Suite ausführen**; alle UI- und Read-only-Tests bestehen.
- [ ] **Step 5: Commit** `feat: show unified trading inventory`.

**Ausführungsbefehl für Handelstests:** `../../../BrainFiles/Agenten/Handel/.venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py"` aus dem Worktree-Ordner `Agenten/Handel`.
