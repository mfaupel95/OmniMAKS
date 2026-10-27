---
name: skill-agentic-atlas-reviewing-agent-designs
description: Prüft ein bestehendes Artefakt (Skill, Agent, Plugin, Hook, Workflow) gegen Muster des Agentic Atlas und liefert einen Befundbericht mit Zitaten, ohne zu ändern.
metadata:
  type: reference
---

**Zweck:** Auditiert ein vorhandenes Agenten-Artefakt gegen den Atlas. Befunde werden nach Wichtigkeit geordnet und mit Fundstelle, Empfehlung und Abschnitts-Zitat angegeben. Behebungen laufen erst auf Anfrage.

**Wann nutzen:** Bei einer Prüfung eines bestehenden Skills oder Workflows, etwa vor einer Freigabe oder bei einem Verdacht auf Schwächen. Für eine Frage zu einem einzelnen Muster reicht `atlas_cards`.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Vault-Skill „posteingang“ prüfen, nur Bericht.

**Ergebnis:** Der Skill „posteingang“ verschiebt Dateien aus `Posteingang/` in die Archivstruktur. Der Atlas-Abruf lief inline (Suche „agent run side effects on files, recovery and verification after run“, 22 Treffer, zwei Karten geprüft: `effect-discipline`, `verification-asymmetry`, Revision v1.1.0). Drei Befunde:
1. **Hoch:** Das Verschieben von Dateien ist nicht rückholbar. Der Atlas verlangt bei irreversiblen Wirkungen eine Bestätigung durch einen Menschen vor der Ausführung ([effect-discipline § model-and-claims](https://agentic-atlas.dev/nodes/effect-discipline#model-and-claims)). Der Skill führt in Schritt 3 den echten Lauf ohne Rückfrage aus. Vorschlag: nach dem Testlauf die Liste der geplanten Verschiebungen zeigen und auf Freigabe warten.
2. **Mittel:** Die Gegenprüfung nach dem Lauf übernimmt derselbe Agent ohne festen Prüfschritt. Der Atlas verlangt deterministische Prüfungen, bevor man einem Ergebnis glaubt ([verification-asymmetry § model-and-claims](https://agentic-atlas.dev/nodes/verification-asymmetry#model-and-claims)). Vorschlag: Dateianzahl vor und nach dem Lauf zählen und die verbliebenen Dateien auflisten.
3. **Niedrig:** Der Testlauf ist nur ab „ein paar Dutzend Dateien“ vorgesehen. Bei kleinen Mengen entfällt er. Ein Rückweg für verschobene Dateien ist nicht beschrieben.

**Gelernt:**
- Der Skill enthält bereits gute Schutzregeln (Zertifikate und Passwort-Exporte werden nicht verschoben). Sie decken aber nur einen Teil des Risikos ab, nämlich die Auswahl, nicht die Ausführung.

**Grenzen:**
- Nur zwei Karten geprüft, keine Abschnitte gelesen. Die Befunde stützen sich auf die Aussagen der Karten, nicht auf den vollen Text.
- Das Skript `sort_inbox.py` wurde nicht gelesen, die Ausführung dort ist deshalb nicht geprüft.
- Es wurde nichts geändert.
