# Autonome Zweiwochen-Optimierung Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Zwei getrennte LLM-Arbeitswege untersuchen alle registrierten Handelsspuren, entwickeln belegte Verbesserungen in isolierten Worktrees und übernehmen bestandene Kandidaten nur in den Papier-Dauerlauf.

**Architecture:** Eine gemeinsame Beleg-/Gate-Schicht dient zwei klar getrennten Läufen: Strategieoptimierung und technische Verbesserung. Kandidaten laufen in einem isolierten Papier-Worktree mit eigenen Zustands-/Journalpfaden. Ein bestandener Kandidat wird in die dedizierte Papier-Laufwurzel übernommen; Live-Code/Wachen und bestehende Echtgeld-Risikogrenzen bleiben unangetastet.

**Tech Stack:** Python 3.13, Git Worktrees, vorhandene Handels-/Backtestmodule, Codex-Heartbeat-Automation im aktuellen Thread.

**Spec:** `Agenten/Handel/docs/superpowers/specs/2026-10-25-handelsuebersicht-autonome-optimierung-design.md`

## Global Constraints

- Kein LLM- oder Routinenlauf löst Orders, Guthabenbewegungen oder Live-Freigaben aus.
- Experimente schreiben ausschließlich in einen eigenen Branch/Worktree und getrennte Papierzustände/Journale.
- Strategieoptimierer und technischer Verbesserer liefern getrennte Hypothesen, Änderungen und Berichte.
- Nettoergebnis enthält Gebühren, Funding und belegbare Ausführungskosten; ungepaarte oder nicht verifizierte Zeilen sind kein Profitbeleg.
- Ohne Mindestdaten, Reproduzierbarkeit, Out-of-Sample-/Holdout-Bestand und eingehaltenen Drawdown-Deckel erfolgt keine Promotion.
- Kein Kandidat wird in den gemeinsam genutzten Live-fähigen Arbeitsbaum gemergt.
- Abhängigkeiten dürfen nur in einer lokalen Worktree-Umgebung gepinnt werden; keine globalen Software-/Host-Konfigurationsänderungen.
- Jeder Zweiwochen-Lauf liefert einen Bericht hier im Codex-Thread und als lokale Markdown-Datei.

## Review Focus

- Unvollständige/ungepaarte Journale: Kandidat wird `nicht_auswertbar`, nicht Null-P&L (Test in Task 1).
- Fehlende Gebühr/Funding/Slippage: Gate blockiert automatische Promotion (Test in Task 1).
- Zeitreihen-Leakage und überlappende Train-/Holdout-Fenster: Kandidat scheitert (Test in Task 2).
- Worktree-Erstellung oder Branch-Anlage schlägt fehl: keine Arbeit im Hauptbaum (Test in Task 3).
- Papierlauf kann eigene Zustände/Journale nicht nachweisen oder Live-Modus nicht ausschließen: Promotion bleibt gesperrt (Test in Task 3).

---

### Task 1: Gemeinsames Ergebnisformat und Promotion-Gates

**Files:**
- Create: `Agenten/Handel/optimierung/__init__.py`
- Create: `Agenten/Handel/optimierung/ergebnis.py`
- Create: `Agenten/Handel/optimierung/gates.py`
- Create: `Agenten/Handel/tests/test_optimierung_gates.py`

**Interfaces:**
- Produces: `Kandidat`, `Messfenster`, `GateErgebnis` als unveränderliche Datenmodelle.
- Produces: `bewerte_kandidat(kandidat: Kandidat, basis: Kandidat, regeln: Mapping[str, object]) -> GateErgebnis` mit maschinenlesbaren Einzelgründen und `promotion_erlaubt: bool`.

- [ ] **Step 1: Tests schreiben** für Mindestanzahl abgeschlossener Papier-Runden, OOS/holdout, Gebühren/Funding, fehlende Daten, Drawdown-Deckel, stabile Verbesserung gegenüber Basis und Gleichstand.
- [ ] **Step 2: Gate-Tests ausführen**; alle Grenzfälle müssen zuerst scheitern.
- [ ] **Step 3: Ergebnis- und Gate-Modelle implementieren**; Mindestwerte je Strategie aus bestehenden Hausregeln ableiten und vor der ersten Promotion versioniert dokumentieren.
- [ ] **Step 4: Gate-Tests ausführen**; kein unbekannter/fehlender Messwert kann als bestanden durchgehen.
- [ ] **Step 5: Commit** `feat: add fail-closed paper promotion gates`.

### Task 2: Getrennte Optimierer- und Verbesserer-Läufe

**Files:**
- Create: `Agenten/Handel/optimierung/strategie.py`
- Create: `Agenten/Handel/optimierung/verbesserung.py`
- Create: `Agenten/Handel/optimierung/zyklus.py`
- Create: `Agenten/Handel/tests/test_optimierung_zyklus.py`
- Reference: `auswertung_alle.py`, `backtest_urteile.py`, `freqtrade/walkforward.py`, `verbesserer/lauf.py`, `dauerlauf.py`

