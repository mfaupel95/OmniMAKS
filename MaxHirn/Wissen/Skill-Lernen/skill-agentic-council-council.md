---
name: skill-agentic-council-council
description: Mehragenten-Ratsworkflow (19 Perspektiven plus Steward) mit Interview, Sitzungsdateien und Freigaben; im Trockenlauf nicht ausführbar.
metadata:
  type: reference
---

**Zweck:** Führt einen interaktiven Rat aus Perspektiv-Agenten durch Interview, Auswahl, drei Verhandlungsrunden und einen Umsetzungsplan. Ergebnis ist ein Entwicklungsplan für größere Funktionen.

**Wann nutzen:** Bei großen, unklaren Vorhaben, die mehrere Fachsichten brauchen, und wenn Max die Befragung und die Freigaben mitträgt.

**Lauf:** 2026-10-26, nicht-ausführbar, Aufgabe: Ratsbewertung, ob der Vault-Index eine Prüfroutine braucht.

**Ergebnis:** Nicht ausgeführt. Der Workflow fragt zuerst interaktiv (Interview), legt Sitzungsordner unter `.claude/council/sessions/` und eine globale Registry an und startet mehrere Agenten. Im Trockenlauf-Auftrag ist das nicht zulässig, weil dabei Dateien geschrieben und Subagenten gestartet werden. Ein Lauf würde also gegen die Regel „nichts speichern, keine Subagenten mit Schreibrecht“ verstoßen.

**Gelernt:**
- Mehragenten-Workflows brauchen eine eigene Testform: einen Modus ohne Sitzungsdateien und ohne Interview, falls sie in skill-lernen geprüft werden sollen.
- Der Rat ist für die Frage nach einer Prüfroutine für den Vault-Index zu groß. Ein einzelner Blick über den Skill genügt dafür.

**Grenzen:**
- Die Ratsbewertung der Frage selbst wurde nicht gemacht.
- Der Skill bleibt offen und sollte später mit einem eigenen Testauftrag wiederholt werden, der keine Sitzungsdateien anlegt.
