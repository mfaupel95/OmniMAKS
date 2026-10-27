---
name: skill-agentic-council-crypto-review
description: Prüft kryptografische Verfahren, Schlüsselverwaltung, Seitenkanal-Festigkeit und Wechselfähigkeit von Algorithmen; für ELSTER-Zertifikate und Sicherungen im Vault als Fragenliste erprobt, ohne Dateien zu öffnen.
metadata:
  type: reference
---

**Zweck:** Prüft, ob Verschlüsselung und Schlüsselverwaltung dem Stand der Technik entsprechen: Algorithmen, Betriebsarten, Schlüssellebenszyklus, Schutz vor Seitenkanälen und Möglichkeit zum Wechsel der Verfahren.

**Wann nutzen:** Bei eigener Kryptografie oder bei Systemen mit Schlüsseln, die einen Schaden verursachen, wenn sie gestohlen werden. Nicht für Dateien, bei denen nur der Zugang zählt und keine eigene Verschlüsselung läuft.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Verschlüsselung der ELSTER-Zertifikate und der Sicherungen einschätzen, im Chat, ohne Dateien zu öffnen.

**Ergebnis:** Keine abschließende Bewertung möglich, weil weder Zertifikat noch Sicherungsskript gelesen wurden. Die entscheidenden Fragen: Ist das Passwort der Zertifikatsdatei stark und liegt es nicht im Vault? Ist das externe Laufwerk per BitLocker verschlüsselt? Ob die Sicherung ein Archivpasswort nutzt, ist offen.

**Gelernt:**
- Der Skill ist für eigene Implementierungen gebaut (Algorithmen, Betriebsarten, Seitenkanäle). Bei einer Standard-Exportdatei wie PKCS#12 zählen vor allem Passwort und Aufbewahrung. Die Prüfpunkte des Skills greifen hier nur am Rand.
- Der stärkste Befund ist organisatorisch: Passwörter gehören nicht in dieselbe Notiz wie der Schlüssel.

**Grenzen:**
- Keine Dateien geöffnet. Die Regeln verbieten das für `Software/`, und die Sicherungsskripte wurden aus demselben Grund nicht gelesen.
- Nur Fragenliste, keine Bewertung.
- Nur Chat-Skizze, keine Datei.
