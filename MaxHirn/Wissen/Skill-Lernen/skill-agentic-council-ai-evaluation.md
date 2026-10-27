---
name: skill-agentic-council-ai-evaluation
description: Entwirft ein Bewertungsgerüst für KI-Funktionen (Golden Dataset, Bewertungsrubrik, Halluzinationsprüfung, Regressionstest, Produktionsmonitoring); im Chat für die Vault-Suche erprobt.
metadata:
  type: reference
---

**Zweck:** Plant die Bewertung einer KI-Funktion: Bewertungsdimensionen, Prüfset mit Verteilung, automatische Bewertung, Halluzinationsprüfung, Regressionstest und Überwachung im Betrieb.

**Wann nutzen:** Vor dem Einsatz oder bei Änderungen an einer KI-Funktion, die messbare Qualität braucht. Nicht für reine Konfigurationsfragen.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Skizze eines Prüfsets für die Vault-Suche, im Chat, ohne Datei.

**Ergebnis:** Der Skill liefert ein vollständiges Gerüst. Für die Vault-Suche wurde daraus eine schlanke Skizze: 30 bis 50 Anfragen mit Verteilung 60/25/15, Trefferprüfung in den Top 3 ohne LLM, deterministische Pfadprüfung. Der Schwellenwert von 80 % ist eine Annahme und noch nicht belegt.

**Gelernt:**
- Für eine Suche ohne generative Antwort braucht es keinen LLM-Richter. Der Skill sieht das Bewertungsmodell als Standard vor. Eine Vorprüfung, ob die Funktion überhaupt generiert, spart hier Aufwand.
- Die Halluzinationsprüfung über Referenzen lässt sich bei Pfaden direkt als Dateiprüfung umsetzen.

**Grenzen:**
- Keine Datei angelegt. Das Prüfset existiert nur im Chat.
- Der Schwellenwert ist nicht geprüft.
- Der Skill ist für generative Funktionen geschrieben. Für Suchfunktionen wurde er angepasst.
