---
name: skill-operations-change-request
description: Formuliert einen Änderungsantrag mit Auswirkung, Risiko, Umsetzung, Rückweg und Freigabe. Für eine Änderung am Index-Format der Vault-Skripte im Chat skizziert.
metadata:
  type: reference
---

**Zweck:** Macht eine Änderung nachvollziehbar, bevor sie umgesetzt wird, und sichert den Rückweg ab.

**Wann nutzen:** Bei Änderungen an Dateiformaten, Skripten oder Abläufen, von denen andere Teile abhängen. Nicht für Korrekturen an einzelnen Notizen.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Ablauf für eine Änderung am Index-Format skizzieren. Keine Datei, kein Antrag geschrieben.

**Ergebnis:** Betroffen sind die Indexdatei, die Skripte, die den Index lesen oder schreiben, der Prüfagent vault-pruefer und die Lernnotizen. Risiko: Skripte brechen bei falschem Format. Rückweg: vor der Änderung eine Kopie mit Datum anlegen, die Änderung auf der Kopie testen, erst dann umstellen. Freigabe: Max als einziger Genehmigender. Die Änderung wird im Regelblatt festgehalten.

**Gelernt:**
- Ein Antrag ohne Rückweg ist keiner. Die Kopie vor der Änderung ist der Rückweg.
- Ein Format, das mehrere Skripte liest, braucht die Liste dieser Skripte, sonst bricht man sie unbemerkt.

**Grenzen:**
- Kein Antrag geschrieben, keine Skripte gelesen.
- Der Skill verlangt Gremien, Kommunikationspläne und Schulungen. Für einen Einzelnutzer genügen Auswirkung, Rückweg und Freigabe.
