---
name: local-tool-integration
description: "Use when importing a repository as a local Hermes tool."
version: 1.0.0
author: Hermes Agent
license: proprietary
metadata:
  hermes:
    tags: [repository, tools, hermes, profiles, integration]
    related_skills: [hermes-agent, github]
---

# Lokale Werkzeuge integrieren

## When to Use

Nutze diesen Ablauf, wenn ein externer Repository-Klon als lokales Werkzeug in `Werkstatt/` bereitstehen und über Katalog oder Hermes-Profil erreichbar werden soll. Besonders relevant bei Werkzeugen mit potenziellen externen Seiteneffekten.

## Ablauf

1. Lies die geltenden Projekt- und Schutzregeln, bevor du einen Klon anlegst oder einen Katalog bzw. ein Profil änderst.
2. Prüfe den Zielordner und klone den Upstream nur dann nach `Werkstatt/<name>`, wenn dort noch kein Verzeichnis existiert. Bewahre den Upstream als `origin`; überschreibe keinen vorhandenen Klon.
3. Lies README, AGENTS/CLAUDE und die ausführbaren Einstiegspunkte. Ermittle, ob das Werkzeug nur auswertet oder externe Zustandsänderungen auslösen kann.
4. Führe die vorhandenen, projektspezifischen Tests aus und prüfe danach den Klonstatus. Bereinige ausschließlich testgenerierte Artefakte wie `__pycache__`, sodass der neue Klon sauber bleibt.
5. Registriere das Werkzeug im zentralen lokalen Werkzeugkatalog mit Ordner, Rolle, Laufzeit, zugehörigem Bot und einer knappen, zutreffenden Sicherheitsnotiz. Validiere die JSON-Datei und lade den Eintrag über die vorhandene Katalog-CLI mit deren Projekt-venv, nicht mit einem zufälligen System-Python.
6. Erzeuge ein eigenes Hermes-Profil über die Hermes-CLI. Weise es der passenden UI-Sektion zu und beschreibe klar Zweck, Arbeitsverzeichnis und Ausführungsgrenzen.
7. Erzwinge fachliche Sicherheitsgrenzen im Profil-SOUL: bei Analyse- und Papierwerkzeugen keine Broker-/Order-Tools aufrufen, keine Credentials anfordern oder speichern und Vorschläge klar von Ausführung trennen.
8. Prüfe am Ende: Remote und Commit des Klons, sauberer Klonstatus, vollständige Tests, Katalogeintrag und Profil-Metadaten/SOUL.

## Sicherheits- und Qualitätsregeln

- Behandle einen importierten Drittklon als Werkzeug, nicht als Teil des eigenen Produktionspfads; ändere ihn nicht, um die Integration zu erzwingen.
- Prüfe bei Handels-, Zahlungs- oder Infrastrukturwerkzeugen gezielt auf Ausführungs- und Credentialpfade, bevor du sie sichtbar machst; eine Dokumentation, die eine Order vorbereitet, ist nicht automatisch eine sichere Ausführungsgrenze.
- Nutze für normale Profilkonfiguration ausschließlich `hermes --profile <name> config set`; `config.yaml` nie händisch ändern, weil ein fehlerhafter YAML-Eingriff den laufenden Gateway beschädigen kann. Lies jeden gesetzten Wert mit `hermes --profile <name> config get <key>` zurück.
- Hängt ein profilbezogener Konfigurationsaufruf beim Start, wiederhole denselben offiziellen Befehl mit `HERMES_SKIP_UPDATE_CHECK=1`, `NO_COLOR=1` und begrenztem, großzügigem Timeout; so bleibt der Config-Writer maßgeblich und der Update-Check verzögert den Schreibvorgang nicht.
- Leitet ein Profil seine Shell-Arbeit in ein Werkzeugverzeichnis, setze `terminal.cwd` per CLI und verankere den Verzeichniswechsel zusätzlich in seiner SOUL-Anweisung, damit die Arbeitsgrenze auch bei abweichendem Prozess-Startverzeichnis gilt.
- Nutze die projektgebundene virtuelle Python-Umgebung für Katalog- und Verwaltungsprogramme; das System-Python kann deren Abhängigkeiten oder Rückgabecodes nicht korrekt abbilden.