**Interfaces:**
- Consumes: `Kandidat` und `GateErgebnis` aus Task 1.
- Produces: `finde_strategiekandidaten(spuren: Sequence[str], *, datenstand: datetime) -> list[Kandidat]`.
- Produces: `finde_technische_verbesserungen(spuren: Sequence[str], *, datenstand: datetime) -> list[Kandidat]`.
- Produces: `ZyklusBericht` mit Spurzuständen, Kandidaten, Blockaden und Revisionen.
- Produces: `fuehre_zyklus_aus(repo: Path, *, datenstand: datetime) -> ZyklusBericht`; jede Spur erhält `geprüft`, `datenarm`, `nicht_auswertbar` oder `Kandidat`.

**Task-2-Abnahmepräzisierung (25.10.2026):** Die bestehenden Auswerter sind
keine pauschal sicheren Kandidatenadapter. Discovery darf lesend Inventar und
konkrete Adapterlücken melden; fehlende Paarung, Gebühren/Funding/Slippage,
zeitliche Trennung oder Reproduzierbarkeit bleibt `nicht_auswertbar` bzw.
`datenarm`. Aus Discovery allein entsteht kein `Kandidat`. Task 2 ist erst
vollständig, wenn die für eine Spur ausdrücklich unterstützten read-only
Adapter geschlossene gepaarte Runden, Kostenfelder und Revision reproduzierbar
belegen. Nicht unterstützte Spuren bleiben sichtbar mit konkretem Grund; ihre
Adapterarbeit ist ein offener Folgeschritt und kein Erfolg.

- [ ] **Step 1: Tests schreiben** für getrennte Befundlisten, Rotation über Spuren ohne ausreichende Daten, Priorisierung riskanter Datenqualitätsfehler, Kostenberechnung und Reproduzierbarkeit.
- [ ] **Step 2: Tests ausführen**; Strategy- und Engineering-Befunde dürfen sich nicht vermischen.
- [ ] **Step 3: Discovery implementieren**; alle Register-Spuren read-only erfassen und bei fehlender Belegstrecke mit konkretem Grund zurückstellen. Discovery allein erzeugt keine Kandidaten.
- [ ] **Step 4: Adapter-Folgeschritt (Task 2B)**; pro freigegebener Spur einen read-only Auswerteradapter anbinden. Vorher Kostenfelder, Paarung, geschlossene Runden, Zeitraum/OOS und Reproduzierbarkeit belegen; technische Änderungen benötigen reproduzierbare Vorher-Nachher-Prüfung.
- [ ] **Step 5: Tests ausführen**; alle Registry-Spuren sind sichtbar geprüft oder begründet zurückgestellt; Adaptertests decken getrennte Befundlisten, Datenrotation/-priorität, Kostenberechnung und Reproduzierbarkeit ab.
- [ ] **Step 6: Commit** `feat: separate strategy and engineering review lanes`.

#### Task 2B: Validierte Spuradapter und Messungen (offen)

**Voraussetzung:** Task 2 Discovery bleibt fail-closed. Vor der Implementierung
Inventar der jeweiligen Journalformate und deren bestehender Paarungs- und
Kostenlogik lesen. Keine Handels-, Backtest-, Walk-Forward- oder Routine-Runner
im gemeinsam genutzten Checkout aufrufen; Messläufe gehören später in den
isolierten Experiment-Worktree aus Task 3.

**Abnahmekriterien:**

- Jede unterstützte Spur mappt aus einem read-only Ergebnis echte geschlossene,
  eindeutig gepaarte Runden und datierte, disjunkte Train/OOS/Holdout-Fenster.
- Gebühren, Funding und Slippage sind je Fenster explizit vollständig oder der
  Befund bleibt `nicht_auswertbar`; fehlende Werte sind nie Null.
- Revision, Datenstand und Eingabefingerabdruck machen dieselbe Auswertung
  reproduzierbar. Tests belegen Kostenrechnung, Zeittrennung und Reproduzierbarkeit.
- Nicht unterstützte Spuren bleiben einzeln mit Dateipfad und konkretem
  Adapter-/Datenmangel sichtbar. Sie zählen weder als geprüft erfolgreich noch
  als Kandidat.
- Technische Verbesserungen benötigen eine konkrete Hypothese und gemessenen
  Vorher-Nachher-Effekt; reine Syntax-/Dateiprüfung genügt nicht.

### Task 3: Isolierte Experimente und Papierpromotion

**Files:**
- Create: `Agenten/Handel/optimierung/worktree.py`
- Create: `Agenten/Handel/optimierung/papierlauf.py`
- Create: `Agenten/Handel/tests/test_optimierung_worktree.py`
- Create: `Agenten/Handel/tests/test_optimierung_papierlauf.py`

