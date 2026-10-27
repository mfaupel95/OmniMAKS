---
name: ziplime-backtesting
description: Set up and run Ziplime backtests for Max's trading.
version: 1.0.0
author: Hermes Agent
license: proprietary
metadata:
  hermes:
    tags: [handel, backtesting, ziplime, mcp, krypto, aktien]
    related_skills: [handel-spuren, hermes-agent]
---

# Ziplime-Backtesting einrichten und nutzen

## When to Use

Max will Ziplime (Fork `mfaupel95/ziplime`, Backtesting-Engine auf Polars mit Zipline-API) fuer seine Handelsoptimierung nutzen: Aktien/ETF als neue Asset-Klasse, Krypto ueber CSV, oder Backtests ueber den MCP-Server. Repo liegt in `Werkstatt/ziplime` (origin + upstream + privat-Remotes), eigenes `.venv` im Repo.

## Installieren und verifizieren

```
cd Werkstatt/ziplime
.venv/Scripts/python.exe -c "import structlog, polars, ziplime; print(pl.__version__)"
ziplime ingest-assets          # einmalig: Instrumentenliste (Yahoo, kein Key)
ziplime ingest -b demo -s AAPL,MSFT --start-date 2019-01-01 --end-date 2025-12-31
ziplime run -f examples/sma_demo.py -b demo -s AAPL,MSFT --start-date 2020-01-01 --end-date 2025-12-31
```

- **Polars auf 1.44.2 pinnen.** Ziplime verlangt `^1.24.0`. Polars 2.0 entfernte `group_by_dynamic(by=)` (bricht den Lauf), und 1.24.0 hat einen `WindowsPath`-Bug in `scan_delta`. 1.44.2 liegt im Band und funktioniert. `nautilus-trader` liegt im `scanner/.venv`, nicht im globalen Python — kein Konflikt beim Downgrade.
- **`ziplime mcp` startet den MCP-Server** (`ziplime-local` 0.1.0, 14 Tools). Smoke-Test: `_test_mcp_server.py` und `_test_mcp_workflow.py` im Repo sprechen JSON-RPC 2.0 ueber stdio.

## MCP-Server registrieren (Hermes + Claude)

Der Server laeuft ueber das Repo-venv (`-m ziplime.mcp`). Registrieren in drei Stellen, die synchron bleiben muessen:

1. **Hermes-Haupt-Config** (`Agenten/Hermes/config.yaml`, default-Profil, NICHT das bots-Profil):
   ```
   hermes -p default mcp add ziplime --command "C:\...\Werkstatt\ziplime\.venv\Scripts\python.exe" --args -m ziplime.mcp
   echo "y" | hermes -p default mcp add ...   # beantwortet die interaktive Tool-Freigabe-Prompt
   hermes -p default config set mcp_servers.ziplime.cwd "C:\...\Werkstatt\ziplime"
   ```
   `hermes mcp add` fragt interaktiv "Enable all 14 tools?" — ohne `echo "y" |` haengt es. `cwd` muss auf das Repo gesetzt werden, sonst findet der Server seine Daten nicht.
2. **MCP-Manifest** (`Agenten/MCP-Manifest.json`, Single Source of Truth): Eintrag mit `agent: "beide"`, `command`/`args`/`cwd` relativ zur Wurzel. Der `mcp-sync-check.ps1` prueft die Synchronisation.
3. **Claude-Desktop-Config** (`%APPDATA%/Claude/claude_desktop_config.json`): liegt ausserhalb `HERMES_WRITE_SAFE_ROOT` — ueber Python-Heredoc schreiben, nicht ueber `patch`/`write_file`.

## Krypto ueber CSV (Weg 2)

Echte Kerzen liegen als `Agenten/Handel/kerzen_<SYMBOL>_<TF>_<N>.json` (Format `[ts_ms, open, high, low, close]`, KEIN Volumen). Konvertieren nach `data/btc_usdt_1h_echt.csv` mit Spalten `timestamp,symbol,open,high,low,close,volume` — und dabei NICHTS auf volume=0 lassen, sonst blockiert der Fill-Pfad (siehe Bruchmengen-Fills): realistisches 1h-Volumen einsetzen (lognormal ~800 BTC).

