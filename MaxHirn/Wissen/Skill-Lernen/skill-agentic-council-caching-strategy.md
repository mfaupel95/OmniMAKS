---
name: skill-agentic-council-caching-strategy
description: Plant Zwischenspeicherung über Schichten (Browser, Edge, Anwendung, Datenbank) mit Schlüsseln, Lebensdauer, Invalidierung und Aufwärmen; für den Vault-Index als Entscheidung gegen Cache erprobt.
metadata:
  type: reference
---

**Zweck:** Legt fest, was wo zwischengespeichert wird, wie lange, wie es ungültig wird und wie ein kalter Start abgefangen wird.

**Wann nutzen:** Bei Diensten mit vielen Lesezugriffen und messbarer Latenz oder Last. Nicht bei kleinen lokalen Beständen.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Entscheidung, ob der Vault-Index bei jeder Suche neu gelesen oder zwischengespeichert werden sollte, im Chat, ohne Datei.

**Ergebnis:** Empfehlung: bei jeder Suche neu lesen, kein Cache. Begründung: Die Datei ist klein (rund 320 Zeilen), das Lesen kostet Millisekunden. Ein Cache könnte frisch eingetragene Einträge verbergen. Erst bei deutlichem Wachstum (mehrere tausend Einträge) lohnt sich ein Cache, der an die Änderungszeit der Datei gekoppelt ist. Die Suchgeschwindigkeit selbst wurde nicht gemessen.

**Gelernt:**
- Die Pflichtfragen des Skills (Schichten, Schlüssel, Lebensdauer, Aufwärmen) passen nicht auf eine lokale Datei. Die Gegenfrage „brauchen wir überhaupt einen Cache?“ ist der eigentliche Mehrwert.
- Die Invalidierung ist die größte Fehlerquelle. Wo es um frische Einträge geht, lohnt sich der Verzicht.

**Grenzen:**
- Nur Entscheidung im Chat, keine Datei.
- Keine Messung der Lesezeit.
- Der Skill ist für Webdienste mit CDN gebaut, die Teile sind hier nicht anwendbar.
