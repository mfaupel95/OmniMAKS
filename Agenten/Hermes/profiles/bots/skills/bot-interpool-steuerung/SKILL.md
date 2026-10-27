---
name: bot-interpool-steuerung
category: autonomous-ai-agents
description: Use when routing repo-bot work. Verify every bot claim.
version: 1.1.0
author: Hermes Interpool
license: MIT
metadata:
  hermes:
    tags: [delegation, repo-bots, telegram, verification, worktree, git]
    related_skills: [brainfiles-git-hygiene, hermes-agent]
---

# Interpool-Bot-Steuerung

## When to Use

Use when a Telegram/group or repo request must be routed to a repo bot, or when
verifying a bot handoff. For a short local read-only lookup, inspect the source
directly instead of spawning a bot.

Ich bin die Interpool (Profil `bots`) auf Telegram. Ich leite Auftraege an die
Repo-Bots (Profile unter `Agenten/Hermes/profiles/<bot>/`, Startverzeichnis
`Werkstatt/<repo>`) weiter und fuehre sie NICHT selbst aus. Start:
`hermes -p <bot> chat -q "<auftrag>"` aus `Agenten/Hermes/profiles`.

- **Binär-Pfad:** `hermes` ist NICHT `./hermes` im Profil-Ordner — der Aufrufer
  liegt unter `Agenten/Hermes/hermes-agent/.hermes/bin/hermes` (bzw. `hermes`
  im PATH). Ein Start mit `./hermes` bricht mit "No such file or directory"
  (exit 127) ab. Immer den vollen Pfad oder `hermes` aus dem PATH verwenden.

## Profil und Laufzeit-Bot auseinanderhalten

- Vor dem Dispatch den exakten Namen gegen `profiles/<name>/config.yaml`
  pruefen. Fehlt das Profil, nicht sofort als Tippfehler oder fehlenden Bot
  behandeln: gezielt im zustaendigen Modul README, Einstiegsskript und
  Statuslog nach einem Dienst, Bridge- oder Alias-Bot suchen (z. B.
  `Agenten/Bus/skillsbot.py`). Profile (`hermes -p`) und dauerhaft laufende
  Bruecken sind unterschiedliche Dinge; vor „rausschmeissen" Eigentum,
  Nutzerpfad und laufenden Prozess pruefen.
- **Telegram-Transport ist keine Profilwahl.** Beim SkillsBot normalen Freitext
  in `Agenten/Bus/skillsbot.py` bis `frage()` verfolgen: dieser A2A-Aufruf geht
  an das Default-/Hauptprofil; `gateway.profile_routes` waehlt nur das Ziel
  eingehender Gateway-Telegram-Updates und routet diese A2A-Nachricht nicht um.
  Die Profilwahl erfolgt dort nur explizit (`/bot NAME Auftrag`, `/bot NAME`
  plus naechste Nachricht einmalig, `NAME: Auftrag` oder `@NAME Auftrag`) oder
  durch einen Dispatcher, der wirklich aufgerufen wird; `/bots` listet Profile.
  Soll freier SkillsBot-Text automatisch an Fachprofile gehen, muss der Pfad
  explizit zum `bots`-Dispatcher oder zu einer tatsaechlich ausgefuehrten Triage
  fuehren; der Config-Schluessel `triage_specifier` allein ist kein Router.
  Behalte Recherche → hoechstens ein Fachprofil seriell bei; kein Fan-out.
  Klaere bei Bridge-Umbauten vor der Code-Delegation den Kontextweg: `gateway.profile_routes`
  routet nur Gateway-Inbound; ein benannter A2A-served profile kann `contextId` erhalten,
  waehrend `hermes -p <profil> chat -q` eine neue CLI-Session startet, sofern deren
  `session_id` nicht pro Chat gespeichert und mit `--resume` fortgesetzt wird. Lade die
  Details aus `hermes-agent/references/telegram-topic-routing.md`. Wenn der A2A-Weg eine
  Konfigurationsaenderung oder einen Gateway-Neustart braucht, klaere die Freigabe vorab.
  Gib einem Codebot nicht gleichzeitig „Mehrturn-Kontext erhalten“ und „keine Config/
  Neustart“ ohne einen erlaubten Fallback; dieser Widerspruch kann in langen Abwaegungen
  enden, bevor Dateien geaendert werden.
- Ein kurzes SkillsBot-Log mit `status=ok` und 11 Ausgabezeichen belegt nur die
  sofortige A2A-Annahme `Angenommen.`, nicht die Erledigung. Wenn ein Transcript
  pro eingehender Freitextnachricht sowohl einen langen Arbeits-Ack als auch
  `Angenommen.` zeigt, trace beide Sendepfade (`sende()` in `bearbeite()` und
  den Rueckgabewert, den die Schleife erneut sendet): das sind zwei Acks fuer
  EINEN Auftrag, nicht zwei erfolgreiche Auftraege. `(leere Antwort)` oder ein
  A2A-Pausenbanner ist kein Abschlussbericht.
- Behandle `skillsbot.log` nicht als vollständigen Auftragsverlauf: `kommando`
  wird auf die ersten 40 Zeichen gekürzt, und der asynchrone A2A-Abschluss wird
  dort nicht protokolliert. Wenn der konkrete Auftrag oder das Ergebnis daraus
  nicht hervorgeht, rekonstruiere ihn aus dem ursprünglichen Telegram-/A2A-Verlauf
  oder frage Max; rate nicht und starte denselben Auftrag nicht doppelt.
- Vor einem Wiederholen auf die spaetere Ergebnisnachricht bzw. den A2A-Abschluss
  warten oder den Taskstatus in der autoritativen Quelle pruefen. Ein pausierter
  A2A-Thread oder eine leere Antwort bestaetigt die Erledigung nicht; nicht
  automatisch erneut senden, weil der erste Lauf teilweise gewirkt haben kann.
  Dem Nutzer klar melden, ob die Aufgabe nur angenommen, pausiert, leer
  abgeschlossen oder wirklich mit Ergebnis beendet wurde.
- Statuswerte trennen: `abgewiesen` ist meist eine Chat-Allowlist-Entscheidung,
  `bildfehler` betrifft den Medien-Eingang; beides beweist keinen A2A-Ausfall.
  Vor einer Codeaenderung den Zielchat gegen `chat_erlaubt()` und den A2A-Fehler
  nach dem Ack separat pruefen.
- Für automatische Handoffs aus Beobachtungen zuerst die reale Quelle und ihr
  dokumentiertes Format nachweisen; ein Planvorschlag ist keine vorhandene Datei.
  Fehlender Workspace bedeutet stoppen und den Pfad/Initialisierungsentscheid
  erfragen. Bei einem als read-only zugesagten Handoff eine per-Aufruf-Toolset-
  Schranke setzen und die effektiven Tools verifizieren; ein Prompt allein ist
  keine technische Sperre. Details/Toolset-Fallen stehen in
  `references/observations-routing.md`.

## Lektion: Immer als Hintergrundjob mit notify starten
- Repo-Bot-Kaltstart + Auftrag ueberschreitet hier regelmaessig das Foreground-
  Timeout (~7 min, terminal wird mit exit 0 timeout abgebrochen). Das Ergebnis
  geht dann verloren und der Bot-Daemon haengt weiter (nicht abgestuerzt).
- Start deshalb IMMER als: `terminal(background=true, notify=true,
  persist_on_release=true, command="cd profiles && env -u PYTHONHOME -u PYTHONPATH hermes -p <bot> chat -q ...")`.
  Ergebnis kommt als eigene Nachricht, sobald der Prozess endet. Persist on release,
  weil sonst ein vorzeitiges /new oder Timeout den laufenden Job killt.
- **`--background`/`--notify`/`--persist-on-release` sind TERMINAL-Tool-Flags, keine
  hermes-CLI-Flags.** Sie an `hermes -p <bot> chat -q ...` selbst zu haengen bricht
  mit `hermes: error: unrecognized arguments`. Die Flags gehoeren in den
  `terminal(background=..., notify=..., persist_on_release=...)`-Aufruf, der den
  hermes-Befehl als `command` traegt — nicht in die hermes-Kommandozeile.
- Nach Ende Exitcode und Ergebnis abwarten. Ist die Ausgabe abgeschnitten, den
  vorhandenen Prozess-Log mit `process_manage(action="log", session_id=...)`
  seitenweise holen — denselben Auftrag nicht neu starten; ein zweiter Prozess
  kann dieselben Dateien oder Ressourcen parallel bearbeiten.
- **Der `terminal(background=true, persist_on_release=true)`-Start kann STILL
  sterben — kein Prozess, keine Ergebnis-Datei, leeres Log.** Das passiert bei
  manchen Bots (Kaltstart + grosser Auftrag) reproduzierbar: der Background-bash
  laeuft kurz, hat aber keine Kinder mehr, und `process-results/<id>.json`
  existiert nie. Vor dem Urteil "laeuft" nach dem Start verifizieren, dass der
  Prozess wirklich lebt (`ps aux | grep <bot>` zeigt den hermes-Prozess) und
  eine Ergebnis-Datei entsteht; ist beides leer, ist der Start fehlgeschlagen,
  nicht "noch am Initialisieren". Robuster Fallback: `nohup <hermes> -p <bot>
  chat -q "..." > <scratch>/<bot>-<thema>.log 2>&1 &` als Background-Command
  starten und die Log-Datei pollen — die ueberlebt Session-Ende und ist
  seitenweise lesbar, statt auf ein verlorenes Notify zu warten.
- **Ein delegierter Bot, der fertig wird, muss MELDUNG bekommen — auf das
  Notify zu warten und die eigene Runde mit "ich melde mich, sobald er fertig
  ist" zu beenden, ist ein stiller Fehlschlag.** Das Abschluss-Notify kann
  verlorengehen oder in keine neue Runde muenden; dann bleibt die Meldung aus
  und Max muss selbst nachfragen ("warum muss ich immer nachfragen"). Der Bot
  committet sein Ergebnis selbst (Autor `Hermes`) — der Abschluss ist deshalb
  ohne Notify an drei Zeugen belegbar: `process_manage(action="list")` leer,
  der Zielbaum-`git log` zeigt den Committ, oder `profiles/<bot>/logs/agent.log`
  endstand. Bei der naechsten Gelegenheit (naechste Runde, erstes Signal,
  bevor ein weiterer Auftrag startet) aktiv `process_manage`/`git log` prüfen
  und den Stand an Max melden — nie passiv abwarten, wenn man eine Meldung
  zugesagt hat. Eine mehrteilige Antwort (zwei unabhaengige Arbeiten) erst
  zusammen abschliessen, wenn beide belegt sind.
- **Foreground-Timeout ist nicht der Tod des Ergebnisses.** Laueft der Start
  versehentlich im Foreground (`terminal(...)` ohne background) in den ~420 s-
  Timeout, HAENGT der Bot weiter und arbeitet den Auftrag zu Ende — nur die
  Rueckgabe ist verloren. Den Prozess per `tasklist | grep -i python` bzw.
  `Get-CimInstance Win32_Process` aufspueren (NICHT `ps` aus git-bash, siehe
  Abschnitt Prozessdiagnose), und
  waehrend er laeuft (oder nach seinem Ende) `profiles/<bot>/logs/agent.log`
  lesen: der Log listet jede Tool-Execution mit Dauer/Zeichen und schreibt am
  Turn-Ende `reason=...` (z. B. `max_iterations_reached(5/5)`). Daraus den
  Teilbefund und den Abbruchgrund ableiten, statt denselben Auftrag blind neu
  zu starten oder falsch als Fehlschlag zu melden.