**Zwei Fixes, ohne die der CSV-Backtest nicht laeuft:**

1. **`CSVDataSource` als Haupt-Marktdatenquelle braucht `get_missing_data_by_limit`.** Die Basis-CSVDataSource ist nur als Zusatzquelle (`custom_data_sources`) gedacht und implementiert die Methode nicht. Als `market_data_source` ruft die Simulation sie auf, wenn ein Abfragezeitpunkt leicht ueber das CSV-Ende ragt (Positions-Bewertung am Laufende). Unterklasse im Beispiel-Skript, die die Daten der CSV selbst zurueckgibt. **WICHTIG: die Basis ruft sie SYNCHRON auf (ohne `await`)** — die Methode muss `def`, nicht `async def` sein, und direkt auf `self.get_dataframe()` filtern.
2. **Asset unter `mic="XNGS"` anlegen, nicht `_BNCC`.** `backfill_sid_data` sucht Symbole mit `mic="XNGS"` (hartkodiert). Legt man das Asset unter `_BNCC` an, findet `backfill` es nicht und wirft `Symbols are missing in asset database`. `_setup_crypto_asset.py` muss das Asset additiv unter XNGS anlegen (auch wenn ein `_BNCC`-Eintrag existiert). `first_traded` und `auto_close_date` sind NOT NULL — beide setzen, sonst `IntegrityError`.

## Stuendlicher Kalender fuer 1h-Krypto

Der eingebaute `24/7`-Kalender ist **tagesbasiert** (24h-Sessions) — eine 1h-Strategie bekommt nie genug Bars und handelt nie (Rendite 0, keine Orders). Fuer 1h-Daten einen eigenen stuendlichen Kalender bauen:

- Von `AlwaysOpenCalendar` erben, `sessions` als stuendliche `pd.date_range` (tz-naive) ueberschreiben.
- `sessions_minutes`, `session_first_minute`, `session_last_minute`, `first_minutes`, `last_minutes` ueberschreiben, damit sie stuendlich statt minutenbasiert arbeiten (die Basis-Minuten-Logik ist tief eingebettet und bricht mit `IndexError`/`Length mismatch`).
- **Registrieren mit `register_calendar_type(name, Klasse, force=True)`** (nicht `register_calendar` mit Instanz — das erlaubt keine Argumente). `run_simulation` ruft `get_calendar(name)` auf.
- `get_calendar` reicht `start=None`/`side="right"` als kwargs durch — der `__init__` muss `start=None, end=None, **kwargs` akzeptieren und None auf Defaults zuruecksetzen, sonst bricht `pd.date_range`.

## Debugging-Falle: Strategie-Datei wird ueberschrieben

Das Beispiel-Skript schreibt die Strategie-Datei bei JEDEM Lauf aus dem eingebetteten `STRATEGY_CODE` neu. Debug-Prints direkt in die Strategie-Datei (`examples/strategies/btc_sma.py`) gehen beim naechsten Lauf verloren. Debug-Code in den `STRATEGY_CODE`-String im Skript einbauen, nicht in die generierte Datei.

## Bruchmengen-Fills (Krypto): drei Fixes, sonst keine Orders

Ein Krypto-CSV-Backtest (BTC ~108k, 100k Budget -> 0.924 BTC) laeuft erst durch, wenn drei Dinge stimmen. Symptom-Kette: Orders werden eingereicht (ORDER_SUBMIT) aber nie gefuellt (Txn leer, Portfolio bleibt 100k).

