---
name: skill-agentic-atlas-designing-agent-systems
description: Berät beim Entwurf eines Agenten-Systems mit Mustern aus dem Agentic Atlas, mit Befragung, Konsultation und Zustimmung vor dem Anlegen von Dateien.
metadata:
  type: reference
---

**Zweck:** Führt von einem Entwurfsproblem zu einem Vorschlag für die Zerlegung eines Agenten-Systems (Skills, Agenten, Übergaben, Prüfstellen). Jede strukturelle Entscheidung wird mit einem Atlas-Abschnitt belegt. Dateien entstehen erst nach Freigabe.

**Wann nutzen:** Bei einem neuen Agenten- oder Skill-System mit mehreren Teilen oder Übergaben, nicht bei einzelnen Fragen zu einem Muster. Für einzelne Muster reicht der günstige Weg über `atlas_cards`.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Beratung für Vault-Routinen (Notizen ordnen, Index pflegen).

**Ergebnis:** Der Atlas-Abruf lief inline, weil die Aufgabe nur eine Konsultation ohne Schreibzugriff verlangte. Der Suchbegriff war generisch. Die Suche ergab 18 Treffer, davon wurden vier Karten geprüft: `verification-asymmetry`, `one-guide-three-bills`, `llm-dispatch`, `heavy-agent` (Revision v1.1.0). Empfehlungen aus den Karten:
- Prüfung der Ergebnisse durch eine getrennte Stelle, nicht durch den erzeugenden Agenten selbst. Deterministische Prüfungen zuerst (`verification-asymmetry`).
- Schwere Anweisungen nur in einen Subagenten auslagern, wenn sie viel Kontext kosten. Auslagern verschiebt die Kosten, es spart sie nicht. Das Kosten-Argument hängt vom Aufbau ab (`one-guide-three-bills`, `heavy-agent`).
- Übergaben an Subagenten mit Modell und Umfang angeben, da sonst das Modell des Elternteils übernommen wird (`llm-dispatch`).

**Gelernt:**
- Für einen Vault-Index mit wenigen Routinen ist ein voller Mehragenten-Aufbau oft zu teuer. Der Atlas stützt die Empfehlung, zuerst einen einzelnen Skill mit deterministischer Prüfung zu bauen.
- Die Karten sagen wenig über konkrete Prüfschritte. Dafür braucht es `atlas_read` auf die Abschnitte.

**Grenzen:**
- Nur vier Karten geprüft, Abschnitte nicht gelesen, Zitate deshalb nicht gegengeprüft.
- Die Befragung fand nicht statt, weil die Aufgabe im Auftrag bereits vollständig beschrieben war.
- Es wurde nichts angelegt.
