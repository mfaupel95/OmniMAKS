---
id: 20261023-sitzungen-und-worktrees
title: 'Sessions und Worktrees - Bestand 23.10.2026'
tags: [betrieb, ki-agenten, system]
created: 2026-10-23
updated: 2026-10-26
related: ['20260830-ki-ablagen-benutzerordner', '20260830-hermes', '20261020-sitzungs-konsolidierung', '20260830-schutzregeln']
summary: 'Gezielte Bestandsaufnahme bekannter Session-Speicher, Codex-App-Threads und sichtbarer Worktrees mit offenem Abdeckungsrand und Prüfplänen.'
---

# Sessions und Worktrees - Bestand 23.10.2026

## Umfang und Grenzen

Erfasst wurden die bekannten lokalen Speicherorte für Codex, Claude Code und
Hermes sowie die Codex-App-Threadliste und die bekannten
`Werkstatt/Worktrees`. Das ist **keine vollständige Dateisuche über jedes
Laufwerk oder jedes installierte Programm**. Die Codex-App lieferte höchstens
50 Threads; mindestens 50 waren in der Antwort enthalten. Der Codex-Sitzungsindex
und die Hermes-/Claude-Ordner wurden read-only gezählt. Sessioninhalte wurden
nicht ausgewertet.

## Gemessener Bestand

| Quelle | Stand am 23.10.2026 | Befund |
|---|---:|---|
| Codex `~/.codex/sessions` | 387 Dateien, 87.738.092 Byte; jüngste Datei 04:20:47 | Lokale Codex-Sessionablage |
| Codex `~/.codex/session_index.jsonl` | 39 Zeilen | Indexeinträge; nicht als Zahl aller archivierten Threads interpretieren |
| Codex `~/.codex/archived_sessions` | 14 Dateien, 1.308.877 Byte | Separater Archivordner; jüngste Datei 28.08.2026 |
| Codex-App | 50 Threads geliefert, davon 2 mit Status `active` | Limit der App-Abfrage erreicht; dies ist kein Gesamtzähler |
| Claude Code `~/.claude/projects` | 47 direkte Unterordner, 1.612 Dateien, 1.105.930.105 Byte | Session-/Projektablage laut vorhandenem Pfadwissen |
| Hermes `Agenten/Hermes/sessions` | 83 direkte Einträge, 85 Dateien, 47.703.435 Byte | Jüngste Datei 04:21:22; direkter Unterordner `saved` ist vorhanden |
| Codex `~/.codex/worktrees` | nicht vorhanden | Kein Codex-eigener Worktree-Ordner an diesem bekannten Pfad |
| `Werkstatt/Worktrees` | 5 direkte Ordner | Namen: `Arbeitsbereich`, `KI WORKTREE`, `maks.sound`, `omnitrade-live-testnet-verify`, `PC` |

Die zwei in der App als aktiv angezeigten Threads waren `Sessions und Worktrees
erfassen` und `Set up PolyStrata` (Abruf am 23.10.2026). Die Threadliste ist
keine vollständige Sessionhistorie.

## Sichtbare Worktree-Befunde

- `omnitrade-live-testnet-verify` ist ein Git-Checkout unter `O:\Werkstatt\Worktrees`,
  Branch `mainnet-gate`, HEAD `8fd1f314fe8ab89620e972750f3f1fe5004028ae`.
- `KI WORKTREE` enthält einen `.git`-Verweis auf
  `C:/Users/faupe/Documents/GitHub/onchainos-skills/.git/worktrees/KI-WORKTREE`;
  Git meldet `fatal: not a git repository: (NULL)`. Ursache und Nutzungsstatus
  sind ungeklärt. Nicht löschen oder reparieren, bevor Repo-Pfad und Besitzer
  geprüft sind.
- `Arbeitsbereich`, `maks.sound` und `PC` sind im untersuchten Ordnerbestand
  keine normalen Git-Worktrees mit `.git`-Marker. Das sagt nichts darüber aus,
  ob sie andere Arbeitsdaten enthalten.
- Der aufrufende BrainFiles-Git-Root meldet nur sich selbst in
  `git worktree list`; das erfasst keine unabhängigen Repositories unter
  `Werkstatt` oder anderen Laufwerken.

