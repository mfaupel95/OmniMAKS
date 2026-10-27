---
name: skill-agentic-council-adr-template
description: Erstellt ein Architecture-Decision-Record-Gerüst mit Kontext, Optionen, Entscheidung, Folgen und Überprüfungsauslösern; im Chat ohne Dateischreibzugriff nutzbar.
metadata:
  type: reference
---

**Zweck:** Hält eine architektonische Entscheidung als ADR fest: Kontext, mindestens drei Optionen (inklusive Status quo), Begründung, Folgen und konkrete Auslöser für eine spätere Überprüfung.

**Wann nutzen:** Bei Entscheidungen, die teuer umzukehren sind oder mehrere Bereiche betreffen. Nicht für kleine Einzeländerungen.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: ADR-Beispiel „Vault-Index bleibt manuell gepflegt“ im Chat, ohne Datei.

**Ergebnis:** Das Template war vollständig und eignete sich gut. Der Beispiel-ADR wurde im Chat ausgegeben. Eine Datei wurde nicht angelegt. Die Entscheidung ist als Beispiel markiert und nicht getroffen.

**Gelernt:**
- Die Pflicht zu drei Optionen einschließlich Status quo zwingt zu einer ehrlichen Abwägung. Das passt gut zu einer kuratierten Wissensbasis wie dem Vault.
- Die Überprüfungsauslöser verlangen konkrete Schwellen. Im Beispiel wurde eine Notizenzahl gewählt, die frei geschätzt ist. Das sollte vor einer echten Entscheidung belegt werden.

**Grenzen:**
- Der Skill legt keine Datei im Vault ab. Für eine echte ADR-Ablage braucht es einen eigenen Ort.
- Die Beispielzahlen (500 Notizen, Datum) sind Annahmen.
