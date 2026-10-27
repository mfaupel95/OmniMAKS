# Zentrale Handelsübersicht und autonome Optimierung

**Status:** Entwurf zur Freigabe durch Max
**Stand:** 2026-10-25
**Zielsystem:** BrainFiles / Agenten/Handel; Experimente ausschließlich in isolierten Branches oder Worktrees

## Absicht

Eine verlässliche Oberfläche soll sämtliche Einträge im Downloads-Ordner sowie alle aktuellen oder kürzlich bearbeiteten Projekt-/Repository-/Worktree-Arbeiten in BrainFiles auffindbar machen. Zusätzlich verknüpft sie Handelsagenten, Handelsspuren, Freqtrade-Bots und laufende oder planbare Routinen an einer Stelle. Auf derselben Grundlage soll ein LLM alle Handelsspuren regelmäßig analysieren und Verbesserungen autonom entwickeln. Gute Kandidaten dürfen nach messbaren Prüfungen automatisch in getrennte Papierläufe einfließen. Max möchte über abgeschlossene Läufe, Änderungen und Blockaden informiert werden, nicht jeden Versuch einzeln genehmigen.

Das Ziel ist bessere, robustere Nettoleistung und eine flexiblere technische Basis. Profit ist nicht garantierbar; ein System darf aus fehlenden oder nicht belastbaren Daten keinen Erfolgsnachweis ableiten.

## Beobachteter Ausgangsstand

Diese Zahlen sind ein einmaliger Lesestand und müssen beim Bau erneut erhoben werden:

- `Agenten/Handel/dauerlauf.py` enthält 47 oberste Einträge in `SPUREN`. Das ist die Liste registrierter Spuren, kein Beleg dafür, dass alle aktuell handeln.
- Docker meldete 20 laufende Freqtrade-Container. `freqtrade/bots.json` listet 20 Bots. Nur drei Dateien in `user_data/bots/` enthielten beim Lesen explizit `dry_run: true`; der Betriebsmodus der übrigen Container ist damit nicht bestätigt und muss vor jeder Freigabe pro Bot verifiziert werden.
- Die bestehende `Handelszentrale` ist bereits eine reine Leseoberfläche über Dauerlauf-Spuren, Freqtrade und OmniTrade. Ihre Beschreibung nennt 42 Spuren (Stand 01.10.2026), während die heutige `SPUREN`-Definition 47 Einträge hat. Sie ist der natürliche Ausbaupunkt.
- `freqtrade/urteile.json` enthält 17 Strategieurteile, zuletzt datiert auf 13.10.2026. Der separate `bt_opt`-Ordner enthält eine 4h-Gegenprobe.
- Der Verbesserer ist laut Aufgabenplanung deaktiviert. Seine Konfiguration kennt mindestens Scanner/OKX, Kraken/EUR und XPERP/OKX; sein dokumentierter letzter Ergebnisdatensatz meldet zu wenig OOS-Runden für einen Kandidaten. Die wöchentliche Routine „Optimierungen finden“ prüft Routinen und abgebrochene Läufe; sie ist kein Strategieoptimierer.
- In Downloads wurden 23 Dateien auf oberster Ebene und 11 Archive gezählt. Der Scan hat Namen, Zeitstempel und Größen verwendet, keine Inhalte von Zugangsdaten- oder Sitzungsdateien geöffnet. `freqtrade-stable.zip` und `handel.tar.gz` sind erkennbare Handelsbezüge; eine vollständige Zuordnung der übrigen relevanten Downloads zu bestehenden Projekten steht aus.
- Der gemeinsam genutzte BrainFiles-Arbeitsbaum enthält mindestens 35 uncommittete Pfadänderungen. Diese werden nicht in Experimente übernommen oder verändert.

Eine vorhandene Gesamtauswertung vom 24.10.2026 trennt Journalmodi und nennt offene Datenqualitäts- und Börsenabgleichsfragen. Sie ist eine Quelle für die Übersicht, aber kein Live-Fill-Nachweis.

## Nutzererlebnis

Die bestehende Handelszentrale erhält einen Inventar-/Entwicklungsbereich mit drei getrennten Ansichten:

1. **Betrieb:** jede registrierte Spur und jeder Bot mit Projektpfad, Laufzeitstatus, geplantem Status, Modus (live / Papier / unbekannt / inaktiv), letzter Aktualisierung, zugehörigem Journal und Quelle des Status. „Registriert“, „startbar“, „geplant“ und „läuft“ bleiben unterscheidbare Zustände. Nur lesende Bedienung.
2. **Projekt- und Downloadkarte:** alle Downloads sowie aktuelle und kürzlich bearbeitete Projekt-/Repository-/Worktree-Arbeiten in BrainFiles mit Originalpfad, erkennbarem Projektziel, Änderungszeit, Repository/Worktree/Branch und Zuordnungsstatus. Es wird verlinkt, nichts verschoben oder dupliziert. Nicht zuordenbare Einträge erscheinen in einer Prüfliste. Sensible Konfigurationen und Sitzungsarchive werden nur als Pfad/Metadaten geführt; Inhalte und Geheimnisse werden nicht gelesen.
3. **Experimente und Entscheidungen:** Vorschläge, Hypothese, betroffene Spur, isolierter Branch/Worktree, Basisrevision, Änderungen, Messfenster, Kostenmodell, Validierung, Ergebnis, Promotion/Rollback und Commit-ID. Abgelehnte Kandidaten bleiben mit Begründung nachvollziehbar.

Die Oberfläche zeigt Aktualität und Datenqualität, statt fehlende Informationen still als Null oder Erfolg darzustellen. Sie zeigt keine Handlungsschaltfläche für Börsenorders und schreibt nie in Journale, Wachen oder Zustandsdateien.

## Zwei getrennte Entwicklungswege

### Verbesserer

Findet technische und betriebliche Schwächen: Fehlerquellen, fehlende Tests, unklare Schnittstellen, Daten-/Journalprobleme, Wiederverwendbarkeit, flexible Strategiekonfiguration und unnötige Wartung. Er darf Strategiecode ändern, wenn eine konkrete Hypothese und messbare Wirkung benannt werden. Eine reine Code- oder Architekturverbesserung gilt nicht automatisch als Handelsverbesserung.

### Strategieoptimierer

Analysiert geschlossene und korrekt gepaarte Runden, Signale, Long/Short, Ausstiegsgründe, Marktregime, Kosten und Rückgang. Er untersucht Regeln und Parameter mit Walk-Forward- und Holdout-Prüfung, vergleicht sie mit der unveränderten Basis und lässt schlechte oder datenarme Kandidaten fallen. Die Suche darf keine Zukunftsdaten oder unvollständigen Börsenfills als Profitbeleg verwenden.

Beide Wege erhalten getrennte Läufe, Metriken und Berichte. Bei einem Kandidaten dürfen sie zusammenarbeiten, aber die Herkunft jeder Codeänderung und jeder Wirkungsmessung muss sichtbar bleiben.

## Autonomie, Isolation und Promotion

- Das LLM entscheidet selbst, welche Spur und Hypothese als Nächstes sinnvoll ist, und arbeitet auf einem neuen oder wiederverwendbaren isolierten Branch/Worktree. Es verändert weder den gemeinsam genutzten Arbeitsbaum noch eine Live-Datei.
- Das LLM darf dort Quellcode, Konfigurationen für ausschließlich isolierte Papierläufe und Dokumentation anpassen, vorhandene Prüfungen/Backtests ausführen und Kandidaten verwerfen. Neue Softwareinstallation oder Änderungen an Host-Konfigurationen sind nicht Teil der Routine.
- Ein Kandidat wird nur automatisch in einen dedizierten Papierlauf übernommen, wenn Daten vollständig und korrekt zugeordnet sind, Kosten einschließlich Gebühren/Funding modelliert sind, Tests und zeitlich getrennte Walk-Forward-/Holdout-Fenster bestanden werden, ein vorab festgelegter Mindestumfang an geschlossenen Papier-Runden vorliegt und die Nettoleistung die Basis robust übertrifft, ohne den festgelegten Drawdown-Deckel zu verletzen. Schwellen werden vor der ersten Promotion je Strategiefamilie dokumentiert und nicht nach Sichtung des Ergebnisses angepasst.
- Bei fehlenden Daten, widersprüchlichen Modi, nicht reproduzierbaren Resultaten oder Grenzwertverletzungen bleibt der Kandidat isoliert. Der Papierlauf kann auf die vorherige nachgewiesene Revision zurückgesetzt werden.
- Live-Einstiegssperren, Live-Wachen, Hebel, Kapitaldeckel und reale Konten werden durch diesen Prozess nicht geändert. Es werden keine echten Orders oder sonstigen Geldbewegungen ausgelöst. Übergang zu Live bleibt ausschließlich Max' Entscheidung und manueller Vorgang.

