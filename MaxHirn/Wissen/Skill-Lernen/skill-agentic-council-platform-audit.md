---
name: skill-agentic-council-platform-audit
description: Prüft eine Anwendung gegen Richtlinien ihrer Zielplattformen (Bedienmuster, Berührungsflächen, Berechtigungen, Prüfregeln der Stores); für Dateinamen und Umzug im Vault als Plattformregeln für Windows und Linux im Chat erprobt.
metadata:
  type: reference
---

**Zweck:** Stellt fest, ob eine Anwendung die Erwartungen ihrer Plattform erfüllt, und ordnet Verstöße nach Schwere mit konkreter Abhilfe.

**Wann nutzen:** Vor dem Veröffentlichen einer App in einem Store oder bei plattformübergreifenden Funktionen. Nicht für Dateien und Ordner ohne Oberfläche.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: prüfen, ob die Namen im Vault den Windows-Regeln entsprechen und was beim Umzug auf eine andere Plattform bricht, im Chat, ohne Liste der Dateien.

**Ergebnis:** Windows-Regeln: verbotene Zeichen, reservierte Namen, Pfadgrenze 260 Zeichen. Beim Umzug brechen: Groß- und Kleinschreibung (Linux unterscheidet), Unicode-Normalisierung (macOS), feste Laufwerksbuchstaben und absolute Pfade in Skripten und Konfigurationen. Empfehlung: Namen ohne Umlaute und ohne Schreibweisen, die sich nur in der Groß- und Kleinschreibung unterscheiden. Die Namen wurden nicht geprüft, nur auf Freigabe.

**Gelernt:**
- Der Skill ist für Oberflächen in Stores gebaut. Dateinamen fallen nur unter den Teil „Plattformregeln“, und der ist für den Umzug die eigentlich nützliche Frage.
- Die Regel im Notiz-Skill (keine Umlaute im Dateinamen) wird im Vault nicht durchgehalten. Das ist ein Widerspruch zwischen Regel und Bestand, den man auflösen sollte.

**Grenzen:**
- Keine Dateinamen gelesen, keine Plattform getestet.
- Die Regeln beruhen auf allgemeinem Wissen zu Windows, macOS und Linux.
- Der Skill verlangt Bedienmuster, Store-Prüfung und Berechtigungen für Apps. Für Dateinamen ist das nur eingeschränkt anwendbar.