**Interfaces:**
- Produces: `lege_experiment_an(repo: Path, *, kennung: str, basis: str) -> Experiment` mit eigenem Pfad und Branch.
- Produces: `pruefe_papierisolation(experiment: Experiment) -> GateErgebnis`; erwartet eigene Zustands-/Journalpfade und nachweislich keinen Live-Modus.
- Produces: `registriere_papier_kandidat(experiment: Experiment, *, gate: GateErgebnis, ziel: Path) -> RegistrierungsBericht`; legt nach bestandenem Gate nur einen Kandidatenbeleg ab und meldet immer `aktiviert=False`.

**Aktivierung ist in Task 3 ausdrücklich nicht abgeschlossen.** Der bisherige
Belegschreiber schaltet keine Revision im Papierlauf um; eine `registriert`
Rückgabe darf nicht als Promotion oder Paper-Readiness gemeldet werden. Bis ein
separater, getesteter Papierlauf-Consumer die Auswahl tatsächlich übernimmt,
bleibt jede Aktivierung gesperrt.

- [ ] **Step 1: Tests schreiben** für Branch-/Worktree-Fehler, gleiche Schreibpfade, vorhandene Fremdänderungen, ungeprüften Modus, Gate-Nein, Ablehnungsvermerk ohne Aktivierung und idempotente Kandidatenregistrierung.
- [ ] **Step 2: Tests ausführen**; bei jedem Fehler bleibt der Hauptbaum unverändert.
- [ ] **Step 3: Experimentanlage und Kandidatenregistrierung implementieren**; keine bestehende Papierausführung einbinden, solange deren Consumer und Isolation nicht geprüft sind. Aktivierung bleibt Task 3B.
- [ ] **Step 4: isolierten Pilotlauf mit einer Spur** ausführen; bleibt offen, bis der eigenständige Aktivierungs-Consumer und dessen Isolation geprüft sind. Dieser Task startet oder verändert keinen Papierprozess.
- [ ] **Step 5: relevante Handelstest-Suite ausführen**; Paper-Readiness wird mit Task 3 nicht belegt und bleibt bis zur Abnahme von Task 3B offen.
- [ ] **Step 6: Commit** `feat: isolate paper experiments and register candidates`.

#### Task 3B: Papierlauf-Aktivierung (offen)

Eine spätere Umsetzung muss nachweisbar die registrierte Revision im dedizierten
Papierlauf laden, dabei Codewurzel, Zustand, Journal und Prozessidentität
getrennt halten und eine idempotente Rückkehr zur vorherigen Revision
ermöglichen. Sie darf keine Orders auslösen und keinen Live-/gemeinsam genutzten
Prozess verändern. Bis diese Vertrags- und Integrationstests bestehen, gilt
Task 3 nur als Experimentanlage und Kandidatenregistrierung; Promotion ist
nicht verfügbar.

### Task 4: Zweiwochenlauf und Berichte

**Files:**
- Create: Codex-Heartbeat-Automation im aktuellen Thread (einzige periodische Optimierungsautomation).
- Create: `Werkstatt/Protokolle/Handel/optimierung/` als Ziel der lokalen Markdown-Berichte.
- Modify only if needed: vorhandener Wrapper `Agenten/Routinen/optimierungen-finden.ps1`; die operative Integritätsprüfung bleibt getrennt.

**Interfaces:**
- Consumes: `fuehre_zyklus_aus()` und `GateErgebnis`.
- Produces: `bericht.md` je Lauf sowie kompakte Thread-Mitteilung mit geprüften Spuren, Blockaden, Commits, Promotionen und Kennzahlen.

- [ ] **Step 1: Berichtstests schreiben** für Erfolg, keine Kandidaten, Datenlücken, Toolfehler und Sicherheitsblockade.
- [ ] **Step 2: Berichtstests ausführen**; fehlgeschlagene Läufe erzeugen eine klare Meldung statt eines Erfolgsstatus.
- [ ] **Step 3: Berichtsschreiber implementieren**; Einheiten, Basisrevision, Kostenmodell, OOS-Fenster und Gründe dokumentieren.
- [ ] **Step 4: einmalige End-to-End-Paper-Probe ohne Live-Zugangsdaten** durchführen; keine echte Order und kein Schreiben in bestehende Journale.
- [ ] **Step 5: Codex-Heartbeat jeden zweiten Montag um 09:45 Europe/Berlin einrichten**; bestehende Windows-Routine „Optimierungen finden“ nicht duplizieren, Ergebnis nach jedem Durchlauf im Thread und lokal melden.
- [ ] **Step 6: Commit** `feat: schedule autonomous biweekly trading review`.

**Empfohlene Umsetzung:** subagent-driven, mit expliziter Dateibesitz-Zuordnung je Arbeitspaket und frischer Prüfung nach jedem Teil; Papierpromotion ist ein hochwirksamer Schritt und benötigt unabhängige Code-/Gate-Reviews, Live-Ausführung bleibt ausgeschlossen.