## Takt und Mitteilung

Gesamtprüfung und Optimierungszyklus laufen alle 14 Tage. Vorgeschlagener Standardzeitpunkt: jeder zweite Montag um 09:45 Uhr Europe/Berlin, in Anlehnung an den bestehenden Montagstakt. Die genaue technische Ausführung (lokale Windows-Aufgabe oder Codex-Heartbeat) wird im Bau anhand Verfügbarkeit, Schlaf-/Offline-Zustand des Rechners und bestehender Routinen gewählt; es wird kein zweiter, konkurrierender Optimierungslauf eingerichtet.

Nach jedem Lauf erhält Max eine kurze Mitteilung in diesem Codex-Thread und einen lokalen Markdown-Bericht: geprüfte Spuren, Datenlücken, gefundene Muster, Experimente/Commit-IDs, Promotionen oder verworfene Kandidaten mit Messwerten und nächster Lauf. Bei einem fehlgeschlagenen oder sicherheitsrelevanten Lauf wird sofort informiert. Es werden keine externen Nachrichten versendet.

## Grenzen und Nicht-Ziele

- Keine Profitgarantie, kein Verlustausgleich durch mehr Risiko und keine automatische Richtungsumkehr Long zu Short ohne nachgewiesene eigenständige Short-Strategie.
- Keine Orders, Guthabenbewegungen, Live-Freigabe oder Veränderung von Echtgeld-Risikogrenzen.
- Keine Änderungen oder Bereinigungen an Downloads, persönlichen Dateien, Geheimnissen, uncommitteter Arbeit anderer Sitzungen oder nicht zugeordneten Projekten.
- Keine automatische Promotion, wenn Papiermodus, Journalqualität, Reproduzierbarkeit oder notwendige Marktdaten nicht zweifelsfrei bestätigt sind.
- Erstes Ergebnis ist eine lesende, nachvollziehbare Bestands- und Zuordnungskarte. Autonome Codeänderungen und Paper-Promotionen starten erst nach erfolgreicher Abnahme der jeweiligen Gates.

## Entscheidungen aus der Entwurfsprüfung

- **Umfang:** vollständige Downloads-Liste und aktuelle/kürzlich bearbeitete Projekte/Worktrees unter BrainFiles; kein pauschaler Scan persönlicher Archivdaten außerhalb dieser Projektbereiche.
- **Mitteilung:** Ergebnis jeweils in diesem Codex-Thread plus lokalem Markdown-Bericht; keine externen Kanäle.

## Offene Umsetzungspunkte für den Builder

- Die tatsächliche Zuordnung der 20 Freqtrade-Container zu ihren effektiven `dry_run`-Einstellungen sicher und ohne Ausgabe von Zugangsdaten feststellen; unbestätigte Bots als „Modus unbekannt“ behandeln.
- Die Handelszentrale so erweitern, dass ihre Spurenzahl aus der Laufzeitquelle stammt und keine zweite manuelle Liste entsteht.
- Den ersten Paper-Slot so isolieren, dass Experimente keine gemeinsam genutzten Journale, Zustände oder Q:-Spiegel überschreiben.
- Die Erfolgs-/Abbruchschwellen je Spur aus den vorhandenen Hausregeln ableiten und vor der ersten automatischen Promotion festschreiben; bei nicht ausreichend belegbarer Spur nur Inventar und Diagnose, keine Promotion.
- Download-/Projektzuordnung lesend für den vollständigen Downloads-Ordner und aktuelle/kürzlich bearbeitete Projekt-/Worktree-Arbeiten in BrainFiles aufbauen; unklare Zuordnungen sichtbar lassen.
- Bestehende Zweiwochen-Routinen und Zeitplanungen inventarisieren, bevor ein Trigger angelegt wird; genau einen ausführenden Takt behalten.
