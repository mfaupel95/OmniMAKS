---
name: skill-agentic-council-analytics-design
description: Plant Messkonzept für ein Produkt (Kennzahlenhierarchie, Ereignisbenennung, Trichter, A/B-Tests, Datenpipeline); im Chat für den Vault-Index als Skizze erprobt.
metadata:
  type: reference
---

**Zweck:** Legt fest, was gemessen wird: Kennzahlen mit Leit- und Schutzkennzahlen, Ereignisnamen, Eigenschaften, Trichter, Experimente und Erfolgskriterien.

**Wann nutzen:** Vor der Einführung eines Features, das später bewertet werden soll. Nicht für einmalige Auswertungen.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: drei Ereignisse für den Vault-Index im Chat skizzieren, ohne Datei.

**Ergebnis:** Drei Ereignisse vorgeschlagen: `vault.searched.query`, `vault.created.note`, `vault.reported.check`. Jeweils mit Eigenschaften als Zähler. Suchtexte werden bewusst nicht gespeichert, weil das Archiv Privates enthält. Keine Datei angelegt.

**Gelernt:**
- Die Namensregel `kategorie.aktion.objekt` ist für einen persönlichen Vault übertragbar, auch ohne Analysesoftware.
- Datenschutz verlangt hier eine klare Grenze zwischen Zählern und Inhalten. Der Skill nennt das nur indirekt unter „Privacy“.

**Grenzen:**
- Die Ereignisse sind Vorschläge, noch nicht umgesetzt.
- Keine Schutzkennzahlen festgelegt, nur drei Ereignisse.
- Der Skill ist für Produkte mit vielen Nutzern gedacht. Für einen einzelnen Vault ist vieles überdimensioniert.