## Vorschläge mit Prüfplan

### 1. Gesamtinventar der Codex-App vervollständigen

**Vorschlag:** App-Threads seitenweise bzw. über die native Codex-Datenbank
erfassen, damit das 50-Thread-Limit nicht als Vollständigkeit missverstanden
wird.

**Prüfplan:** (a) Quelle und Schema der nativen Threaddatenbank bestimmen,
read-only; (b) Zahl der eindeutigen Thread-IDs gegen `session_index.jsonl`
und die App-Liste abgleichen; (c) aktive Threads anhand des App-Status separat
bestätigen; (d) Differenzen samt Abrufzeit festhalten. Keine Sessioninhalte
kopieren, bis der Nutzer das ausdrücklich möchte.

### 2. PC-weite Worktree-Suche abschließen

**Vorschlag:** Git-Worktree-Metadaten über die übrigen lokalen Volumes und
bekannten Projektwurzeln ermitteln.

**Prüfplan:** (a) vorhandene Laufwerksbuchstaben und bekannte Repo-Wurzeln
listen; (b) ausschließlich `.git`-Dateien bzw. `git worktree list --porcelain`
für gefundene Repositories lesen; (c) dieselben Checkout-Pfade deduplizieren,
Junctions berücksichtigen und Existenz/Branch/HEAD erfassen; (d) keine
Ordnerinhalte rekursiv inventarisieren und keine Worktrees verändern.

### 3. Verwaisten Verweis `KI WORKTREE` klären

**Vorschlag:** Repo-Root `onchainos-skills` und Besitzer des Worktrees finden.

**Prüfplan:** (a) den eingetragenen Git-Common-Dir-Pfad mit `Test-Path`
prüfen; (b) nur falls vorhanden, `git worktree list --porcelain` im Repo
lesen; (c) Branch, HEAD und Änderungen erfassen; (d) bei fehlendem Repo den
Worktree-Eintrag unverändert lassen und den ursprünglichen Pfad aus
Git-Metadaten suchen; (e) erst nach eindeutiger Zuordnung einen separaten
Vorschlag zur Reparatur oder Bereinigung erstellen.

### 4. Session-Sicherungsstrategie verifizieren

**Vorschlag:** Prüfen, ob Codex-, Claude- und Hermes-Sessions absichtlich
außerhalb der regulären BrainFiles-Sicherung bleiben oder gesichert werden
sollen.

**Prüfplan:** (a) Sicherungsskript und Ausschlusslisten read-only prüfen;
(b) Zielmedien und verfügbare Kapazität feststellen; (c) einzelne
repräsentative Dateien per Hash gegen eine vorhandene Sicherung vergleichen;
(d) Ergebnis und Umfang vor jeder Änderung vorlegen. Keine Sessiondaten
verschieben oder kopieren, bevor Ziel und Datenschutzumfang geklärt sind.

## Wiederholbare Erhebung

Die Zahlen oben sind ein Snapshot, kein automatisch aktueller Zustand. Bei
einer Wiederholung dieselben Pfade messen, Zeitstempel und Bytezahlen sichern
und die App-Abfragegrenze separat notieren. Die alte Erhebung in
[[KI-Ablagen-im-Benutzerordner]] bleibt als historischer Stand vom 30.08.2026
erhalten.


## Nachmessung und Rueckschau 26.10.2026

Gezielte Nachmessung der bekannten lokalen Speicherorte am 26.10.2026, 00:46 Uhr MESZ. Dateizahlen sind Dateizahlen und keine Zahl eindeutiger Threads; Forks koennen Inhalte duplizieren.

