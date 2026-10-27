---
name: skill-agentic-council-a11y-audit
description: Prüft Web- und UI-Code gegen WCAG 2.2 AA (Tastatur, Screenreader, Kontrast, ARIA, Bewegung, Formulare); für reine Markdown-Dateien nur eingeschränkt anwendbar.
metadata:
  type: reference
---

**Zweck:** Bewertet Oberflächen-Code auf Barrierefreiheit nach WCAG 2.2 AA. Befunde werden mit Kriterium, Schwere und Empfehlung ausgegeben. Automatische Scans übernimmt der Skill nicht.

**Wann nutzen:** Bei Komponenten, Seiten oder Formularen mit Benutzeroberfläche. Nicht geeignet für Markdown-Dateien ohne Darstellungscode.

**Lauf:** 2026-10-26, trockenlauf (eingeschränkt), Aufgabe: Strukturcheck der Vault-Übersicht `MaxHirn/Wissen/INDEX.md`.

**Ergebnis:** Die Datei hat 322 Zeilen. Die Überschriften folgen einer sauberen Hierarchie: eine `h1`, dann `h2` und `h3` ohne Sprünge. 41 Zeilen sind länger als 300 Zeichen, das kann bei Vorlesewerkzeugen und schmalen Anzeigen das Verfolgen erschweren. Die Befunde sind mild, Schweregrad niedrig. Die Kriterien 1.4.3 (Kontrast), 2.1.1 (Tastatur), 4.1.2 (Name, Rolle, Wert) und 2.3.1 (Blitze) betreffen eine Markdown-Datei nicht und wurden nicht bewertet.

**Gelernt:**
- Der Skill passt nur auf Oberflächen. Für Wissensdateien wäre ein Lesbarkeits- oder Strukturcheck besser geeignet.
- Die Ausgabe-Tabelle erzwingt eine Zuordnung zu WCAG-Kriterien. Ohne sichtbare UI müssen Zeilen ausgelassen werden. Das sollte man im Befund offen sagen.

**Grenzen:**
- Kein Code, keine Stile, keine Komponenten geprüft. Nur Struktur und Zeilenlängen.
- Die Befunde zu langen Zeilen sind eine Heuristik, kein WCAG-Verstoß.