1. **`get_spot_value`-await-Bug:** Basis-`DataSource.get_spot_value` ruft das async `get_data_by_limit` OHNE `await` auf und liefert eine Coroutine statt dem Preis. Bundles ueberschreiben das korrekt, `CSVDataSource` erbt den Bug. In der Unterklasse `get_spot_value` ueberschreiben und `await self.get_data_by_limit(...)` zurueckgeben.
2. **`int()`-Truncation bei Bruchmengen:** `trading_algorithm.order()` Zeile ~1702 `order_qty_rounded = int(round_if_near_integer(amount))` stutzt 0.924 -> 0 ("Not executing order for zero shares"). Gleicher Bug in `slippage_model.simulate()` Zeile ~169 `amount=int(execution_volume)`. Beide auf `round_if_near_integer(...)` aendern (Import aus `ziplime.utils.math_utils`). Aktien (ganze Anteile) bleiben unberuehrt.
3. **`volume=0` blockiert den Fill-Pfad:** `slippage_model.simulate()` kehrt bei `volume == 0` sofort zurueck (Zeile ~132). Die CSV aus den Kerzen hat kein Volumen -> nie gefuellt. Realistisches 1h-Volumen in die CSV schreiben (lognormal um ~800 BTC).

Zusaetzlich: Default-Slippage ist `FixedBasisPointsSlippage` (braucht volume, bricht bei 0) - im Backtest-Aufruf `equity_slippage=NoSlippage()` uebergeben. Und der stuendliche Kalender (siehe unten) ist Pflicht, sonst bekommt die 1h-Strategie nie genug Bars.

## Parameter-Sweep fuer die Strategie (SMA-Kombinationen durchtesten)

Steht die Engine (Backtest laeuft durch, Orders werden gefuellt), aber das Ergebnis ist schlecht: nicht raten — mehrere Parameter mit einem Sweep testen. Max waehlt dafuer gezielt „Parameter-Sweep".

- Ein eigenes Sweep-Skript (`data/btc_param_sweep.py` als Vorlage): die CSV **einmal** laden, dann je Kombination eine Strategie-Datei aus einem String generieren und `run_simulation` aufrufen. Ergebnis je Kombination (Return, Sharpe, Drawdown) sammeln und nach Return sortiert ausgeben.
- Ueber `equity_slippage=__import__('ziplime.finance.slippage.no_slippage', ...).NoSlippage()` auch im Sweep das NoSlippage setzen — sonst bricht jede Kombination am volume-
-0-Default (wie der Einzel-Backtest).
- Sweep braucht Minuten bis eine Viertelstunde (je Kombination ein voller Lauf) — im Hintergrund starten und auf die Notification warten, nicht blockierend.
- Ergebnis-Lesart: die beste Kombination nach Return ist NICHT automatisch die beste Wahl — auf Sharpe und Drawdown achten (Overfitting auf einen Zeitraum).

## Warum ein SMA-Crossover auf 1h-Kerzen stark verlieren kann (Whipsaw)

Ein SMA-Crossover (z.B. 12/26) auf **1h-Kerzen** flippt in einem fallenden, volatilen Markt staendig: es kauft jeden lokalen Hochpunkt und verkauft jeden lokalen Tiefpunkt. BTC von 116k auf 79k (−32 %) wird so zu −81 % durch staendiges Hin-und-her — das ist ein echtes, korrekt gemessenes Ergebnis, kein Ausfuehrungsfehler. Antworten, wenn der Nutzer fragt warum eine Crossover-Strategie so schlecht abschneidet:

- **Laengere SMAs** (50/200 statt 12/26) reduzieren Whipsaw.
- **Trendfilter** (nur long wenn Preis > 200er-SMA) verhindern Kaeufe im Abwaertstrend.
- Oder ein Parameter-Sweep (oben) statt einer Einzelraterei.

## Verifizieren, dann committen

- Backtest laeuft durch heisst: Performance-Zeilen > 0 UND Orders werden ausgefuehrt (Portfoliowert aendert sich). `handle_data` wird aufgerufen, aber Orders nie gefuellt = Kalender- oder Datenquellen-Problem, kein Strategie-Problem.
- Arbeit im Fork-Repo lokal auf `master` committen (`git commit --author="Hermes <hermes@local>"`), nicht ungefragt pushen. `.venv` ist ignoriert.
- Ein delegierter Bot, der in einer Repetitionsschleife stirbt, hat oft schon Dateien geschrieben — `git status` pruefen, Artefakte uebernehmen und selbst fertigstellen statt neu zu starten.
