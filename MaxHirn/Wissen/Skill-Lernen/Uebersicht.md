# Skill-Lernen: Übersicht der Ergebnisse

Stand: 2026-10-26. Die Vormerkliste mit Wiederholungen liegt unter `Werkstatt\Projekte\skill-lernen\wiederholen.md`.

**Zahlen (aus `fortschritt.md`):** 259 Einträge, davon 184 trockenlauf, 59 übersprungen (Dubletten), 3 nicht-ausführbar. Im Ordner liegen 200 Lernnotizen.

**Was ein Trockenlauf hier bedeutete:** Die meisten Läufe lieferten eine Einschätzung im Chat, ohne Dateien zu öffnen. Es gab nur wenige Läufe mit echtem Dateizugriff (etwa `security-review`, das ein echtes Review lieferte). Die Notizen geben deshalb meist die Einschätzung wieder, nicht eine geprüfte Befundlage.

## Befunde mit Vault-Bezug

Diese Läufe haben etwas gefunden, das im Vault zu tun ist:

- **`posteingang`** (agentic-atlas:reviewing-agent-designs): Dateien werden ohne Bestätigung verschoben (hoch), die Gegenprüfung ist nicht deterministisch (mittel).
- **`Wissen/Zugaenge.md`** (agentic-council:data-classification): steht auf „vertraulich“, gehört in „besonders schützenswert“.
- **Suchindex des Archivs** (agentic-council:data-classification): folgt der Stufe des Archivs, ist aber nicht als Stufe festgehalten.
- **Index-Konflikte** (agentic-council:distributed-patterns): Mehrere Geräte schreiben dieselbe Datei, ein Hauptschreiber wird empfohlen.
- **Stiller Sicherungsfehler** (agentic-council:failure-mode-analysis): größtes Risiko, weil er unbemerkt bleibt.
- **Wiederherstellungsschlüssel BitLocker** (agentic-council:hw-sw-boundary): gehört nicht in den Vault.
- **Ende-zu-Ende-Prüfung der Sicherung** (agentic-council:e2e-testing): Stichprobe mit Wiederherstellung ist der wichtigste Punkt.
- **Trennung Vault, Archiv, Werkstatt** (agentic-council:isolation-review): Prüfung über Rechte und Git-Whitelist, kein Schreibtest.

## Offene Fragen an dich

1. Liegt das Passwort des ELSTER-Zertifikats irgendwo im Vault?
2. Ist das externe Sicherungslaufwerk mit BitLocker verschlüsselt, und wo liegt der Wiederherstellungsschlüssel?
3. Bist du gewerblich tätig? Davon hängt die Aufbewahrungspflicht für Belege ab.
4. Welche Synchronisierung läuft zwischen den Geräten?

## Ergebnis nach Gruppe

- **agentic-atlas** (3 Läufe): Empfehlungen zu Entwurf und Prüfung von Agenten-Systemen, Änderungsplan für `notiz` (im Wesentlichen konform), Befunde zu `posteingang`.
- **agentic-council** (rund 60 Läufe, überwiegend Skizzen): Befunde siehe oben, der Rest sind allgemeine Entwurfshinweise.
- **Blockiert**: `agentic-council:council`, `agent-memory:memory-search`, `anthropic-skills:docs`.