- Fremdarbeit im gemeinsamen Repo-Baum nicht ueberschreiben oder mitcommitten:
  vor Weiterarbeit `git status` und Aenderungszeit pruefen, und nur den Bot
  starten, der den betreffenden Bereich verantwortet.
- Vor dem Start pruefen, ob noch ein Prozess vom abgelaufenen Lauf haengt —
  mit `powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match '<bot>' -and $_.CommandLine -match 'chat' } | Select-Object ProcessId,CreationDate"`,
  nicht mit `ps` (siehe Abschnitt Prozessdiagnose). Erst feststellen, ob er
  wirklich zum eigenen Auftrag gehoert; keinen fremden/aktiven Worker beenden
  und nie doppelt starten.
- Wenn Max „stop“ sagt, den aktuellen delegierten Auftrag sofort beenden.
  Nur eigene Prozesse beenden, deren Zugehörigkeit zu diesem Auftrag verifiziert
  ist; vorbestehende Dienste und fremde Worker nicht stoppen. Danach prüfen, ob
  der eigene Prozess beendet ist und ob Teiländerungen/Worktrees entstanden
  sind. Diese unberührt lassen, nicht fortsetzen oder erneut starten, bis Max
  es ausdrücklich verlangt.

## Bot-Wahl: ein Modell, das in Schleifen laeuft, ist ein Wechsel-Grund
- **Nous-Credits koennen mitten im Betrieb erschoepfen (HTTP 402 "Insufficient
  available credits") — dann faellt JEDE Bot-Delegation aus, weil alle Profile
  ueber provider nous laufen.** llamacpp ist nur Fallback, und die `:free`-
  Modelle (longcat) antworten dann auch nicht brauchbar (haengen ohne Antwort).
  Erkennbar am Bot-Lauf, der nach ~30 s mit 402 endet. Vor einer Delegation bei
  unklarer Lage einen Trivial-Prompt als Credit-Probe schicken (z. B. "Antworte
  nur mit BEREIT"); schlaegt der fehl, erst Credits aufladen oder den Teil ohne
  LLM (Prozess-Checks, Watcher, Commits) direkt selbst machen statt zu warten.
- **Ein UNFERTIGES Hermes-Update blockiert JEDE Bot-Delegation mit einem
  eigenen Haeng-Signatur — nicht als Bot-/Gateway-Problem weiterdelegieren.**
  Haengt der Trivial-Prompt (und jeder `hermes -p <bot> chat`) mit
  "source-update completion failed: pm: worker exited without a result — run
  `hermes update` to finish it" (exit 124), ist ein Update nicht sauber
  abgeschlossen (ein pm-Worker endete ohne Ergebnis) und die CLI blockiert bei
  jedem Start. Das ist Wartungs-Arbeit, kein Bot-Problem: die richtige Adresse
  ist `hermes-wartung` oder Max in einer interaktiven Shell. Einen weiteren
  `hermes update` NICHT ungefragt selbst laufen lassen — er kann das Gateway
  neu starten und die eigene Telegram-Verbindung kappen. Vorher pruefen, ob
  eine verwaiste `.hermes-update-in-progress`-Datei den Start blockiert
  (entfernen, wenn kein Update-Prozess laeuft und das Log "Update complete!"
  zeigt), und den Update-Zustand aus `logs/update.log` lesen.
- **"Gateway did not answer session.create" ist NICHT automatisch ein
  Gateway-Ausfall — es kann das `:free`-Modell EINES Profils sein, dessen
  Gratis-Fenster beendet ist (HTTP 404 "free period has ended").** Isolieren
  statt raten: einen Trivial-Prompt an ein bekannt-gutes Profil schicken
  (z. B. `jev-trader` auf deepseek). Antwortet das, ist das Gateway gesund und
  das fehlschlagende Profil hat das Modellproblem. Dann `model.default` in
  dessen `config.yaml` pruefen und auf `deepseek/deepseek-v4-flash-0731`
  umstellen (config committen, profiles/ gehoert dem bot-Bereich), danach den
  Auftrag neu starten. Ein `:free`-Modell mit beendetem Fenster antwortet
  nicht — es haengt, bis der Client mit session.create aufgibt.
- **Die Modell-Karte in diesem Skill kann vom IST der config.yaml abweichen —
  vor dem Delegieren `model.default` des Zielprofils lesen, nicht der Karte
  glauben.** Ein Profil, das laut Karte deepseek faehrt, kann in der config
  laengst auf longcat zurueckgefallen sein (parallele Sitzung, frueherer
  Umbau). Der Fehlschlag "session.create" mit einem `:free`-Modell ist genau
  das Symptom einer solchen Drift.
- **Das Subagent-Delegationsmodell lebt in der PROFIL-config, nicht nur in der
  zentralen `config.yaml` — und die Profil-config ist gegen `patch`
  geschuetzt.** `Agenten/Hermes/config.yaml` `delegation.model` zu aendern
  wirkt NICHT fuer Subagenten, wenn `profiles/bots/config.yaml` einen eigenen
  `delegation:`-Block hat (der ueberschreibt die zentrale). Und `patch`/
  `write_file` auf die Profil-config wird verweigert ("Agent cannot modify
  security-sensitive configuration"). Der funktionierende Weg ist
  `hermes config set delegation.model <modell>` (mit `HOME` gesetzt), das
  schreibt in die Profil-config; danach `hermes config get delegation.model`
  zuruecklesen. Vor einem Subagent-Fan-out das effektive Delegationsmodell
  pruefen — die laufenden Kinder zeigen es im `delegate_task`-Resultat
  (`Model: ...`), nicht der zentrale config-Wert.
- **Max' Vorgabe fuer Subagent-Arbeit im Handel-Baum: `openai/gpt-6-luna`
  (die "low"-Variante ohne `-pro`) ueber provider nous.** Das ist die
  OpenAI-Anbindung — die `openai/gpt-*-`Modelle laufen ueber den nous-Provider
  (inference-api.nousresearch.com), es gibt keinen separaten openai-Provider-
  Block. Vor einem Subagent-Fan-out fuer Handel-Optimierung
  `delegation.model` auf `openai/gpt-6-luna` setzen, wenn es nicht schon
  steht.
- Kollabiert ein delegierter Bot mit exit 1 / "Repetition Detected" (Modell-Loop),
  NICHT denselben Bot blind erneut starten — das Modell kollabiert wieder. Erst im
  Repo pruefen, was wirklich passiert ist (Commit da? Fenster offen? Position
  eingelegt?), dann den Auftrag an einen Bot mit stabilem Modell geben.
- Modell-Karte (gemessen): `recherche` = deepseek-v4-flash (stabil, auch fuer
  Handel-Baum-Analyse, cwd BrainFiles), aber LESEN-only; `jev-trader` = seit
  14.10.2026 auf deepseek-v4-flash fuer schreibende Handel-Codearbeit, seit
  23.10.2026 auf `deepseek/deepseek-v4-pro` eskaliert (der flash verbrauchte
  beim konzeptionell komplexen swap→Familie-A-Umbau das ganze Reasoning-Budget
  trotz Ein-Datei-Aufteilung); `markt-recherche`/`lotse` = longcat
  (kollabiert bei offenen Such-/Bau-Aufgaben in Wiederholungsschleifen). Fuer
  Analyse/Recherche im Handel-Baum `recherche` bevorzugen, nicht den longcat-Bot; fuer einen Bau/Commit einen deepseek-fahrenden schreibfaehigen Bot nehmen, und bei konzeptionell komplexem Umbau direkt `deepseek-v4-pro` statt flash. Die Karte ist ein Snapshot — vor dem Delegieren `model.default` des Zielprofils lesen (siehe Drift-Regel).
- **Iterationsbudget-Erschoepfung ist ein eigener Abbruchmodus, kein Kollaps.**
  Ein Bot kann mit exit 0 enden, aber "Iteration budget exhausted (5/5)"
  melden — er hat das Tool-Budget ausgeschoepft, bevor er fertig wurde, und
  liefert nur einen Teilbefund. Das ist kein Modell-Loop (nicht blind denselben
  Bot neu starten), sondern ein zu breiter Auftrag. Vor dem Neustart pruefen,
  was er schon geschafft hat (z. B. Journal-Analyse fertig, Parametersuche
  nicht), und den Rest als EINEN engen, single-focus Auftrag neu vergeben —
  nicht den ganzen mehrteiligen Auftrag wiederholen. Formuliere den Folgeauftrag
  anhand belegter Teilbefunde mit exakten Rest-Dateien, IDs, Tabellen/Abfragen
  und Suchmustern; verbiete erneute Repo-Erkundung, bereits erledene Code-Lektuere
  und breite Log-Suchen, damit das Budget fuer den fehlenden Beleg reicht.
  Erreicht derselbe Bot auch mit einem solchen engen Folgeauftrag erneut die
  Iterationsgrenze, starte ihn nicht zum dritten Mal mit derselben Diagnose:
  uebergib die konkreten Teilbefunde und nur die offene Pruefung an genau einen
  passenden Fachbot, sofern die serielle Gruppenregel (Recherche zuerst) bereits
  erfuellt ist. Ein mehrteiliger Analyse-Auftrag (Asymmetrie + Parametersuche +
  Tore) gehoert in getrennte Einzelauftraege, sonst frisst der erste Teil das Budget.
- **Ein "exhausted (5/5)"-Bot kann auf der ZENTRALEN Behauptung falsch
  liegen, nicht nur unvollstaendig sein.** Er kann das Budget verbraucht
  haben, BEVOR er den wichtigsten Fakt geprueft hat, und trotzdem eine
  vorlaeufige Diagnose liefern, die den Kern falsch nennt (Fall: Bot meldete
  "Dauerlauf-Prozess tot", obwohl er lief — er hatte den Prozess-Check nie
  gemacht). Die zentrale Behauptung eines erschoepten Bots IMMER selbst
  nachmessen (Prozess-Check, Datei-Existenz, Commit) bevor man sie an Max
  weitergibt; der Teilbefund ist eine Hypothese, kein Befund.
- **Bau-Bot gibt "exhausted (5/5)" zurueck, aber die Dateien sind geschrieben
  und die Tests zeigen konkrete rote Faelle: direkt auf dem Zweig verifizieren,
  die benannten Bugs selbst patchen, NICHT den Bau neu delegieren.** Ein
  Bau-Auftrag, der `fetch.py`+`config.json`+`README`+`tests/` schreibt und dann
  am Budget scheitert (Symptom: exit 1, nur `asyncio``closed pipe``-Teardown-am
  Ende), hat die Kernarbeit schon geleistet; der Bericht nennt die Parser-Bugs
  (z. B. stooq-Hinweiszeilen vor der Kopfzeile, leere Eingabe), die seine eigenen
  Tests gerade rot machen. Diese benannten Randfaelle sind vom Interpool direkt
  behebbar (ein `parse_stooq_csv`-Patch), statt einen zweiten Botlauf zu starten
  — ein Neustart zaehlt nur ein neues Tool-Budget auf einem fast fertigen Bau.
  Die Delegationsregel "nicht selbst ausfuehren" gilt fuer den Repo-Baum und
  fremde Fachbots; einen toten, benannten Klein-Bug im eigenen Build zu patchen
  ist Abschlussarbeit, kein Fremdeingriff.
- **Ein Bot, der mit `finish_reason='length'` / "No visible answer produced"
  endet, hat trotzdem echte Arbeit auf der Platte hinterlassen — oft UNCOMMITTET.**
  Das Ausgabe-Token-Limit ist ein anderer Abbruchmodus als der Iterationsbudget-
  Kollaps: der Bot macht 60+ Tool-Calls (editiert Dateien, laesst Tests laufen),
  aber seine Antwort wird nie sichtbar, weil das Reasoning das gesamte
  Ausgabe-Budget verbraucht. Vor dem Neustart IMMER `git status`/`git diff` im
  Ziel-Worktree pruefen und die uncommittete Arbeit sofort mit
  `--author="Hermes <hermes@local>"` committen (Regel 1: Sichern ist Pflicht) —
  sonst ist sie beim naechsten Schritt das Verlustrisiko. Gegenmittel im
  Folgeauftrag: explizit "eine Datei nach der anderen, bei vollem Kontext SOFORT
  committen und Zwischenstand melden statt weiterzumachen" — das zerlegt den
  Auftrag in committbare Haeppchen und rettet den Fortschritt vor dem Limit.
- **Ein grosses Codeprojekt NIE in EINEM Bot-Lauf — vorab in isolierte Schritte
  zerlegen, je ein eigener Bot-Lauf und Commit.** Ein Umbau ueber mehrere Dateien
  und ein Interface-Wechsel (z. B. swap als Familie-A-Spur: lade_wachen +
  pruefe_einstieg-Signatur + replay.py + spur_opt.json + Suche) sprengt das
  Output-Limit eines einzelnen Laufs: der Bot arbeitet eine Weile, wird bei
  "Response truncated (finish_reason='length')" abgeschnitten und verliert den
  Kontext. Die sichere Zerlegung: Schritt 1 = nur die Naht/Interface-Funktion +
  Suchbereich (klein, ein Commit), Schritt 2 = die eigentliche Strategie-Abbildung,
  Schritt 3 = Daten (Kerzen-Historie) + echte Suche. Jeder Schritt ist ein
  separater delegierter Lauf, der gut ins Limit passt. Und: erst nach dem ersten
  Schritt pruefen, ob Folge-Schritte ueberhaupt noch Blocker haben (z. B. `--trocken`
  braucht Kerzen-Historie, die fehlt — das gehoert als eigener Schritt erkannt).
- **Wenn Aufteilen auf EINE Datei trotzdem am Output-Limit scheitert, ist es ein
  Modell-/Aufgaben-Problem, kein Groessen-Problem — nicht weiter verkleinern,
  das Modell wechseln.** Belegt (swap→Familie-A-Umbau): auf eine einzige Datei
  reduziert (nur `pruefe_einstieg`/`pruefe_ausstiege` in handeln.py), und
  `jev-trader` (deepseek-v4-flash) verbrauchte trotzdem das ganze Budget im
  Reasoning ("reasoning consumed the entire budget on every continuation
  attempt"), kein Commit. Ursache: das Grid→Einzel-Position-Interface-Abbild ist
  konzeptionell komplex, das Reasoning frisst das Budget unabhaengig von der
  Dateizahl. Abhilfe: ein staerkeres Modell (deepseek-v4-pro, gpt-6-luna,
  claude) fuer genau diese Aufgabe umstellen statt weiter zu verkleinern, oder
  die Arbeit der zustaendigen Sitzung uebergeben.
- **Ein Bau-Bot, der an ``laenge()``/Kerzen-Daten scheitert, hat OFT eine Daten-
  Luecke statt eines Code-Defekts — die Historie holen ist ein eigener Schritt,
  kein Blocker fuer die Config-/Naht-Arbeit.** Schlaegt z. B. der Trockenlauf
  `optimieren.py --spur x --trocken` mit "keine Historie" fehl, weil
  `kerzenlaenge` VOR dem `--trocken`-Check laeuft, ist die Parametersuche erst
  nach dem Daten-Fetch (`historie_binance.py --auffuellen`) moeglich. Das als
  eigenen Folge-Schritt erkennen und committen, was darum herum schon fertig
  ist (Naht-Funktion, Suchbereich) — die Daten-Nachladung nicht Teil des
  bereits abgeschlossenen Config-Schritts werden lassen.
- **Ein Bau-Bot ohne Kontext auf der Platte gruebelt endlos statt zu bauen —
  das Lagebild als Spec-Datei ablegen und den Bot darauf verweisen.** Ein
  grosser Umbau-Auftrag, dessen Kontext nur in der Interpool-Konversation
  existiert (z. B. "swap zu Familie-A"), laesst den Bot im Repo nach dem
  Begriff suchen, findet nichts und wiederholt die Suche bis zum Timeout
  (exit 124) — er hat keinen Anker. Vor dem Delegieren das Lagebild als
  Markdown-Spec unter `Werkstatt/Projekte/<datum>-<thema>.md` schreiben
  (Ziel, gemessener Kontext, Schritte, Pflichten) und den Auftrag mit
  "Lies zuerst <pfad>" beginnen. Der Bot findet dann den Anker und arbeitet
  statt zu gruebeln; die Spec ist zugleich der Platten-Beweis fuer den
  Auftrag.
- **Ein Analyse-/Bestandsaufnahme-Auftrag muss benennen, WELCHE Dateien zu
  lesen sind (README, Einstiegsdateien, ggf. eine wachen.json) und darf
  teure Sondierungs-Kommandos ausdruecklich VERBIETEN.** Ohne das
geschieht
  Folgendes: der Bot macht einen teuren, haengenden Probe-Command (z. B.
  `du -sh` auf dem venv, der hier 180s auf den Tool-Timeout laeuft), der State
  wiederholt sich, und die 5-Iterationen-Budget ist aufgebraucht, bevor irgend
  eine inhaltliche Analyse lief — der Bot endet mit exit 0 + "exhausted (5/5)"
  und einem Leerbefund. Konkret in den Auftrag schreiben: "keine
  du/du -sh/venv-Groessenchecks (haengen 180s)", "lies nur <Liste>,
  nicht das ganze Repo", und explizit, dass KEIN Code eingespielt werden soll,
  wenn die Aufgabe rein bewertend ist.

## Neuen Repo-Bot anlegen (Klon + Profil + Doku)

Auftrag "<repo> zur Werkstatt und Agent anbinden" ist Pool-Infrastruktur, die
ich selbst ausfuehre — kein Fall fuer einen Fachbot. Reihenfolge:

1. **Klonen:** `git clone --quiet https://github.com/mfaupel95/<repo>.git
   Werkstatt/<repo>` (Junction → O:). `origin` = mfaupel95-Fork, dann
   `git remote add upstream <original>` (nur lesen, nie pushen).
2. **Profil anlegen:** `mkdir -p profiles/<repo>/skills`. config.yaml nach
   Vorlage eines kompakten Repo-Bots (z. B. `lotse`), aber `model.default` =
   `deepseek/deepseek-v4-flash-0731` (stabil) statt longcat (kollabiert in
   Schleifen); `terminal.cwd` auf `Werkstatt/<repo>`. SOUL.md nach Hausmuster
   (verweist auf `..\rule_repo-bots.md`), Repo-Skill `skills/<repo>-betrieb/`.
3. **Verifizieren:** `hermes profile list` zeigt das Profil; Smoke-Test
   `hermes -p <repo> chat -q "<eine Frage>"` (Kaltstart ~18 s, Antwort muss
   das Repo korrekt nennen).
4. **Committen:** nur eigene Pfade stagen (`git add <pfad>`), nie `-A`;
   `git commit --author="Hermes <hermes@local>"`. Danach `git branch
   --show-current` pruefen — muss der Integrationszweig sein.
- **Der Integrationszweig heisst NICHT ueberall `master` — vor jedem
  `git worktree add ... <zweig>` den echten Namen lesen.** Im BrainFiles-Repo
  kann der Integrationszweig umbenannt sein (beobachtet: `maks_master` statt
  `master`, mit `backup/maks-master-before-sync-*`-Sicherungen). Ein
  `git worktree add ../Handel-x -b <agent>/<thema> master` bricht dann mit
  `fatal: ambiguous argument 'master': unknown revision` ab. Vor dem Anlegen
  `git branch`/`git show-ref | grep -iE 'master|maks'` lesen und den
  tatsaechlichen Integrationszweig verwenden; `origin/HEAD` zeigt ihn
  (`remotes/origin/HEAD -> origin/maks_master`).
- **Der Integrationsname kann sich WAEHREND des Ports aendern (parallele
  Sitzung benennt um) — vor Port-Schluss die Bedachtnahme nicht auf die
  stale `master`-Ref stuetzen.** Ein temporaerer Worktree auf `master` und
  der Cherry-pick können gelingen, waehrend eine parallele Sitzung den Zweig
  auf `maks_master` umbenennt; danach schlagen alle spaeteren `master`-Verweise
  fehl (`fatal: invalid object name 'master'`) und die Worktree-Cleanup-Fehlermeldung
  "<pfad> is not a working tree" ist dann normal (die Sitzung hat ihn schon
  entfernt), kein Beleg fuer einen fehlgeschlagenen Port. Den Commit-Stand
  deshalb am AKTUELLEN Integrationszweig belegen, nie an der stale Ref:
  `git branch --show-current`-Ort + `git merge-base --is-ancestor <commit>
  <zweig>` (Exit 0 = drin) + `git cat-file -e <zweig>:<pfad>` (Datei da)
  + `git log --oneline -1 <zweig>` die erwartete Message. Erst wenn das
  traegt, den Port als auf master/maks_master verifiziert melden und die
  temporaeren Zweige/Worktrees loeschen (`git branch -D <temp>`, `git
  worktree prune`).
5. **Doku:** Zeile in die Flottenstand-Tabelle von
   `MaxHirn/Wissen/Repo-Bots.md` (alphabetisch einsortieren) + `updated` im
   Frontmatter hochsetzen; committen.

Fallen:
- **`hermes profiles` ist kein Befehl** — es heisst `hermes profile list`.
- **`write_file` verweigert das Ueberschreiben von `SOUL.md`**, weil das
  Profil-Scaffold beim `mkdir` schon eine Default-SOUL.md (nur der
  Standard-Text) anlegt. Erst `read_file` auf die vorhandene SOUL.md, dann
  ueberschreiben.
- **Verwaister `.git/index.lock`:** `git commit` bricht mit "index.lock
  exists" ab. Der Lock allein sagt nichts — **verwaist heisst: kein
  Git-Prozess lebt, nicht "der Lock ist alt".** Zwei Zeugen pruefen:
  `stat -c '%y' .git/index.lock` (Alter) UND `tasklist | grep -iE '^git.exe'`
  bzw. `ps aux | grep git`. Entscheidend ist der Verlauf ueber ZWEI Messungen:
  wechseln die git.exe-PIDs zwischen den Checks, committen gerade fremde
  Sitzungen — warten, nicht eingreifen. Ist in einer Messung KEIN git.exe da
  und der Lock aelter als ein paar Minuten, ist er tot: `rm -f
  .git/index.lock` und sofort committen. Ein 30 min alter Lock mit lebenden
  Prozessen ist NICHT verwaist; ein 2 min alter ohne Prozess schon.
  **`git fsmonitor--daemon`-Prozesse zaehlen NICHT als lebende Git-Operation**
  — sie erscheinen als `git.exe` in tasklist, halten aber keinen index.lock
  und committen nichts. Vor dem Urteil "Git laeuft noch" die CommandLine
  pruefen (`Get-CimInstance Win32_Process` auf `git.exe`): sind alle nur
  `fsmonitor--daemon run --detach`, ist der Lock trotz lebender git.exe
  verwaist und darf entfernt werden.
- **Kein automatischer Live-Betrieb.** Ein neuer Repo-Bot baut/testet/bewertet
  Strategien, oeffnet aber keine Positionen und bekommt keine Spur im
  `dauerlauf`. Eine echte Handelsspur (Statusdateien lesen → ins Buch buchen)
  ist ein separater Bau in `Agenten/Handel/` mit `wachen.json` — nur auf
  ausdruecklichen Auftrag, dann an den passenden Handel-Bot delegieren.
  - **Den Handel-Bau-Bot ueber `terminal.cwd` waehlen, nicht ueber den Namen.**
    Eine Spur im Betriebsbereich wird nur von einem Profil gebaut, dessen
    `cwd` auf `Agenten/Handel` zeigt (hier: `markt-recherche`) — die
    Repo-Fork-Bots (`jev-trader`, `agent-trade-kit`, `awesome-systematic-trading`,
    `harvard-trading`, `fomo-radar`, ...) starten alle in `Werkstatt/Repos/<repo>`/
    bzw. `Werkstatt/<repo>` und bauen/testsen Strategien, schreiben aber nicht
    in den Betriebsbereich. Vor dem Delegieren aller Profile die `cwd`-Zeile
    der `config.yaml` pruefen (`grep -A3 'terminal:' <p>/config.yaml | grep cwd`
    oder `grep -rl 'Agenten/Handel' */config.yaml`) statt nach einem
    Bot-Namen mit "handel" zu suchen.

## Bot-Flotten-Audit (Beschreibungen, Regeln, Skills)

Auftrag "pruefe in allen Profilen Beschreibungen, Regeln und Skills" ist
Flotten-Hygiene, die ich selbst ausfuehre (lesend) oder an einen Subagenten
delegiere — kein Fachbot. Die drei Pruefstellen je Profil:

- **Beschreibung:** `profiles/<name>/profile.yaml` Feld `description` (die
  `/bots`-Anzeige liest DIESE Datei, nicht config.yaml). Aussagekraeftig =
  nennt Repo/Zweck; dupliziert = geklonte Kopien (z. B. zwei Profile mit
  wortgleichem "Moon-Dev-Repo-Bot"); fehlt = kein description-Feld.
- **Regeln:** `profiles/<name>/SOUL.md` — verweist es auf die gemeinsame
  `..\rule_repo-bots.md`? Die Regeldatei existiert zentral in `profiles/`;
  ein SOUL ohne Verweis bindet die gemeinsamen Grenzen nicht ein. Generische
  SOULs (nur Stiltext, keine Rollen-/Grenzenregeln) sind der haeufigste
  Qualitaetsmangel.
- **Skills:** `profiles/<name>/skills/` erste Ebene — die 12 Standard-
  Kategorien (apple, creative, devops, email, media, note-taking,
  productivity, research, social-media, software-development, web,
  autonomous-ai-agents) plus profil-spezifische. Missverteilung = ein
  fachfremdes Paket (okx-*, handel, smart-home, geld) auf Repo-Bots kopiert,
  die es nicht brauchen. Lose `.txt`-Dateien direkt in `skills/` (z. B.
  `aspect-reviewer.txt`) gehoeren in einen Skill-Unterordner mit SKILL.md.

**Fachfremde Skills reversibel entfernen, nicht hart loeschen:** in einen
`_fachfremd-bak-<datum>`-Ordner im selben `skills/` verschieben statt `rm`.
`Agenten/Hermes` ist Stufe 1 — reversibel ist sicherer, und die geloeschten
Skills sind ohnehin im git-Verlauf. Vor dem Loeschen pruefen, dass die
Skill-Ordner echte Kopien sind (unterschiedliche inodes), nicht geteilte
Symlinks — sonst trifft das Loeschen andere Bots.

**Subagent-Berichte ueber Flotten-Aenderungen IMMER selbst nachmessen**
(grep auf den entfernten Token, `git log` auf den Commit, YAML-Validierung)
— ein Subagent kann "0 Treffer" melden, waehrend der ollama-Provider noch da
ist (siehe Abschnitt MAGDA: paralleler Commit setzt Migration zurueck).

## Lokale Modelltests delegieren

- Vor einem Modellstart den vorhandenen Modellserver und GPU-Belegung pruefen;
  Modell-Dateigroesse ist nicht gleich Runtime-VRAM. Niemals einen bestehenden
  Server entladen oder stoppen, um einen Test freizumachen.
- **Ein lokales Modell fuer die Bot-Flotte waehlt man nach VRAM, nicht nach
  Dateigroesse — und die Generationsgeschwindigkeit MESSEN, nicht nur pruefen,
  dass es antwortet.** Auf der 8-GB-GPU (RTX 3060 Ti) spillt ein 12B-Modell
  (7,1 GB) + KV-Cache auf CPU und laeuft mit ~2 tok/s (fuer Agent-Betrieb
  unbrauchbar), waehrend ein 9B-Modell (5,7 GB) mit ~14 tok/s passt. Vor der
  Wahl `nvidia-smi --query-gpu=memory.used,memory.total` lesen und nach dem
  Load einen echten Request mit `max_tokens` schicken und
  `timings.predicted_per_second` auswerten. Ein Modell, das nur antwortet,
  aber zu langsam generiert, ist fuer die Bots wertlos.
- **`ctx-size` im Preset auf das setzen, was der VRAM haelt, nicht auf das
  Modell-Maximum — ein zu grosses Fenster laesst den llama-server crashen.**
  262144 mit q8_0-KV-Cache OOM auf 8 GB VRAM und beendet den Server (Port
  zu, kein Prozess mehr). 131072 mit q4_0-KV-Cache passt. Nach einem
  Load-Crash den Server neu starten und das Fenster verkleinern, statt das
  Modell zu verwerfen.
- **Ein zweiter llama-server/ollama kann den VRAM halten und Modell-Loads mit
  `cudaMalloc failed: out of memory` scheitern lassen — vor dem Test
  `nvidia-smi --query-compute-apps=pid,used_memory,process_name` pruefen.**
  Eine zweite ollama-Installation (z. B. auf G:) hat einen eigenen
  llama-server, der ein Modell auf der GPU haelt; dann passt das zu testende
  Modell nicht mehr rein. Den fremden Server stoppen (wenn verwaist — alle
  Profile nutzen llamacpp), dann neu laden.
- **Modell-Downloads mit `hf`, nicht `huggingface-cli` — das ist deprecated
  und bricht mit exit 2.** `hf download <repo> <datei> --local-dir <ziel>`
  (z. B. `hf download unsloth/Qwen3.5-9B-GGUF Qwen3.5-9B-Q4_K_M.gguf
  --local-dir O:/Modelle/GGUF/qwen3.5-9b`). Danach Symlink in
  `Agenten/Hermes/models/` anlegen und ein Preset in
  `runtimes/llamacpp/presets.ini` ergaenzen (ctx-size, batch, cache-type,
  flash-attn, model-Pfad).
- Ein ausdruecklicher Testauftrag erlaubt nur den benoetigten Test, keine
  Downloads, Konfigwechsel oder Handelsaktionen. Smoke-Prompts belegen nur, dass
  ein Modell antwortet; fuer Signalqualitaet den vereinbarten Vertrags-/Eval-Satz
  ausfuehren und die Stichprobe nennen.
- Fehlen bei einem Repo die Checkpoints, Unit-/Routing-Tests von echter Inferenz
  trennen; keine Gewichte ohne ausdrueckliche Download-Freigabe nachladen.
- Hat der Bot selbst einen Testserver gestartet, PID/Endpoint notieren und den
  eigenen Prozess nach der Messung sauber beenden, sofern das erlaubt ist. Einen
  fremden Prozess nie beenden; wenn der eigene nicht sauber stoppbar ist, klar
  melden, dass er weiterlaeuft, und keinen sauberen Abschluss behaupten.

## FOMO-Telegram-Listener

Bei `/start`- oder Polling-Problemen den Ablauf in
`references/fomo-telegram-listener.md` verwenden. Der Telegram-Poller
(`fomo_agent.cli bot`) ist von Pipeline-`cli watch` und `cli receive` getrennt.

## fomo-radar Score-Workflow
- Ablauf: `score --export` -> Verdicts beurteilen (ok/skip, per LLM-Workflow des
  Bots oder im Chat) -> `score --import <results>`. Ein `--import` ohne neue
  Verdicts ergibt NICHTS.
- **Parallele fomo-radar-Sitzungen koennen dieselbe Queue abarbeiten — vor einem
  Score-Job den IST-Stand in der DB pruefen, nicht dem letzten Bericht glauben.**
  Mehrere delegierte Auftraege (Cron + Chat) koennen dieselben Wallets schon
  gescort haben; ein neuer `score --export` findet dann `exported: 0` und ein
  Re-Score wuerde heutige Kontexte ueberschreiben und die Rescore-Fenster
  (72 h watch / 14 d dropped) verletzen. Vor dem Start die Verteilung in der DB
  lesen (`SELECT status, COUNT(*) FROM traders GROUP BY status`,
  `SELECT COUNT(*) FROM score_history WHERE date(ts,'unixepoch')=date('now')`)
  und `docs/STATUS.md`-Session-Eintraege; ist die Queue leer, KEINEN Score-Job
  starten und das als erledigt melden.
- `pending_scores.json` liegt im Repo-Root. Struktur: dict mit
  `wallets` (52+), je Wallet: address, chain, source, fomo, indexer_stats
  (fills, buys, sells, closed_trades, wins, win_rate, realized/unrealized/net
  pnl, open_bags).
- Fallen: absurde unrealized-Betraege (Trillionen/Billionen) sind Datenfehler -
  skip, keine Trader. Leere Wallets (0 fills, 0 bags) sind nur Adressen, kein
  Scoring moeglich - skip. Aehnliche/schon bekannte Wallets (z. B. game_for_one)
  koennen schon gescort sein.
- GPU-Engpass: fremder llama-server kann die GPU halten; Scoring-Modell faellt
  von qwen3.5 auf gemma-e4b-8k-64k zurueck, wenn cudaMalloc failed (OOM).
- Repo-Pfad ist UNSTABIL und wechselt zwischen `O:\Werkstatt\Repos\fomo-robinhood-radar` und `C:\Users\faupe\Documents\BrainFiles\Werkstatt\fomo-robinhood-radar` (beide wurden 2026-10 beobachtet; der C:-Junction-Unterpfad existierte zeitweise nicht). Einen leeren Check nicht als "Repo weg" deuten — erst beide Pfade pruefen. Im Auftrag an den Bot beide Kandidaten nennen und ihn das Repo selbst lokalisieren lassen, statt einen Pfad hart zu verdrahten.
- **Das fomo-radar-Profil hat einen EIGENEN Pipeline-Cron** (`profiles/fomo-radar/cron/jobs.json`, Job `0708b8f2725d`, alle 6 h `run --once` gegen das Repo). Vor dem Anlegen eines "fomo-radar Loop"-Crons im bots-Profil erst pruefen, ob das fomo-radar-Profil selbst schon einen laufenden Loop hat — ein zweiter ist Doppelarbeit und wird pausiert. Der fomo-radar-eigene Cron ist der echte Pipeline-Loop; ein bots-Cron dafuer ist redundant.
- **Ein `cli watch`-Prozess ist ein BAUM, kein Einzelprozess — zwei gleich aussehende `python.exe -m fomo_agent.cli watch` sind Eltern-Kind DESSELBEN Watchers, kein Duplikat.** Beim Watcher-Restart/Chaos-Check nie nach der Commandline allein urteilen: `Get-CimInstance Win32_Process` und `ParentProcessId`/`CreationDate` pruefen (bash→env→python→python-Kette). Nur ein Prozess OHNE Eltern-Kind-Beziehung zu einem anderen watch ist ein echter Doppel. Der Skill-Warnhinweis "ein Dauerlauf hat zwei python-Prozesse" gilt hier genauso.
- **Watcher-Restart braucht KEIN LLM — reiner Prozessstart, direkt vom Interpool machbar, auch wenn das Bot-Modell-Guthaben erschöpft ist.** `cd <repo> && env -u PYTHONPATH -u PYTHONHOME PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe -m fomo_agent.cli watch` als `terminal(background=true, persist_on_release=true)` (kein notify — Dauerprozess). Bar aus `HOT_DELTA` in `config.py`/`.env` pruefen (Default 1.0). Danach verifizieren: genau EIN Baum, tickt.
- **Ein delegierter Job, der mit `HTTP 402: Insufficient available credits` + Fallback auf ein lokales Modell mit zu kleinem Kontext stirbt, ist ein ABRECHNUNGS-/KONTEXTPROBLEM, kein Aufgabenproblem — nicht blind neu delegieren.** Der Fallback (z. B. gemma-4-E4B, 65k) kann den Auftrag nicht lesen ("conversation too long"). Erst das Primärmodell-Guthaben aufladen oder fomo-radar auf ein Modell mit grossem Kontext setzen; ein erneuter Versuch laeuft sonst in denselben Fehler. Teile, die kein LLM brauchen (Watcher, Prozess-Checks), direkt selbst machen.
- Keys nie ausgeben. Echte Zugaenge nur in `MaxHirn/Wissen/Zugaenge.md`.

## fomo-radar fomo-family-Discovery
- `fomo-radar discover leaderboard` (Perioden 24h/7d/30d) + resolve_execution_wallets
  fuellt `fomo_users`; `discover trenches` fuellt `traders` direkt. `fomo_users` kann
  LEER sein, waehrend der Roster komplett aus trenches kommt — das ist kein Fehler,
  sondern heisst nur, dass die Leaderboard-Discovery nie lief. Vor einem
  Discovery-Auftrag den Ist-Stand in der DB pruefen (`SELECT source, COUNT(*) FROM
  traders GROUP BY source`, `SELECT COUNT(*) FROM fomo_users`), nicht dem STATUS.md-Text
  glauben.
- FOMO_SESSION in .env ist der Cookie/Bearer; Gueltigkeit pruefen mit
  `FomoClient.leaderboard` (wirft FomoError/FomoNotConfigured bei ungueltiger
  Session), nicht am Vorhandensein des Keys raten. Ein Discovery-Auftrag an den Bot
  soll explizit sagen, dass er die Session-Gueltigkeit pruefen und das Ergebnis
  (neue fomo_users je Periode, neue Trader nach Resolve, Session ok/Fehler) melden soll.

- **SkillsBot "leere Antwort" = der A2A-Gateway (Port 9900, `hermes-maks-pc`)
  beantwortet Tasks mit leerem Inhalt, NICHT der SkillsBot.** Symptom: der
  SkillsBot antwortet nur mit `Angenommen.` (im Log `zeichen: 11`), und
  `python skillsbot.py --probe` endet bei `A2A-Ping: (leere Antwort)`. Der
  SkillsBot ist dann gesund (Telegram-Bot angemeldet, Gateway-Port offen,
  Skills geladen) — der Fehler liegt darin, dass der A2A-Agent sofort
  `TASK_STATE_COMPLETED` meldet, aber die Task weder `message.parts` noch
  `artifacts` traegt.
- **Warum die Task leer ist: der Gateway STREAMT die Antwort und legt sie
  nicht in den Task-Status.** Das Gateway-Log zeigt `Suppressing normal final
  send ... content_delivered=True` und `response ready: ... response=N chars`
  — die Antwort existiert, wird aber als gestreamt markiert. Der A2A-Adapter
  `_emit_terminal` schreibt `artifact_update` nur wenn `reply` nicht leer ist,
  und der Gateway liefert `reply=""` an den Adapter, weil er die Antwort
  selbst gestreamt hat. Deshalb kommt die Antwort weder in `message.parts`
  noch in den SSE-Stream — egal ob der Client `SendMessage`+`GetTask`-Polling
  oder `SendStreamingMessage` nutzt. Ein reiner skillsbot-seitiger Wechsel auf
  `SendStreamingMessage` behebt das NICHT; der Fix liegt im A2A-Adapter
  (gestreamte Antwort als `artifactUpdate`/`statusUpdate.message`
  weitergeben) oder darin, Streaming fuer den lokalen Agenten zu deaktivieren
  (`streaming=bool(agent.get("local", True))` in `_build_card`).
  **Es gibt KEINE Konfig-Option, das Streaming abzuschalten** —
  `streaming=bool(agent.get("local", True))` ist fuer lokale Agents hart
  gesetzt, kein config.yaml-Schalter. Nicht nach einem Toggle suchen; der
  Fix ist ein Adapter-/Gateway-Patch oder ein Gateway-Neustart (der
  haeufigste praktische Fix fuer einen "gesund aber leer haengenden"
  Hauptagenten). Das direkt reproduzieren statt zu raten:
  `env -u PYTHONHOME -u PYTHONPATH python -c "import skillsbot; ..."` mit
  `SendMessage` + `GetTask` auf 127.0.0.1:9900 — zeigt eine Task ohne Text,
  ist der Hauptagent das Problem, nicht die Bruecke. Vor einem SkillsBot-Bug
  den `skillsbot.log`-Antwortlaengen-Wert pruefen: `zeichen: 11` = der Ack
  `Angenommen.`, die eigentliche Antwort laeuft asynchron und fehlt.
- **Leere-Antwort-Diagnose: Log-Flut von `Blocked unauthorized user <id>` ist
  Sekundaerlaerm, kein Beleg fuer einen A2A-Ausfall.** Fremde Nutzer-/Bot-IDs,
  die die Gruppe im Sekundentakt pollen, schreiben haufenweise
  `Blocked unauthorized user ... in chat -1003980261765` in errors.log und
  koennen den Hauptagenten in Wiederholungsschleifen druecken (sichtbar als
  `A2A: anti-loop triggered ... turn N > 5` im agent.log). Diese Zeilen nuetzen
  nur, um die SECUNDAERE Belastung zu benennen; den A2A-Zustand belegen die
  `kommando`-Zeilen mit `zeichen: 11` und der direkte `SendMessage`-/`GetTask`-
  Test gegen 9900. Der konkrete, uebliche Fix fuer einen "gesund aber leer
  haengenden" Hauptagenten ist ein Neustart des Haupt-A2A-Gateways — den
  laufenden Prozess aber erst nach Max' Freigabe anfassen.
- **Den Gateway-Neustart NICHT an `hermes-wartung` delegieren — es verweigert
  ihn regelkonform.** hermes-wartung hat die Betriebsgrenze "laufende Prozesse
  nicht anfassen" und bricht einen Neustart-Auftrag sauber ab ("Ich kann den
  Gateway nicht neu starten"), statt ihn auszufuehren. Der Neustart ist
  Interpool-/Max-Sache: entweder selbst ueber den offiziellen Launcher
  (`gateway run --replace` oder der VBS-Launcher mit Doppelstart-Schutz, siehe
  `Agenten/Routinen/gateway-waechter.ps1`) nach Max' Freigabe, oder — wenn die
  Ursache ein Code-Bug ist — hermes-wartung mit einem CODE-Fix-Auftrag
  beauftragen ("untersuche und behebe, wo final_response leer bleibt"), nicht
  mit einem Restart-Auftrag. Ein Code-Fix-Auftrag ist hermes-wartungs Bereich;
  ein Restart-Auftrag ist es nicht.
- **"COMPLETED ohne Inhalt" bei gleichzeitig laufenden API-Calls im agent.log
  ist ein A2A-Dispatch-Bug, kein Neustart-Fall.** Zeigt `agent.log` echte
  Modell-Calls (`API call #N: model=... in=... out=...`), arbeitet der Agent
  — die Antwort geht nur nicht in die Task zurueck. Die Naht ist
  `plugins/platforms/a2a/adapter.py` (liest `result.get('final_response')`)
  und `gateway/session_a2a.py::forward_to_owner`. Ein Neustart heilt das
  nicht; der Fix ist ein Adapter-/Gateway-Patch. Erst wenn der Agent GAR
  NICHT arbeitet (keine API-Calls), ist ein Neustart der richtige Hebel.

## Gruppenchat mit Telegram-Forum-Topics seriell dispatchen

- „Alle Bots verfügbar“ bedeutet: Fachprofile über den einen Gruppeneingang aufrufbar, nicht jeder mit eigenem Telegram-Token. Halte genau ein gruppenempfangendes Profil; unabhängige Tokens können parallel antworten, und zwei Poller für denselben Token erzeugen Telegram-409. Bei fachlichen Gruppenanfragen genau einen Auftrag an `recherche` senden, dessen Ergebnis abwarten, danach höchstens einen passenden Fachbot starten; kein Fan-out.
- `gateway.profile_routes` waehlt fuer ein einzelnes Inbound-Ereignis genau ein Runtime-Profil; es ist kein Recherche->Dispatcher-Workflow. Soll Recherche pruefen und ein Dispatcher danach handeln, route die Gruppe an den Dispatcher und verankere die serielle Weitergabe in dessen Arbeitsanweisung. Route ein Topic direkt zu Recherche, wenn es selbst antworten soll, nicht wenn danach automatisch ein zweites Profil erwartet wird.
- Forum-Themen lassen sich nach `platform` + `chat_id` + `thread_id` routen; vor Topic-Routen die effektive `gateway.profile_routes` lesen und jedes Zielprofil gegen `profiles/<name>/config.yaml` pruefen. Topic-Links koennen Nachrichten-IDs enthalten: niemals die letzte URL-Zahl ungeprueft als `thread_id` einsetzen. Nimm die empfangene `message_thread_id`/SessionSource-`thread_id` aus einer echten Nachricht oder verifiziere sie in der Session-Datenbank.
- Eine Chat-weite Route und spezifische Topic-Routen koennen nebeneinander bestehen; spezifischere Routen gewinnen (thread_id-Spezifitaet 8 > chat_id 4). Nach dem Edit die effektive Route fuer alle Topics aufloesen und nachweisen, dass jedes Inbound-Event nur ein Zielprofil trifft — `parse_profile_routes`/`match_profile_route` aus `gateway/profile_routing.py` gegen die config laufen lassen (Sim je thread_id), bevor der Gateway neu startet.
- **Die Routen-Simulation braucht `adapter_profile=None`, sonst ist das Ergebnis eine Falschmeldung.** Die Routen in der config tragen `bot_profile: null` (Default-Bot, der den geteilten Gruppen-Token pollt); `match_profile_route` matcht nur, wenn `_bot_profile_key(self.bot_profile) == _bot_profile_key(adapter_profile)`. Uebergibt die Sim `adapter_profile='bots'` (das ROUTED Zielprofil), wird JEDE Route abgelehnt und jede Topic simuliert "KEIN TREFFER (dropped)" — das sieht wie eine kaputte Config aus und ist nur ein Simulations-Artefakt. Der Aufruf lautet `match_profile_route(routes, 'telegram', chat_id='-1003980261765', thread_id=tid, adapter_profile=None)` (None = Default/Bot-Besitzer), nicht der Ziel-Profilname.
- **Thread-IDs gegen die Session-DB verifizieren, nicht gegen die Zuordnungs-Doku:** `SELECT thread_id, title, session_key FROM sessions WHERE chat_id='-1003980261765'` in `profiles/bots/state.db` (bzw. den Session-Registry-`sessions.json`, dessen Keys `...:telegram:group:-1003980261765:<tid>` die wirklich benutzten Threads zaehlen). Nur ein thread_id, der dort als echte Session existiert, ist belegt; ein Eintrag in der `Telegram-Themen-Bot-Zuordnung.md` oder die Zahl aus einem t.me/c/-Link beweisen allein keine Topic-ID.
- **Ein TASKS-Eintrag, der behauptet "die Topics existieren nicht", kann veraltet sein — die Existenz gegen den Session-Registry messen, nicht dem Eintrag glauben.** Belegt: T-431 behauptete "nur Threads 615 und 1 existieren", waehrend `sessions.json` reale Sitzungen fuer 1998/1999/2000/2001/2006/723 (und 1989/2002) zeigte. Der aus der Registry gezogene Thread-Satz ist die IST-Wahrheit; ein TASKS-Text oder eine Notiz ist nur der Stand beim Anlegen. Dieselbe Gegenprobe gilt fuer BEIDE Richtungen: weder "Topic fehlt" noch "Topic verdrahtet" aus dem TASKS-Text uebernehmen, ohne vorher die Route aus dem aktuellen Arbeitstand zu simulieren.
- **`config.yaml` im geteilten Baum kann eine uncommittete Aenderung einer parallelen Sitzung tragen — den Arbeitstand lesen, nicht die aus der Doku/aus dem Skill gelernte Zuordnung.** Eine Zuordnung (z. B. Handel→jev-trader, Auswertung→recherche) kann am HEAD stimmen, waehrend der Working-Tree sie bereits zu `bots` abgeflacht hat (git `M`, uncommittet, mtime heute). Vor einem Routen-Urteil `git status --short`/`git diff` gegen `Agenten/Hermes/config.yaml` pruefen und die effektive Route aus dem AKTUELLEN Arbeitstand simulieren; die Simulation beantwortet das IST, die Doku nur den Entwurf. Eine solche fremde, lebende Aenderung nicht ueberschreiben oder committen, sondern dem Nutzer als klärungsbedürftig melden.
- **Thread-IDs verifizieren, nicht raten:** Eine `t.me/c/<gruppe>/<id>`-URL kann eine Nachrichten-ID enthalten; sie beweist nicht allein die Topic-`thread_id`. Nutze die tatsaechliche Telegram-`message_thread_id` aus einem eingegangenen Update oder einem gespeicherten Session-Eintrag (`sessions.thread_id` fuer dieselbe `chat_id`). Topic-Namen den IDs nur zuordnen, wenn der Nutzer sie benennt oder die Topic-Metadaten das belegen; sonst nachfragen.
- **Ein Topic = genau EIN Profil.** `profile_routes` kann pro (chat,thread) nur ein Zielprofil haben. Eine Zuordnung mit mehreren Bots pro Topic (z. B. 6 Handel-Bots) ist nicht abbildbar — vor dem Bau die federfuehrenden Bots je Topic mit Max klaeren; die uebrigen bleiben ueber `/bot NAME` im Dispatch erreichbar. Ziel-Profile muessen existieren und ein gueltiges `model.default`/`provider` haben (Multiplex laedt sie).
- **Die Ein-Profil-pro-Topic-Grenze ist Kern-Gateway-Logik, kein Plugin-Schalter.** `match_profile_route` (installierter Quelltext `hermes-agent/gateway/profile_routing.py` + Tests) hat pro Inbound-Event GENAU ein Ergebnis; es gibt keinen Plugin-Mechanismus, der daraus mehrere Empfaenger pro Topic macht. Behauptet Max ein "Plugin", das das koennte, nicht glauben: den Plugin-Katalog tatsaechlich listen (`hermes plugins`, `grep -i bots`) — fehlt der Name dort, ist es ein Fehlname (meist ist das `bots`-Profil gemeint). Verloren gegangene Suchschleife: mehrere identische `search_files`-Queries, die dasselbe Ergebnis liefern, sind ein degenerativer Modell-Loop, kein Fortschritt — sobald ein Query-Zyklus kein neues Ergebnis bringt, auf eine gezielte Lesequelle (config.yaml, Quelltext) wechseln und dem Nutzer die Antwort geben statt weiterzusuchen.
- **Vor einem Routing-Vorschlag erst die BESTEHENDE Wahrheit lesen.** `Agenten/Hermes/config.yaml` → `gateway.profile_routes` kann schon verdrahtet sein (Dispatch→bots, Handel→jev-trader, Auswertung→recherche, Wissen→obsidian-skills, Bots→gbrain, Wartung→hermes-wartung fuer -1003980261765). Keine Zuordnung von Grund auf entwerfen und als "neu" anbieten, bevor man die aktive Route gelesen hat; haeufig deckt sie den Entwurf bereits ab. Die Zuordnungs-Doku fuer die Gruppe: `profiles/bots/Telegram-Themen-Bot-Zuordnung.md`.
- Eine SOUL-/Profilregel-Aenderung beweist nicht, dass bereits laufende Topic-Sitzungen sie geladen haben: erst in einer neuen Sitzung pruefen; keinen Gateway-Neustart ausloesen, wenn er alle laufenden Profile beeintraechtigen kann.
- **`hermes gateway restart` verweigert sich von INNEN des Gateways — und auch ein abgetrennter Start weigert sich ohne `--yes`, solange eine Live-Session laeuft.** Der direkte Aufruf aus einer am Gateway haengenden Shell wird blockiert ("cannot restart from inside the gateway"); via `Start-Process`/detached laeuft er, bricht aber ab mit "Refusing to restart ... 1 live session(s) would be interrupted" und nennt die betroffene Session (genau die, aus der man antwortet). Das ist kein Fehler, sondern Schutz: der Neustart beendet die laufende Telegram-Sitzung. Ein korrigierter `profile_routes`-Satz wird also erst beim naechsten natuerlichen Neustart aktiv, es sei denn man opfert die aktive Session. Vor so einem Schritt Max die Wahl geben: er startet in einem separaten Terminal `hermes -p <profil> gateway restart --yes` (Sofort-Aktivierung, bricht diese Unterhaltung kurz) ODER der naechste ohnehin anstehende Neustart uebernimmt die config. Signale: `hermes gateway status` nennt das aktive Session-PID und dass `default`/`codex-programming` denselben Token teilen (ein Token bedient nur EIN Gateway; der andere Adapter parkt) — das ist eine separate Drift, kein Routing-Problem.

## "Weiter" ohne Kontext: erst rekonstruieren, dann pruefen, ob schon erledigt

Sagt Max nur "Weiter" (oder "weiter wo aufgehoert wurde") ohne Auftrag, ist der
letzte echte Auftrag NICHT im aktuellen Kontext — er liegt in einer frueheren
Sitzung. Vor jeder Aktion:

1. **Den letzten echten Auftrag aus der Sitzungshistorie rekonstruieren**
   (`session_search` mit `sort=newest`, dann in die gefundene Sitzung scrollen
   bis zur letzten User-Nachricht). Nicht raten, was gemeint sein koennte.
2. **Pruefen, ob die Arbeit schon erledigt und committet ist, BEVOR man sie
   wiederholt.** Eine parallele Sitzung kann den Auftrag laengst ausgefuehrt
   und committet haben. `git diff HEAD -- <pfad>` leer UND `git log -1 --
   <pfad>` zeigt einen passenden Commit = die Arbeit ist getan; das als
   erledigt melden statt sie neu zu machen. Das gilt besonders fuer
   Stilllegungen/SPUREN-Aenderungen, die eine andere Sitzung schon committet
   haben kann.
3. Erst wenn weder Historie noch HEAD die Arbeit belegen, den Auftrag
   ausfuehren oder delegieren.

**Wenn die unterbrochene Arbeit ueber `delegate_task`-Subagenten lief, ist die
Wiederaufnahme eine Verifikation, kein Neustart.** Die Subagenten laufen
unabhaengig von der abgeschnittenen Eltern-Sitzung weiter und committen ihre
Ergebnisse selbst. Wiederaufnahme-Reihenfolge:

1. `cache/delegation/live/<id>/manifest.json` lesen — `status` je Task
   (`completed`/`failed`) und `completed`-Zeitstempel. Ein `failed`-Task mit
   "model's reply was cut off" hat NICHTS geaendert (Output-Limit vor der
   ersten Aktion); ein `completed`-Task hat gearbeitet.
2. `git log --oneline -N` im Zielbaum: die Subagenten-Commits stehen schon da
   (Autor `Hermes`, Betreff nennt die Gruppe). `git status --short` auf
   uncommittete Reste pruefen.
3. `cache/delegation/live/<id>/task-<n>.log` tailen (ANSI rausfiltern) fuer
   die Abschluss-Zusammenfassung je Task — die Eltern-Sitzung wurde
   abgeschnitten, BEVOR sie die konsolidierte Meldung an Max schrieb.
4. Erst was in keinem Manifest/Commit/Log steht, selbst ausfuehren oder neu
   delegieren.

**Ein Subagent, der an einer Freigabe-Huerde stoppt, tut NICHTS und meldet
"Dateien geaendert: keine" — das ist ein stiller Fehlschlag, kein
Teilergebnis.** Ein Hintergrund-Subagent kann keinen interaktiven
Freigabe-Dialog beantworten; ein Write, der eine Freigabe ausloest, blockiert
und der Task endet `completed` mit leerem Ergebnis. Nach so einem Lauf
`git status`/`git diff` pruefen: ist wirklich nichts geaendert, die kleine
Aenderung direkt im eigenen Kontext ausfuehren (die Dateien sind lesbar, das
Muster frisch) statt einen weiteren Subagenten zu starten, der an derselben
Huerde wieder stoppt.

## Systempruefung (systempruefung.ps1)

`Agenten/Routinen/systempruefung.ps1` ist die taegliche Diagnose (~7 min).

- **Immer im Hintergrund mit notify starten** — der Foreground-Timeout (300 s) reicht nicht; der Lauf schreibt erst am Ende den Bericht. `terminal(background=true, notify=true, command="powershell -NoProfile -ExecutionPolicy Bypass -File Agenten/Routinen/systempruefung.ps1 -NurPruefen")`.
- **`-NurPruefen` fuer Handlaeufe** (kein Auto-Aufraeumen); der volle Lauf raeumt eindeutig reproduzierbare Orphans selbst weg.
- **Bericht:** `Agenten/Routinen/logs/systempruefung-letzter-lauf.md` (strukturiert: Seit gestern neu / Selbst erledigt / Zu entscheiden / Zur Kenntnis). Vollprotokoll: `logs/systempruefung-<datum>.log`.
- **Kann in der Git-Pruefung haengen** (git-Prozesse bleiben stehen, kein Bericht). Haengt ein eigener Lauf >10 min ohne Bericht, den eigenen Lauf beenden und den letzten Bericht lesen statt weiter zu warten.

## Prozessdiagnose auf Windows (und warum Bot-Diagnosen nachzumessen sind)

Details und fertige Kommandos: `references/windows-prozessdiagnose.md`.

- **`ps` / `ps -ef` aus git-bash ist auf diesem Host UNBRAUCHBAR fuer
  Prozessdiagnose — es sieht nur einen Bruchteil der nativen Prozesse** (hier:
  4 von 45 python-Prozessen, waehrend `tasklist` und `Get-CimInstance
  Win32_Process` beide 45 sahen). Jede Aussage der Form "Prozesse, die in `ps`
  stehen, aber nicht in `tasklist`" ist daher ein Werkzeug-Artefakt und kein
  Befund. Immer `tasklist` oder `Get-CimInstance Win32_Process` als Quelle
  nehmen.
- **Ein Daemon mit totem Elternprozess ist KEINE Waise, sondern Absicht.** Das
  Gateway wird von einem VBS-Launcher gestartet, der sofort endet; die
  Elternkette zeigt dann "Eltern tot". Dasselbe gilt fuer die Wurzel jedes
  Prozessbaums. Vor einem Waisen-/Kill-Verdacht die Lebenszeichen pruefen:
  CPU-Zeit (`Get-Process -Id <pid>` → `TotalProcessorTime`), Kinderzahl
  (`Win32_Process -Filter "ParentProcessId=<pid>"`) und `ThreadCount`. Ein
  Prozess mit tausenden CPU-Sekunden, 26 Kindern und 200 Threads ist der
  laufende Dienst, kein Leichnam.
- **Die ZAHLEN eines Bot-Diagnoseberichts selbst nachmessen, bevor sie in
  TASKS/Notizen wandern — ein Diagnosebefund kann detailliert, plausibel und
  komplett falsch sein.** Ein Bot meldete "11 Phantom-Prozesse" plus drei
  verdaechtige PIDs; nachgemessen waren die Phantome das `ps`-Artefakt und die
  drei PIDs das Gateway selbst und zwei aktive Sitzungen. Gegenprobe-Pflicht
  fuer jede Zahl, die eine Aufraeum-/Kill-Empfehlung begruendet: Quelle
  (tasklist/CIM), Elternkette, CPU/Kinder/Threads. Erst danach dem Nutzer
  melden — und wenn der Bot falsch lag, das beim Namen nennen statt den
  Befund weiterzutragen.
- **Bei Speicherdruck-Fragen die Verteilung messen, nicht die Prozesszahl
  zaehlen.** Summe und Top-Verbraucher per `WorkingSetSize` gruppiert nach
  Dienst, dazu `FreeVirtualMemory`/`TotalVirtualMemorySize` aus
  `Win32_OperatingSystem`. Eine hohe Prozesszahl bei kleiner Summe ist kein
  Druck; der Treiber ist fast immer ein einzelner grosser Dienst oder eine
  Neustart-Schleife, die Duplikate erzeugt.

## Sonstiges
- **Eine clarify-Freigabe autorisiert KEINEN Schreibzugriff auf geschuetzte
  Agent-Anweisungsdateien (AGENTS.md/CLAUDE.md).** Sagt Max in einer
  clarify-Frage "ja, freigeben", loest der anschliessende `patch` auf die
  Datei trotzdem einen EIGENEN Freigabe-Dialog aus; laeuft der in einen
  Timeout, wird der Write BLOCKIERT ("Silence is not consent") und darf NICHT
  ueber einen anderen Weg (terminal/execute_code) wiederholt werden. Die
  clarify-Antwort ist eine Absicht, kein Vorab-OK fuer den Datei-Write. Den
  neuen Text in der TASK dokumentieren und Max bitten, den Write im
  Freigabe-Dialog zu bestaetigen, wenn er bereit ist.
- Batch offener TASKS: die entscheidungsbeduerftigen interaktiv aufbereiten
  (clarify), die machbaren parallel im Hintergrund an einen Bot delegieren."
  Max' bevorzugter Ablauf fuer einen Stapel offener Punkte: die
  Max-Entscheidungen als clarify-Fragen gruppieren (eine Frage je TASK, mit
  Empfehlung zuerst), waehrenddessen die ohne Entscheidung machbaren Teile
  (z. B. spiegelstand-Fix, Prozess-Diagnose) als `terminal(background=true,
  notify=true)` an passende Bots starten. So laeuft die Arbeit, waehrend Max
  antwortet; die Antworten werden danach abgearbeitet.
- **Offene Punkte "aller Sitzungen" konsolidieren: drei Quellen abfragen, nicht
  eine.** Max fragt gern nach einer zusammengefuehrten Liste aller offenen
  Punkte. Die drei registrierten Quellen: (1) `MaxHirn/Archiv/TASKS.md`
  (Checkbox-Zeilen `- [ ] **T-… —`; nach Epoche filtern, z. B. `T-4xx` fuer die
  aktuelle, sonst sind 90+ Eintraege unlesbar), (2) Kanban-Boards — die Karten
  liegen in `Agenten/Hermes/kanban/boards/<board>/kanban.db` (SQLite, Tabelle
  `tasks`, Spalte `status`), NICHT in der nur-Metadaten-`board.json`; je Board
  `SELECT id,title,status,priority FROM tasks WHERE status != 'done'`
  (3) die gerade offenen Faeden der eigenen Session. Erst zusammenfuehren und
  nach Bereich gruppieren, dann zur Abarbeitung in Reihenfolge anbieten statt
  die rohe Liste hinzuschreiben.
- Cron-Jobs, die ich erstellt habe (z. B. `fomo-radar Loop`), koennen mit dem
  cronjob-Tool gepauajt/weiterverwaltet werden - der fomo-radar Bot selbst kann
  das nicht (anderes Profil). `/loop` ist reiner Chat-Befehl, kein CLI-Weg.
- TASKS.md-Punkte (T-0xx): Nummer = Auftrag an den passenden Bot. Im Zweifel
  Bot-Liste pruefen (`profiles/`) statt selbst anzufangen.

## MAGDA-Gedaedchtnis (Auftrag Max 13.10.2026)
Jedes Profil fuehrt eine Markdown-Gedaedchtnisdatei, gelesen VOR jedem Lauf,
fortgeschrieben NACH jedem Lauf. Eine zentrale Datei zeigt den aktuellen Stand
aller Bots auf einen Blick.

- **Profil-Datei:** `Agenten/Hermes/profiles/<bot>/MAGDA.md` — Abschnitte:
  Letzter Stand / Offene Punkte / Erinnerungen / Ziel des naechsten Laufs.
- **Zentrale Datei:** `Agenten/Hermes/MAGDA.aktuell.md` — eine Zeile je Profil
  (letzter Stand, laeuft gerade, offener Punkt).
- **Beim Dispatch:** jedem `hermes -p <bot> chat -q "..."` dem Auftrag
  voranstellen: "Lies zuerst `Agenten/Hermes/profiles/<bot>/MAGDA.md` und
  `Agenten/Hermes/MAGDA.aktuell.md`, arbeite daraus deinen Kontext, und schreibe
  nach Abschluss deinen Stand in beide zurueck."
- **Ich selbst (Profil bots):** lese `MAGDA.aktuell.md`, bevor ich Auftraege
  verteile, und schreibe nach jeder Verteilung meinen Stand hinein.
- Pfade sind relativ zur Wurzel (`cd "$HERMES_HOME/../.."`). Die MAGDA-Dateien
  sind Betriebsdateien, nicht versioniert.
- **TASKS.md-Beschreibungen koennen veraltet sein — vor dem Delegieren den
  IST-Stand verifizieren, nicht den Text glauben.** Ein Eintrag kann einen
  Punkt als "blockiert"/"offen" beschreiben, der laengst erledigt ist (z. B.
  T-396: Vorschlag als blockiert gelistet, war aber schon angewendet, Commit
  vorhanden, Werte in der wachen.json korrekt). Erst `git log`/`git show` auf
  den vermuteten Commit und die betroffene Konfig lesen; ist der Punkt faktisch
  erledigt, das in der Rueckmeldung sagen statt einen Auftrag dafuer zu
  starten oder einen Fachbot blind auf den TASKS-Text loszulassen.
- **Eine Config-Migration kann von einer PARALLELEN Sitzung per Commit
  zurueckgesetzt werden — am ENDE den IST-Zustand der Datei pruefen, nicht
  nur die fruehere Verifikation glauben.** Ein frueherer Subagent meldete
  "0 Treffer 11434" fuer die default-config; spaeter war der
  `ollama-launch`-Provider (11434) wieder da, weil ein paralleler Commit
  ("Preserve pending Hermes...") die Datei auf einen aelteren Stand
  zurueckgesetzt hatte. Vor dem Abschluss einer Migration IMMER erneut
  `grep -n <entfernter-token> <datei>` auf den AKTUELLEN Arbeitstand laufen
  und `git log --oneline -2 -- <datei>` lesen — ein fremder Commit kann die
  Arbeit zwischen Verifikation und Abschluss ueberschrieben haben. Der
  Subagent-Bericht "keine Vorkommen" belegt nur den Stand zum Zeitpunkt
  seiner Pruefung, nicht den finalen.
- **Ein delegierter Bot kann Arbeit MELDEN, die nie passiert ist — vor dem
  Weitergeben/Verifizieren auf der Platte pruefen, nicht dem Bericht glauben.**
  Ein Bot kann einen Zweig, Commit, Testlauf und "working tree clean"
  behaupten, obwohl nichts davon existiert (Modell-Halluzination). Vor der
  Rueckmeldung an den Nutzer belegen: `git branch -a | grep <zweig>`,
  `git log --oneline -1 <zweig>`, `git diff master..<zweig> -- <pfad>`,
  `git status --short <pfad>`. Ist nichts da, den Auftrag an einen BOT
  NEU VERGEBEN, der (a) ein stabiles Modell hat UND (b) tatsaechlich
  schreiben darf — nicht automatisch an `recherche`.
- **Ein Bot-Ergebnis kann schon von einer PARALLELEN Sitzung committet sein —
  das ist kein Verlust und kein Grund, neu zu committen.** Liefert der Bot
  (wie oft) uncommittete Arbeit und "das ueberlasse ich dir", kann die
  Fremdarbeit-Routine oder eine parallele Sitzung sie in der Zwischenzeit
  eingezogen haben. Symptom: `git status` leer UND `git diff HEAD -- <pfad>`
  leer, der neue Code steht aber in der Datei. Vor dem eigenen Commit immer
  `git log --oneline -3 -- <pfad>` lesen: ein Commit mit Autor `Andere Sitzung`
  / Betreff "fremde Arbeit gesichert" ist die Antwort. Dann NICHT erneut
  committen und nicht "die Arbeit ist weg" melden, sondern den fremden Commit
  als Beleg nennen und den FUNKTIONS-Nachweis selbst fuehren (Probelauf +
  Tests) — der Commit beweist nur die Ablage, nicht die Wirkung.
- **Ein delegierter Bot kann Arbeit AUSSERHALB seines Auftrags tun und
  committen — nach dem Lauf pruefen, was er sonst angefasst hat.** Ein Bot mit
  Diagnose-Auftrag kann nebenbei eine andere offene TASK bearbeiten und dafuer
  eigene Commits setzen. Nach dem Bot-Ende `git log --oneline -5` lesen und die
  Commits benennen, die nicht zum Auftrag gehoeren: sie sind oft nuetzlich,
  aber unerwartet, und erklaeren, warum der Bot laenger lief. Ungefragte
  Betriebskonfig-Aenderungen daraus dem Nutzer melden, nicht stillschweigend
  uebernehmen.
- **Laufen ZWEI Bots parallel und schreiben beide in dieselbe Registerdatei
  (`TASKS.md`), vor jedem eigenen Patch neu einlesen.** Das Patch-Tool warnt
  dann ("modified by sibling subagent but this agent never read it") — die
  Warnung ernst nehmen: die Datei frisch lesen, patchen, und danach
  verifizieren, dass die Bloecke des anderen Bots noch da sind
  (`grep -c "T-<nummer>"` auf dessen TASK). Zwei Bots auf dieselbe Datei
  anzusetzen ist vermeidbar: beim Parallel-Dispatch jedem Bot eine eigene
  Datei/einen eigenen TASK-Block zuweisen.
- **Der stabile Bot kann der False mit LESEN sein.** `recherche`
  (deepseek-v4-flash, stabil) verweigert schreibende Arbeit aus eigenen
  Regeln ("als Recherche-Agent committest du nichts") und der
  Bereichs-Besitz-Regel (`Agenten/Handel/` gehoert laut `BEREICHE.json` dem
  `handel`-Besitzer). Ein stabiler Lese-Bot ist fuer Analyse gut, fuer einen
  Bau/Commit aber der falsche Adressat — der erste Versuch endet dann mit
  einer legitim begruendeten Weigerung, nicht mit Arbeit. Vor einem
  Bau-Auftrag pruefen, ob das Zielprofil Schreiberlaubnis hat.
- **Fehlt fuer einen Bereich ein Bau-Bot mit stabilem Modell, EINEN der
  vorhandenen Profile umpolen statt raten.** Die handelsnahen Fork-Profile
  (jev-trader, agent-trade-kit, awesome-systematic-trading, harvard-trading)
  defaulten auf longcat (kollabiert bei Bau); `recherche` ist stabil aber
  lesen. Wenn Max freigibt, `model.default` eines handelsnahen Profils auf
  `deepseek/deepseek-v4-flash-0731` setzen, `terminal.cwd` auf
  `C:\Users\faupe\Documents\BrainFiles` (damit es in `Agenten/Handel`
  arbeitet), config committen (profiles/ gehoert dem bot-Bereich), danach
  den Bau delegieren. Das ist Config-Arbeit im eigenen bot-Bereich, kein
  Fremdeingriff.
- **Nach dem Bot-Bericht den IST-Wert aus der frischen Quelle melden, nicht aus der naheliegenden Datei.** Bei parallelen Stufen-Buechern (`zustand.json` Basis vs. `zustand.mittel/hoch.json`) kann die Basis-Datei stale sein; melde offene Positionen/Status nur aus der Datei mit dem juengsten `letzter_lauf`. Eine verstaendliche, aber falsche Masse ("3 offene Live-Positionen") aus einer toten Datei ist schlimmer als ein ehrliches "welche Stufe?" — der Nutzer korrigiert die Zahl, und das Vertrauen in jede weitere Zahl sinkt.
- **PR-Body mit Backticks/Code nicht in eine doppelt-gequotete Shell-Commandline packen.** In `gh pr create --body "...`<code>`..."` wertet die Shell die Backticks als Command-Substitution aus und frisst die Stellen aus dem Body. Als Here-Doc mit einfachen Quotes (`--body-file - <<'EOF'`) uebergeben und danach den Body per `gh pr view <n> --json body --jq .body` zuruecklesen und auf die Code-Stellen pruefen, statt nach dem Erstellen zu vertrauen.
- **"Tests gruen" erst in den PR-Body schreiben, NACHDEM man sie selbst gelaufen hat — nie aus einem Handoff/Erinnerungsstand uebernehmen.** Ein Handoff kann "fertig, verifiziert" behaupten, aber die Tests schlagen im Worktree fehl (falsches Arbeitsverzeichnis, Pfad-Guard, nicht umgestellte Alt-Venue-Tests). Vor dem `gh pr create` die Tests des Branches mit dem Hauptbaum-Interpreter SELBST ausfuehren und das Ergebnis (OK/FAILED + Anzahl) abwarten; erst dann "Tests gruen" in den Body schreiben. Ein PR-Body, der gruene Tests behauptet, die rot sind, ist eine falsche Zusicherung an den Reviewer.
- **Einen delegierten Bot-Bericht immer gegen die Platte verifizieren — nie den
  Wortlaut ("erledigt", "committet", "verifiziert") allein glauben.** Die
  Gegenpruefung ist billig und zwingend: `git log --oneline -3 -- <pfad>` (Commit
  wirklich da?), `git show <hash> --stat` (Inhalt im diff?), `git grep`/`grep -n`
  auf den erwarteten Beleg (z. B. `def lade_wachen`), `git status --short`. Erst
  wenn diese Checks den Bericht stuetzen, an den Nutzer melden. Ein Commit mit
  fremdem Autor (nicht der delegierte Bot) heisst oft: gelogen ODER eine parallele
  Sitzung hat gearbeitet — beides vor der Meldung klaeren. (Gegenprobe-Pflicht
  gilt auch fuer Diagnose-ZAHLEN, siehe Abschnitt Prozessdiagnose; verwaistes
  Git-Lock siehe "Neuen Repo-Bot anlegen".)
  - **Standard-Regel: bei jeder Bot-Delegation eines Projekts eine Markdown-Datei zum Stand auf der Platte hinterlassen und pflegen.** Max erwartet es als Massstab: ein delegiertes Codeprojekt ist nur sauber uebergeben, wenn eine Markdown-Spec/Stand-Datei (unter `Werkstatt/Projekte/<datum>-<thema>.md`) existiert und den Fortschritt je Schritt dokumentiert — Ziel, gemessener Kontext, Schritte, Commit-Hash je fertigem Schritt, offene Blocker. Diese Datei ist zugleich der Platten-Beweis und der Anker fuer Folge-Bot-Schritte (siehe "Lagebild als Spec-Datei"). Die Spec konsolidieren/aktualisieren, sobald ein Schritt abgeschlossen ist, und ab und zu ueberfluessige/veraltete Abschnitte aufraeumen statt sie staendigig zu verlaengern.
- **Handel-Spuren-Tests laufen NUR aus dem Spur-Ordner, nie als `-m unittest tests.test_x`.** Der Pfad-Guard `assert h.__file__.startswith(SPUR)` in den Testdateien schlaegt bei `-m unittest tests.test_x` fehl, weil `scanner/handeln.py` den Import gewinnt (der Test fuegt scanner vor SPUR in den Pfad ein). Korrekt: `cd Agenten/Handel/<spur> && <hauptbaum-python> -m unittest discover -s tests -p "test_*.py"` (oder die Testdatei direkt als Skript `python tests/test_x.py`). Ein `-m unittest`-Fehler "falsches handeln.py: ...scanner\handeln.py" ist also ein Aufruf-Problem, kein Code-Fehler — und tritt auf master genauso auf wie auf dem Branch.
- **Merge-fertige Worktree-Branches pushen + PR eroeffnen ist ein eigener Schritt, der die Tests voraussetzt.** `git push -u origin <branch>` aus dem jeweiligen Worktree, dann `gh pr create --base master --head <branch>`. Vor dem Push pruefen, dass der Branch nicht schon auf dem Remote liegt (`git ls-remote --heads origin <branch>` leer) und dass er wirklich Commits vor master hat (`git rev-list --count master..<branch>` > 0) — sonst eroeffnet man eine leere PR.
- **Mehrzeilige Code-Bloecke mit dem `patch`-Tool umschreiben ist unzuverlaessig — bei Einrueckungs-/Tippfehler-Korruption auf ein Python-Heredoc wechseln.** Das fuzzy `patch`-Tool verschiebt bei mehrzeiligen Ersetzungen gern die Einrueckung und verdoppelt/verstuemmelt Zeilen (`if w    if w is None:`, `wurzel_vwurzel_von`). Sobald ein Patch-Block zweimal kaputt zurueckkommt, nicht weiter mit dem Tool fummeln, sondern die exakte Zeilenspanne per `python - <<'EOF'` neu schreiben: Datei lesen, Start-/Endzeile der Methode per `startswith("    def ")` finden, den Block durch die sauberen Zeilen ersetzen, zurueckschreiben, `py_compile` zur Syntaxpruefung. Das ist deterministisch und laesst die Einrueckung intakt.
- **Python-Literal-Ersetzung auf einer CRLF-Datei muss CRLF erhalten, sonst wird der git-Diff riesig (jede Zeile insert+delete).** Eine config.yaml mit CRLF-Zeilenenden, per `open(p,'w').write(s)` mit LF geschrieben, erzeugt einen 1396/1396-Diff statt der zwei echten Aenderungen. Vor dem Write pruefen (`data.count(b'\r\n')`), und beim Schreiben `open(p,'w',newline='')` verwenden oder nach dem Write LF→CRLF zurueckkonvertieren (`data.replace(b'\n', b'\r\n')`). Danach `git diff HEAD -- <datei>` auf den echten Aenderungsumfang pruefen, nicht nur `git add`+`commit` — ein riesiger Diff ist das Symptom einer Zeilenenden-Konvertierung, kein echter Umbau.
- **Worktree-Commit, der mit "keine .git-Wurzel gefunden" abbricht, aber `git rev-parse --show-toplevel`/`status` gruen sind, haengt am pre-commit-Hook:** der `.githooks/pre-commit` ruft das Bereichs-Skript (`bereiche.py --staged`) und kann im Worktree-Kontext scheitern. Worktree-Commits mit `git -c core.hooksPath=/dev/null commit -m ...` durchfuehren (einmalig, area-Hook wirkt nur mit gesetzter `BRAINFILES_BEREICH`).
- **Vor jedem PR-Follow-up den Remote-Zustand frisch lesen.** Eine parallel
  gemergte PR bleibt lokal als Worktree/Branch sichtbar; ein späterer Commit
  auf dem alten Kopf gehört nicht zum gemergten PR und kann eine große,
  fremde Diff-Fläche erzeugen. `gh pr view <N> --json
  state,mergedAt,headRefName,baseRefName,mergeCommit` und `git fetch origin`
  prüfen. Wenn bereits gemergt: frischen Worktree von `origin/HEAD` anlegen,
  nur den Folgecommit portieren, den Diff-Namensumfang prüfen und eine neue PR
  eröffnen; nie den veralteten Branch weiter pushen.
- **Nach dem Bot-Bericht den ZIEL-ZWEIG pruefen, nicht nur die
  Dateien.** Ein Bot committet auf dem Zweig, den der geteilte Arbeitsbaum
  gerade haelt — das kann der fremde aktive Zweig einer anderen Sitzung sein
  (z. B. `claude/...`), nicht `master`. Betriebskonfig-Aenderungen
  (`wachen.json`-Werte, `dauerlauf.py` SPUREN/AUTO_FREIGABE) gehoeren auf
  `master`. Nach dem Bot-Bericht `git log --oneline -1 <commit>` UND
  `git branch --show-current` pruefen; liegt der Commit auf einem fremden
  Zweig, sag es dem Nutzer und biete an, ihn auf `master` zu bringen.
  - *Auf master bringen ohne `git switch` im geteilten Hauptbaum:* temporaeren
    Worktree auf dem Zielzweig (`master`) anlegen
    (`git worktree add .worktrees/<thema> -b <agent>/<thema> master`), dort
    `git cherry-pick <commit>`, das Ergebnis pruefen, dann per PR einbringen:
    `git push origin <agent>/<thema>`, `gh pr create --base master --head
    <agent>/<thema>`, und erst NACH dem Merge aufraeumen
    (`gh pr merge <n> --merge --delete-branch`, `git worktree remove
    .worktrees/<thema> --force`, `git worktree prune`). Kein direkter
    Fast-forward-Merge auf `master` — die Repo-Regel ist "gemergt per PR".
  - Vor dem Cherry-pick pruefen, dass das Legacy-Commit nur die eine
    Konfig/Datei anfasst und deren Kontextanchor auf dem Zielzweig identisch
    ist (`git show --stat <commit>`, `git show <zielzweig>:<pfad> | grep
    <anchor>`); das macht den Port konfliktfrei, statt blind zu portieren.
  - Nach dem Port den Inhalt validieren, BEVOR gepusht wird — bei YAML z. B.
    `python -c "import yaml; yaml.safe_load(open('...',encoding='utf-8'))"`
    und die Werte (Routen/Profile) ausgeben, nicht nur die Dateigroesse.    
  - Der urspruengliche Commit bleibt auf dem fremden Zweig liegen; kommt der
    spaeter nach `master`, gibt es einen Konflikt (identischer Inhalt) — den
    Hinweis in der Rueckmeldung nicht verschweigen. Der fremde Zweig ist der
    gerade aktive des geteilten Arbeitsbaums und traegt oft noch uncommittete
    Arbeit der parallelen Sitzung: dort kein `git switch`/Rebase/Reset
    ausfuehren, nur der temporaere Worktree wird beruehrt.
