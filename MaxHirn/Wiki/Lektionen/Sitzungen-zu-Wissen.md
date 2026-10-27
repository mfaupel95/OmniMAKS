---
id: 20261026-sitzungen-zu-wissen
title: 'Sitzungen als Quelle fuer gemeinsames Wissen'
tags: [betrieb, ki-agenten]
created: 2026-10-26
updated: 2026-10-26
related: ['[[Memory-Verluste]]', '[[Wissen/Sitzungen-und-Worktrees-2026-10-23]]']
summary: 'Wie dauerhafte Erkenntnisse aus Codex-, Claude- und Hermes-Sitzungen sicher und mit ehrlicher Abdeckung ins gemeinsame Wissen gelangen.'
---

# Sitzungen als Quelle fuer gemeinsames Wissen

## Regel

Sitzungstranskripte sind **Belegquellen, kein Gedaechtnis**. Vor jeder Konsolidierung zuerst vorhandene Notizen und Skills abgleichen. Nur dauerhaft gueltige, gegen heutige Dateien oder Laufzeit belegte Erkenntnisse uebernehmen; Fork-Duplikate, eingespielte Kontextbloecke, Werkzeugausgaben und Einzelfall-Protokolle herausfiltern. Ausgaben koennen Zugangsdaten enthalten: keine Rohtranskripte oder unbereinigten Auszuege in Wiki, Wissen oder Git schreiben.

## Quellen und Abdeckung

Die bekannten lokalen Quellen sind:

- Codex: `~/.codex/sessions/` und `~/.codex/archived_sessions/`.
- Claude Code: `~/.claude/projects/`.
- Hermes: `Agenten/Hermes/state.db`.

Der Ordner `Agenten/Hermes/sessions/` enthaelt `request_dump_*.json`-Aufzeichnungen von API-Anfragen; er ist kein vollstaendiges Gespraechsarchiv. Die Rueckschau-Auswertung verarbeitet Claude-JSONL und Hermes-SQLite, aber keine Codex-Rollouts. Codex muss daher separat strukturiert geparst werden. Eine Liste bekannter Speicherorte ist keine PC-weite Vollstaendigkeit.

Bei Hermes muss der SQLite-Lesezugriff den aktiven WAL-Stand einschliessen. `immutable=1` ueberspringt WAL-Aenderungen und kann juengste Nachrichten auslassen. `state.db` selbst nicht fuer eine Rueckschau veraendern.

## Auswertung und Ablage

- Haeufigkeiten nach unterschiedlichen Sitzungen und Tagen betrachten, nicht nur nach Nachrichten oder Befehlen. Forks koennen dieselbe Vorgeschichte mehrfach enthalten.
- Kategorien aus der bestehenden Arbeitsweise gegenpruefen, bevor neue Regeln entstehen. Am 26.10.2026 passten die haeufigen Muster (Zeitlimits, fehlende Dateien, Zeilenenden, Tests, Interpreter, paralleles Git und Zugangsdaten) bereits zu den globalen Arbeitsregeln; die Zaehler allein begruenden keine zweite Kopie.
- Max' bestaetigte Fakten und Projektzustaende gehoeren nach `Wissen/`; agentenuebergreifende Lehren nach `Wiki/`; wiederholbare Verfahren in einen Skill, der auf die Wiki-Lehre verweist.
- Jeder Befund braucht Quelle, Datum und eine heutige Gegenpruefung. Den Abdeckungsrand benennen; aus bekannten lokalen Quellen nicht „alle Sitzungen des PCs“ ableiten.

## Bekannte Werkzeuggrenze

Am 26.10.2026 brach `sitzungen_auswerten.py --umwege` beim Zusammenfuehren mit Hermes `state.db` mit `AttributeError: 'int' object has no attribute 'items'` ab. Die normale Zusammenfassung lief. Den kombinierten Umweg-Bericht erst wieder als verfuegbar melden, wenn dieser Fehler behoben und verifiziert ist.
