---
name: skill-agentic-council-finops-analysis
description: Ordnet Cloud-Kosten Zweck und Team zu, prüft Auslastung, Verpflichtungsrabatte und Verschwendung und rechnet Stückkosten; für den Vault als Kostenzuordnung nach Kategorien im Chat erprobt.
metadata:
  type: reference
---

**Zweck:** Macht Cloud-Ausgaben nachvollziehbar: Zuordnung nach Zweck, Auslastung, Preisnachlässe bei Verpflichtung, Stückkosten und ungenutzte Ressourcen.

**Wann nutzen:** Bei Cloud-Rechnungen mit mehreren Diensten und Teams. Nicht für lokale Speicherung ohne Abrechnung.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: sinnvolle Kostenzuordnung für den Vault im Chat, auch bei geringen laufenden Kosten, ohne Datei.

**Ergebnis:** Vier Kategorien: Speicher (Vault und Werkstatt), Sicherung (`G:` und extern), Abos (offen, falls Synchronisierung läuft), Modelle (eigene Zeile, nicht dem Vault zugerechnet). Angabe in Gigabyte statt Euro, weil Hardwarepreise und Strom nicht vorliegen. Stückkosten sind für einen persönlichen Vault ohne Nutzen.

**Gelernt:**
- Der Skill ist für Cloud-Konten mit Rechnungen gebaut. Die Zuordnung nach Zweck ist auch für lokale Speicher nützlich, weil man sieht, was den Platz frisst.
- Ob ein Abo läuft, ist die wichtigste offene Frage. Ohne sie fehlt eine Kostenzeile.

**Grenzen:**
- Nur Chat-Skizze, keine Datei.
- Keine Rechnungsdaten gelesen. Die Kategorien beruhen auf der Struktur aus `CLAUDE.md`.
- Der Skill verlangt Verpflichtungsrabatte und Auslastungsdaten. Beides gibt es für den Vault nicht.
