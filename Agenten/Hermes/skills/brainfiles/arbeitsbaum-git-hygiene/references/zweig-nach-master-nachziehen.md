# Eigenen Commit vom Zweig einer Parallelsitzung nach master nachziehen

Wenn die eigene Arbeit auf dem ZWEIG einer parallelen Sitzung gelandet ist
(HEAD stand dort, `git switch` wurde nie gemacht) oder Max sagt „nachziehen,
Parallelsitzung mitnehmen": der Zweig haengt oft an einem aelteren Stand als
`origin/master` (andere Sessions haben per PR gemergt), `--ff-only` ist dann
keine Option.

## Ablauf

1. **Lage messen** (lesend, ein Aufruf):
   `git fetch`, `git log --oneline master..<zweig>`,
   `git rev-list --left-right --count master...origin/master`,
   `git cherry origin/master <zweig>` — nur `+`-Zeilen fehlen in
   origin/master. **Ein `+` fuer den eigenen Commit heisst NICHT „Inhalt
   fehlt":** der Commit wurde beim Nachzug unter anderer SHA gemergt
   (Konfliktloesung). Identitaet per Inhalt pruefen:
   `git diff <eigener-sha> <gemergte-sha> --numstat` — leer oder klein =
   derselbe Inhalt, nichts nachzutragen.

2. **Ruhende Fremdarbeit ZUERST sichern** (bevor etwas bewegt wird). Die
   30-min-Regel aus `fremdarbeit-uebernehmen`; Leerlauf der Prozesse messen
   (CPU-Delta zweimal, ~0 = tot), NICHT nur das Dateialter — ein Ordner mit
   Minuten-mtime kann ein laufender Dienst sein (Cron-`ticker_heartbeat`,
   `eingelegt.hoch.json` vom Dauerlauf). Dauerlauf-Schreibzugriffe
   (`eingelegt.hoch.json`, Minuten alt) sind KEIN Ruhezustand und bleiben
   liegen; vor dem Reset aus `cache/scratch/` zuruecksichern.

3. **Worktree von `origin/master`, eigener Commit zuerst:**
   `git worktree add .worktrees/<name> -b <zug> origin/master`, darin
   `git cherry-pick <eigener-sha>`.

4. **Konflikt in einer Datei, die master inzwischen NEU hat: KEINE Seite
   verwerfen — VERKETTEN.** Die HEAD-Fassung (fremde Aenderung) behalten und
   den eigenen Block als ZUSAETZLICHEN Schritt danach einfuegen; beide Filter
   wirken dann zusammen. Die Aufloesung und der Grund gehoeren in die
   Commit-Meldung.

5. **Rest des Zweigs der Reihe nach:** `git cherry-pick` in umgekehrter
   chronologischer Reihenfolge (`git log --reverse --format=%h
   origin/master..<zweig> | grep -v <eigener-sha>`), beim ersten Konflikt
   (`git diff --name-only --diff-filter=U`) stoppen und aufloesen.