| Quelle | Gemessener Stand | Einordnung |
|---|---:|---|
| Codex `~/.codex/sessions/` | 233 JSONL-Dateien; 551 Dateien gesamt, 311.627.117 Byte | Rollouts; gesondert vom Claude/Hermes-Rueckschau-Skript |
| Codex `~/.codex/archived_sessions/` | 18 Dateien, davon 3 JSONL; 1.820.113 Byte | lokaler Archivordner |
| Claude Code `~/.claude/projects/` | 974 JSONL-Dateien; 1.614 Dateien gesamt, 1.106.715.449 Byte | durch Rueckschau ausgewertet |
| Hermes `Agenten/Hermes/state.db` | 1.172 Sitzungen; 937.811.968 Byte | aktuelle SQLite-Hauptdatei; Read-only-Rueckschau mit WAL-Zugriff |
| Hermes `Agenten/Hermes/state.db-wal` | 6.241.832 Byte, zuletzt 00:30:48 | aktive Aenderungen neben der Hauptdatei; bei Vollstaendigkeitsaussagen mitlesen |
| Hermes `Agenten/Hermes/sessions/` | 85 JSON-Dateien; 48.038.642 Byte | Request-Dumps, kein vollstaendiges Gespraechsarchiv |

Die normale Rueckschau ueber Claude und Hermes lief. Der Zusatzmodus `--umwege` scheiterte beim Hermes-Zusammenfuehren mit `AttributeError: 'int' object has no attribute 'items'`; siehe [[Wiki/Lektionen/Sitzungen-zu-Wissen]]. Die haeufigen Fehlerklassen aus der Auswertung waren bereits in den globalen Arbeitsregeln abgedeckt. Die dauerhaft nuetzliche neue Lehre und Quellenabdeckung steht in [[Wiki/Lektionen/Sitzungen-zu-Wissen]].

Abdeckungsgrenze: bekannte lokale Ordner und die Hermes-Datenbank, keine Vollsuche aller Laufwerke, weiterer Agentenprofile, externer Sicherungen oder vollstaendigen Codex-App-Datenbank. Die Zahlen sind ein Snapshot und muessen vor einer spaeteren Bereinigung neu gemessen werden.


## Nachmessung 26.10.2026, 01:29 MESZ

### Codex, Claude und Hermes

Die Datenbanken wurden ausschliesslich lesend abgefragt; Sitzungsinhalte wurden nicht ausgelesen.

| Quelle | Stand | Abgrenzung |
|---|---:|---|
| Codex `~/.codex/session_index.jsonl` | 144 Zeilen, 18.584 Byte | CLI-Index, kein Gesamtzaehler aller App-Threads |
| Codex `~/.codex/sessions/` | 566 Dateien, 335.112.942 Byte; juengste 01:28:34 | lokale Sessiondateien |
| Codex `~/.codex/archived_sessions/` | 18 Dateien, 1.820.113 Byte | lokales Dateiarchiv; getrennt vom Archiv-Flag in der DB |
| Codex `state_5.sqlite`, Tabelle `threads` | 550 Datensaetze: 534 nicht archiviert, 16 archiviert | Statuszaehlung, keine Inhalte gelesen |
| Codex `thread_history_1.sqlite` | 69.237 Items, 4.221 Turns | Zeilen in der Projektion, keine eindeutigen Chats |
| Codex `codex-dev.db`, `local_thread_catalog` | 379 Eintraege: 373 lokal, 6 ChatGPT | separater lokaler Katalog |
| Codex-App-Abfrage | 59 Eintraege: 9 angeheftet und 50 weitere; 4 aktiv, 18 idle, 37 nicht geladen | Limit der App-Abfrage erreicht |
| Claude Code `~/.claude/projects/` | 47 direkte Ordner, 1.614 Dateien, 1.106.715.449 Byte | juengste Datei 24.10.2026 04:47:26 |
| Hermes `Agenten/Hermes/sessions/` | 85 Dateien, 48.048.698 Byte | juengste Datei 26.10.2026 01:18:24 |

In der App-Abfrage waren aktiv: `Fehlende Dateien lokal aufspueren`, `Linux-OS fuer BrainFiles planen`, `IT-AUFGABEN` und `dann mach das`. Die angezeigte Threadliste bleibt auf angeheftete Eintraege plus 50 weitere begrenzt; die native Datenbank enthaelt deutlich mehr Datensaetze, darunter auch Kind-/Agenten-Threads.

### Git-Worktrees

Die aktuelle `git worktree list` fuer BrainFiles (26.10.2026) meldete Hauptcheckout plus fuenf registrierte Checkouts:

