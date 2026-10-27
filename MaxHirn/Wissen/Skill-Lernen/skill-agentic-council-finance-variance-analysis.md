---
name: skill-agentic-council-finance-variance-analysis
description: Erklärt eine Abweichung zwischen Plan und Ist oder Vorperiode mit Zerlegung in Treiber, Einmaleffekt oder Dauer und Folgerung für die Prognose. Für die monatlichen Ausgaben eines Privathaushalts als Plan-Ist-Vorlage mit Erklärungsschwelle im Chat erprobt, ohne Daten.
metadata:
  type: reference
---

**Zweck:** Macht aus einer Zahlendifferenz eine Erklärung: Brückenrechnung, Treiber je Bucket, Einordnung als einmalig, dauerhaft oder zeitversetzt.

**Wann nutzen:** Wenn eine Abweichung erklärt oder eine Prognose angepasst werden soll. Nicht für eine einfache Summe ohne Vergleich.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Abweichungsanalyse für die monatlichen Ausgaben eines Privathaushalts im Chat skizzieren (Plan gegen Ist, Schwelle, Ursachen). Keine Datei, keine Daten gelesen.

**Ergebnis:** Vorlage: Plan je Kategorie gegen Ist, Differenz in Euro und Prozent. Erklärungsschwelle, etwa ab 50 € und 10 % je Kategorie; darunter Sammelposten "Sonstiges". Jeder erklärte Treiber wird als einmalig, dauerhaft oder zeitversetzt eingeordnet. Zeitversatz betrifft vor allem Jahresbeiträge und Nachzahlungen, die im Plan monatlich verteilt sind. Folgerung: Dauerhafte Treiber fließen in den Plan des Folgemonats, einmalige nicht.

**Gelernt:**
- Die Zeitversatz-Klasse ist für den Haushalt wichtiger als im Unternehmen, weil Jahresbeträge den Monatsvergleich verzerren.
- Eine Schwelle in Euro und Prozent zusammen verhindert, dass kleine Kategorien ständig auffallen.

**Grenzen:**
- Keine Ausgaben gelesen, keine Pläne vorhanden. Die Schwellen sind Vorschläge, keine geprüften Werte.
- Der Skill verlangt Volumen-, Preis- und Mix-Zerlegung. Für Haushaltsausgaben ist nur die Zerlegung in Kategorien sinnvoll.
- Der Skill ist für Unternehmensberichte mit Prognoseanpassung gebaut, die Folgerung für den Haushalt ist entsprechend vereinfacht.