6. **Ein Commit, der eine Datei LOESCHT, auf Referenzen pruefen.** Ein
   Housekeeping-Commit (z. B. kb-sync) kann eine Datei entfernen, auf die ein
   Task noch zeigt („Betrifft: <pfad>"). Aus dem ANLAGE-Commit zurueckholen
   (`git show <add-sha>:<pfad> > <pfad>`) und als eigenen Commit hinterher —
   sonst zeigt der Task ins Leere. Dateien unter `Werkstatt/Projekte` brauchen
   `git add -f` (die `*`-Sperre der .gitignore trifft sie).

7. **Push:** `git push origin <zug>:master`. Vorher `GITHUB_TOKEN`/`GH_TOKEN`
   leeren (`export GITHUB_TOKEN= GH_TOKEN=`) — der Registry-Token hat keinen
   Schreibzugriff und der Push endet sonst als 403, waehrend derselbe Push von
   Hand geht.

8. **Aufraeumen in DIESER Reihenfolge:** `git worktree remove
   .worktrees/<name> --force` → `git branch -D <zug>` →
   `git push origin --delete <fremder-zweig>` → `git worktree prune`.
   `git branch -D <paralleler-zweig>` kann mit „used by worktree at ...
   pr79" scheitern: erst DORT den Stand pruefen (`git diff origin/master
   HEAD --stat` leer = inhaltlich identisch), dann dieses Worktree entfernen,
   dann den Zweig loeschen.

9. **Mischzustand nach dem Zweig-Wechsel erkennen und heilen.** Schreibt die
   parallele Sitzung waehrend des Wechsels in den GETEILTEN Index, bewegt
   `git switch master` den Kopf, aber der Arbeitsbaum traegt weiter den
   Inhalt des anderen Zweigs: 40+ `M`-Zeilen und fremde `??`-Ordner stehen
   da, obwohl HEAD stimmt. **Erst den Beweis fuehren, dann hart
   zuruecksetzen:** `git cherry origin/master <zweig>` (nur der eigene,
   gemergte Commit darf `+` sein) UND je `??`-Datei
   `git cat-file -e origin/master:<pfad>` — steht alles in origin/master,
   `git checkout -- .` und `git reset --hard origin/master`. OHNE diesen
   Beweis ist reset verboten (Regel „nichts fremdes zuruecksetzen" aus dem
   SKILL.md gilt).

10. **Die Suite NACH dem Reset im Hauptbaum fahren**, nicht im Worktree: nur
    dort laeuft sie gegen den Zustand, den master wirklich hat.

## Nachweis vor dem Abschluss

- `git log -1 --format=%h %s` = der eigene Commit oben auf origin/master
- `git status --porcelain` leer (bis auf Dauerlauf-Schreibzugriffe)
- betroffene Suite im Hauptbaum: `Ran N tests ... OK`
- `git branch -a | grep -E '<zug|fremd>'` leer, `git worktree list` nur
  noch erwartete Eintraege

## Merksatz

**Nachziehen ist Beweisfuehrung in der Reihenfolge: sichern → Worktree →
verkettet mergen → pushen → aufraeumen.** Ein `reset --hard` ohne den
cherry-Beweis verwirft fremde Arbeit; ein `--ff-only` auf einen Zweig, der
hinter origin/master liegt, tut nichts und sieht erledigt aus.

## Lokale Synchronisierung und sichere Worktree-Bereinigung

Wenn der Nutzer einen lokalen Nachzug und die Bereinigung verbleibender Arbeitsbaeume freigibt:

1. **Zielzweig und Zustand zuerst feststellen.** Den Defaultzweig aus `git symbolic-ref --short refs/remotes/origin/HEAD` lesen; bei fehlendem Symbol den im Auftrag genannten Integrationszweig verwenden. `git status --short --branch`, `git diff --cached --name-only`, `git worktree list --porcelain`, Branches und aktive Git-Prozesse erfassen. Einen Index-Lock nur bei belegter Stale-Lage (kein Git-Prozess, Alter/Größe dokumentiert) reversibel umbenennen, nie blind löschen.
2. **Remote aktualisieren und Commit-Integration trocken prüfen.** Den Remote-Stand holen und `git merge-tree --write-tree HEAD origin/<zielzweig>` verwenden. Das prüft Commit-Bäume, erkennt aber keine Konflikte zwischen Remote-Commits und uncommitteten Dateien im Arbeitsbaum. Diese Überlappungen separat aus `git diff --name-only HEAD..origin/<zielzweig>` gegen `git status --porcelain` ermitteln.
3. **Nur konkrete Überlappungen sichern.** Vor dem Merge exakte Originaldateien und einen Patch in einen datierten Bereich unter `.git/` kopieren; Hashes oder bytegenaue Vergleiche zur Sicherungskontrolle verwenden. Kein `git stash`. Remote-Deduplizierung und neue Metadaten übernehmen, aber nur den semantisch notwendigen lokalen Zusatz wieder einarbeiten. Sicherheitswerte wie ein lokales Handelsverbot nicht durch eine alte Komplettdatei überschreiben. JSON/YAML nach der Auflösung strukturell parsen und auf doppelte Einträge/Schlüssel prüfen; `git diff --check` ausführen.
4. **Lokal integrieren, nicht ungefragt veröffentlichen.** Den freigegebenen Zielzweig mit dem Remote zusammenführen. Kein Push ohne ausdrücklichen Auftrag. Anschließend `git merge-base --is-ancestor origin/<zielzweig> HEAD` sowie Ahead/Behind prüfen; lokale, uncommittete Arbeit muss weiterhin unverändert sichtbar sein.
5. **Jeden Worktree einzeln klassifizieren.** Status, Branch-Divergenz und Commit-Erreichbarkeit prüfen. Vorhandene Änderungen oder einzigartige Commits behalten. Patch-Äquivalenz (`git cherry <zielzweig> <branch>`) darf als Integrationsnachweis dienen, wenn Commit-SHAs durch Cherry-Pick abweichen. Ignorierte, nicht regenerierbare Zustände vor Entfernen sichern; `__pycache__` und andere klar regenerierbare Caches nicht unnötig kopieren. Gepinnte/verwaltete App-Worktrees nicht gegen App-Schutz entfernen.
6. **Nur belegbar saubere und integrierte Worktrees entfernen.** `git worktree remove <pfad>` ohne `--force`; Branch erst löschen, wenn seine Inhalte erreichbar oder nachweislich patch-identisch integriert sind. Bei Windows `Permission denied` Registrierung, Pfad und Prozesse prüfen. Wenn die sichere normale Entfernung scheitert, liegen lassen und melden; nicht mit rekursivem Löschen, `--force` oder robocopy umgehen.
7. **Abschlussnachweis knapp erheben.** Merge-Base, Status, Worktree-Liste, verbliebene Branches und Sicherungspfade erneut prüfen. Verbliebene Dirty-/unmergierte Arbeitsbäume, gepinnte Einträge, unregistrierte Reste und fehlende Pushes ausdrücklich nennen. Tests nur ausführen, wenn sie zum Auftrag gehören oder für den Merge-Nachweis verlangt wurden.