| Pfad/Branch | Stand |
|---|---|
| Hauptcheckout `maks_master`, HEAD `db043516` | 51 geaenderte Pfade; nicht angefasst |
| `.worktree/handel-vergleich`, `codex/handelsspuren-vergleich` | sauber |
| `.worktrees/skillsbot-ack-fix`, `bots/skillsbot-ack-fix` | 3 geaenderte Pfade; nicht angefasst |
| `.worktrees/skillsbot-auto-dispatch`, `informatiker161/skillsbot-auto-dispatch` | sauber |
| `Documents/Handel-swap-schritt1`, `jev/swap-schritt1` | sauber, ein Commit voraus |
| `Documents/Handel-trading-hub-design`, `arbeit/trading-hub-design` | sauber |

Der fruehere `codex/repos-zentrale-deduplikation`-Worktree und sein lokaler Branch sind nicht mehr vorhanden; der damalige Commit `bd6a679a` ist Vorfahr des aktuellen Haupt-HEADs und damit integriert. Ein App-Artefakt verweist noch auf den alten Worktree-Pfad. Auch `Documents/Handel-swap-familie-a` fehlt inzwischen; der Pfad und lokale Branch-Ref sind nicht vorhanden und Git listet ihn nicht mehr.

Das separate Multi-Container-Repository fuehrt `Agenten/claude/multi-container-app` auf `main` sauber sowie `.worktrees/multi-container-app-production` sauber mit sieben Commits Vorsprung zu `origin/main`.

### Weitere Worktree-Metadaten unter O:

An 112 direkten Ordnern und Projektordnern eine Ebene unter `O:\Werkstatt` wurden 74 Git-Wurzeln gefunden; fuenf Repositories haben je einen verknuepften Worktree-Eintrag:

- `codex/mfaupel95-bookish-engine`, `deepseek-harness/mfaupel95-refactored-sniffle` und `one-skill-to-rule-them-all/mfaupel95-miniature-fishstick`: Zielpfade unter `BrainFiles/Werkstatt/Repos/copilot-worktrees` fehlen; auch die naheliegenden Pfade unter `O:\Werkstatt` fehlen.
- `jev-trader/jev-trader-hl-livetest`: Ziel vorhanden, detached HEAD `2ecb23c`; vier unversionierte Dateien, darunter `.env.live` und `.env.trocken`. Inhalte der `.env`-Dateien nicht gelesen.
- `omnitrade/omnitrade-pr`: Ziel vorhanden, Branch `hermes/okx-reconnect-20261021`, HEAD `f01c37f`; eine unversionierte Rust-Beispieldatei.
- `O:\Werkstatt\Worktrees\omnitrade-live-testnet-verify`: eigenstaendiger Checkout, Branch `mainnet-gate`, HEAD `8fd1f31`, sauber.
- `KI WORKTREE` zeigt auf das fehlende Repo `C:\Users\faupe\Documents\GitHub\onchainos-skills`; keine Reparatur vorgenommen.

`Arbeitsbereich`, `maks.sound` und `PC` unter `O:\Werkstatt\Worktrees` haben keinen `.git`-Marker. Unter BrainFiles sind `hausspur-schluss` (mit verbliebenem `Agenten`-Ordner, ohne `.git`) sowie die leeren Ordner `kraken-papier2` und `kraken-papierbuch` ebenfalls keine registrierten Worktrees. `.worktrees/.codex/environments` enthaelt nur `environment.toml`.

### Abdeckung

In `C:\Users\faupe\Documents` wurden die direkten Ordner und eine Ebene darunter geprueft: 137 Verzeichnisse, 5 Git-Wurzeln; nur BrainFiles hatte dort verknuepfte Worktree-Metadaten. Das verschachtelte Multi-Container-Repository wurde separat erkannt. Unter `O:\Werkstatt` wurden nur direkte Repo-Ordner und eine Ebene unter `Projekte` geprueft. Ein tiefer rekursiver Lauf dauerte laenger als 60 Sekunden und wurde abgebrochen. Damit bleibt dies eine gezielte Bestandsaufnahme der bekannten Arbeitswurzeln, keine vollstaendige Dateisuche ueber alle Laufwerke oder Backups.
