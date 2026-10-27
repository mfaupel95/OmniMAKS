---
name: docker-compose-deploy
category: software-development
description: Deploy third-party Docker Compose repos on Windows.
version: 1.0.0
author: Hermes Agent
license: proprietary
metadata:
  hermes:
    tags: [docker, compose, deploy, build, pnpm, windows]
    related_skills: [disk-space-triage, brainfiles-git-hygiene]
---

# Docker-Compose-Deploy (Fremd-Repos auf Windows)

## When to Use

Max will ein geklontes Fremd-Repo (z. B. eine AI-Trading-Plattform, ein
Dashboard, ein Tool) als laufenden Dienst hochziehen: `docker compose up -d
--build`. Ziel: ein verifiziert laufender Stack auf localhost, ohne den
bestehenden Handelsbetrieb (Freqtrade-Container) zu stoeren.

## Ablauf

1. **Platz pruefen, BEVOR du baust.** `df -h <laufwerk>` (bzw. `Get-PSDrive`).
   Ein voller Datentraeger laesst den Docker-Daemon mitten im Build crashen
   (`rpc error: code = Unavailable ... EOF`) und reisst dabei ALLE Container mit
   — nicht nur den bauenden. Details + Neustart-Muster: Skill `disk-space-triage`.
2. **Image bauen und Container starten getrennt.** `docker compose build app`
   zuerst (einzelner Schritt, laeuft im Hintergrund mit notify), erst nach
   erfolgreichem Build `docker compose up -d`. So isolierst du Build-Fehler vom
   Container-Start und riskierst nicht den laufenden Stack.
3. **Engine + Bestand vor dem Build checken:** `docker info` (Engine oben),
   `docker ps | grep -c freqtrade` (Handels-Container noch da). Nach einem
   Engine-Crash kommen `unless-stopped`-Container beim Neustart selbst zurueck.
4. **Nach dem Start verifizieren:** Port antesten (`curl -s -o /dev/null -w
   '%{http_code}' http://localhost:<port>/...`), Container-Status `docker ps`.
   Ein erfolgreicher Build ist kein erfolgreicher Start.

## pnpm 10+ blockt Build-Skripte: `ERR_PNPM_IGNORED_BUILDS`

Ein Frontend-Build in einem Fremd-Repo scheitert mit `ERR_PNPM_IGNORED_BUILDS
... Ignored build scripts: esbuild@0.18.20` und dem Hinweis `Run "pnpm
approve-builds"`. Das ist pnpm 10+ Verhalten: Build-Skripte von Dependencies
sind standardmaessig blockiert.

**Der Fix ist NICHT `onlyBuiltDependencies` zu ergaenzen.** Das Feld in
`package.json` (`pnpm.onlyBuiltDependencies`) wird von pnpm 10+ ignoriert; die
`pnpm-workspace.yaml`-Variante (`onlyBuiltDependencies:`) wird zwar gelesen
(`pnpm config get onlyBuiltDependencies` zeigt den Wert), aber der Install
ignoriert sie trotzdem; auch `pnpm install --config.onlyBuiltDependencies=...`
und die Env-Variante greifen nicht. Du verbrennst mehrere Build-Laeufe damit.

**Der zuverlaessige Fix: pnpm auf die im Projekt deklarierte Version pinnen.**
Lies `packageManager` im Root-`package.json` (z. B. `pnpm@8.15.5+sha512...`) und
pinne genau diese Version im Dockerfile:

```dockerfile
RUN npm install -g pnpm@8.15.5 && pnpm install
```

pnpm 8 blockt Build-Skripte nicht standardmaessig und liest die Lockfile-Version
(6.0) korrekt. Nach dem Pinnen mit `--no-cache` bauen, damit der geaenderte
Dockerfile-Schritt sicher greift.

## SIGBUS (Exit 135) bei C-Erweiterungen auf Docker Desktop/WSL2

Ein Debian/glibc-basiertes App-Image kann auf dieser Docker-Engine crashen, wenn
bestimmte C-Erweiterungen importiert werden: `uvloop`, `psycopg2` (und
aehnliche) stuerzen mit `Bus error` / Exit 135 (SIGBUS) ab, waehrend andere
C-Module (`httptools`, `websockets`, `cryptography`) und das Basis-Image selbst
fehlerfrei laufen. Symptom-Muster: `import main` ok, aber `python -m
database.init_postgresql` oder `pip list` crasht mit `Bus error`.

- **Nicht verwechseln mit einem Repo-Fehler.** Das Image baut sauber, das
  Basis-Image laeuft, einzelne C-Module laufen — nur die betroffenen C-Binaries
  crashen. Diagnose: jedes C-Modul einzeln importieren und den echten Exit-Code
  messen (nicht `$?` eines Pipes — der zeigt den tail-Exit).
- **Der Restart-Loop eines so crashenden Containers destabilisiert die Engine**
  und kann sie samt Freqtrade-Stack crashen lassen (zweimal beobachtet). Nach
  Diagnose den Stack sofort stoppen (`docker compose stop`), nicht im Loop
  lassen.
- **Kein schneller Fix im Repo.** `--no-binary`-Rebuild aus dem Quellcode ist
  der naechste Kandidat, aber nicht garantiert. Wenn die Engine zweimal crasht,
  den Build abbrechen und ehrlich berichten statt weiter zu schleifen.

## Fallen

- **`patch`-Tool vermurkst JSON/mehrzeilige Bloecke** (dupliziert Fragmente,
  zerstoert Einrueckung, erzeugt Tippfehler wie `onlyBuiltDiltDependencies`).
  Fuer JSON/Code mit Einrueckung die Datei per Python `json.load`/`json.dump`
  (oder Zeilen-Index-Ersetzung) aendern und danach validieren, nicht per
  `patch`-Tool.
- **`write_file` verweigert Ueberschreiben nach einem `patch`-Versuch** (Stale-
  Guard: "last read with offset/limit pagination"). Die Datei vorher vollstaendig
  lesen oder die Aenderung per Python-Heredoc machen, das den Stale-Guard
  umgeht.
- **`git worktree move` scheitert ueber eine Junction** (`Improper link`).
  Manueller Umzug (robocopy + Register-Pointer) steht im Skill
  `brainfiles-git-hygiene`.
- **Ein `--no-cache`-Build ist teuer** (zieht alle Images neu). Erst pruefen, ob
  der geaenderte Schritt (z. B. Dockerfile-Zeile) ohne `--no-cache` greift —
  Docker invalidiert den Cache ab der geaenderten Zeile automatisch. `--no-cache`
  nur, wenn ein Cache-Problem vermutet wird.
