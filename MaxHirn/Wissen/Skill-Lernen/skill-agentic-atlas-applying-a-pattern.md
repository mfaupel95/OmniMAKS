---
name: skill-agentic-atlas-applying-a-pattern
description: Wendet ein benanntes Muster des Agentic Atlas auf einen bestehenden Skill an und liefert einen geprüften Änderungsplan mit Quellenangaben, ohne Dateien zu ändern, bis der Nutzer zustimmt.
metadata:
  type: reference
---

**Zweck:** Ordnet ein Muster des Agentic Atlas einem vorhandenen Artefakt (Skill, Agent, Hook, Workflow) zu und erstellt daraus einen Änderungsplan. Jede Änderung wird mit einem Abschnitt des Atlas belegt. Ausgeführt wird erst nach Freigabe.

**Wann nutzen:** Wenn ein Skill nach einem bestimmten Entwurfsmuster verbessert werden soll und der Nutzer das Muster nennt oder der Atlas-Begriff bekannt ist. Nicht für freie Umformulierungen ohne Atlas-Bezug.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Muster auf den Vault-Skill „notiz“ anwenden, nur Änderungsplan.

**Ergebnis:** Der Plan wurde inline erstellt. Der Atlas-Abruf lief über `atlas_orient` (Suche „skill instructions structure and clarity“), `atlas_cards` für `baseline-skill` und `contract-documentation` (Revision v1.1.0). Das Ziel-Skill „notiz“ hat Name, Beschreibung und Körper (55 Zeilen) und kein Übergabe-Artefakt zwischen Komponenten. Deshalb trifft `contract-documentation` nicht zu und wurde nicht angewendet. `baseline-skill` bestätigt die Form. Der Körper ist durch konkrete Regeln begründet, deshalb kein Kürzen. Ergebnis: im Wesentlichen konform. Einziger Diskussionspunkt ist die Beschreibung, die imperativ „Benutzen, wenn …“ formuliert. Der Atlas verlangt eine Aussage in dritter Person. Die Auslösefunktion spricht für die jetzige Form, deshalb keine Änderung vorgeschlagen. Es wurde keine Datei verändert.

**Gelernt:**
- Der Skill verlangt die Konsultation über den Subagenten `design-auditor` im Apply-Modus. Im Trockenlauf wurde die Prüfung inline ausgeführt, weil die Aufgabe nur einen Plan ohne Schreibzugriff verlangte. Für einen echten Apply-Lauf gilt der Ablauf des Skills.
- Die Atlas-Werkzeuge sind deferred und müssen per `ToolSearch` mit `select:` geladen werden, bevor sie aufrufbar sind.
- Der Skill verbietet, Artefaktinhalt an den Atlas zu senden. Die Suchanfrage enthielt nur allgemeine Entwurfsbegriffe.

**Grenzen:**
- Die Suche ergab mehrere Kandidaten. Ausgewählt wurden nur zwei Muster, nicht die volle Liste (11 Treffer, Cursor nicht weiterverfolgt).
- Die Abschnitts-Adressen (`#model-and-claims`, `#scope-and-boundaries`) stammen aus den Karten-Quellen. Sie wurden nicht mit `atlas_read` gegengeprüft.
- Die Änderung in Schritt 4 (Ausführung) wurde bewusst nicht gemacht.
