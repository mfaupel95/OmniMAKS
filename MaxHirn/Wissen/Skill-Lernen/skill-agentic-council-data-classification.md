---
name: skill-agentic-council-data-classification
description: Stuft Dateninhalte nach Schutzstufe ein (öffentlich, intern, vertraulich, besonders schützenswert) und ordnet Ordner und Pflichten zu; für den Vault als Einstufung im Chat erprobt.
metadata:
  type: reference
---

**Zweck:** Ordnet jedes Datenelement einer Schutzstufe zu, verfolgt personenbezogene Daten durch ihren Lebensweg und legt Pflichten je Stufe fest (Zugriff, Verschlüsselung, Maskierung, Aufbewahrung, Protokoll).

**Wann nutzen:** Wenn ein System oder eine Sammlung personenbezogene oder geschäftskritische Daten enthält und niemand sagen kann, welche Schutzregeln gelten.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Einstufung der Vault-Inhalte mit Beispielordnern, im Chat, ohne Datei. Gelesen wurde nur die Struktur aus `CLAUDE.md` und den Berechtigungsregeln, keine Dateiinhalte.

**Ergebnis:** Vier Stufen mit Ordnern. Befunde:
- `Wissen/Zugaenge.md` mit Schlüsseln und Tokens steht im Entwurf auf „vertraulich“. Richtig wäre „besonders schützenswert“.
- Der Suchindex des Archivs enthält Auszüge aus den Archivdateien und folgt deren Stufe. Das ist nirgends festgehalten.
- Für die Stufe „besonders schützenswert“ fehlt eine Regel, wohin Sicherungen und Weitergaben dürfen. Die Regel für die Zertifikate gibt es schon.
Keine Datei angelegt, nichts geändert.

**Gelernt:**
- Die Stufen des Skills sind für Unternehmen gedacht. Für einen Vault reichen vier Stufen mit Beispielordnern, Anforderungen je Stufe lassen sich schlanker fassen.
- Die wertvollste Frage des Skills ist der Lebensweg: Wo werden Daten kopiert? Beim Vault sind das Sicherungen und der Suchindex.

**Grenzen:**
- Keine Dateiinhalte gelesen, nur Ordnerstruktur.
- Die Pflichten je Stufe (Verschlüsselung, Aufbewahrung) sind als Entwurf gemeint, nicht geprüft.
- Die Einstufung ist eine Empfehlung, keine Entscheidung.
