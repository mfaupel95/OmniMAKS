---
name: skill-agentic-council-enterprise-search-strategy
description: Plant eine Suche über interne Wissensquellen in fester Reihenfolge, mit Quellenangabe je Treffer und Schutzregeln; für Index, Notizen und Archiv des Vaults im Chat als Ablauf erprobt.
metadata:
  type: reference
---

**Zweck:** Sucht gezielt in internen Quellen (Wiki, Entscheidungsnotizen, Tickets, Nachbetrachtungen, Chatverläufe), um Belege für eine anstehende Entscheidung zu sammeln. Ergebnis sind Belege, keine Empfehlung.

**Wann nutzen:** Vor einer Entscheidung, zu der es frühere Versuche oder Absprachen geben könnte. Nicht für Fragen nach Außenmärkten oder Bibliotheken.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Suche über Index, Notizen und Archiv im Chat skizzieren (Reihenfolge, Treffer, Datenschutz), ohne Datei.

**Ergebnis:** Reihenfolge Index, Notizen, Archiv, Internet. Jeder Treffer mit Quelle und Pfad. Aus dem Archiv nur Pfad und Titel, kein Textauszug ohne ausdrückliche Anfrage. Treffer der Stufe „besonders schützenswert“ nicht in Berichte übernehmen. Offen: ob die Archivsuche den bestehenden Index nutzt oder die Dateien neu liest.

**Gelernt:**
- Die Reihenfolge aus `CLAUDE.md` (erst Wissen, dann Archiv, zuletzt Internet) passt genau auf das Vorgehen des Skills. Das ist ein guter Beleg, dass die Regeln schon die Struktur tragen.
- Die Quellenangabe pro Treffer ist die wichtigste Regel. Ohne sie lässt sich nicht prüfen, wie alt eine Aussage ist.

**Grenzen:**
- Nur Chat-Skizze, keine Datei, keine Suche ausgeführt.
- Die Frage nach Geschwindigkeit der Archivsuche ist offen.
- Der Skill ist für Unternehmen mit Chat- und Ticketsystemen gebaut. Der Vault hat nur einen Teil dieser Quellen.
