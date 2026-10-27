---
name: skill-agentic-council-finance-tax-research
description: Beantwortet eine Steuerfrage mit einem Recherchememo: Rangfolge der Quellen von Gesetz bis Schreiben, Zitat des Wortlauts, Anwendung auf den Fall, Unsicherheitsbewertung. Für die Frage nach der sofortigen Aufwandsbuchung eines Arbeitsmittels bis zu einer Nettogrenze im Chat erprobt, ohne Recherche.
metadata:
  type: reference
---

**Zweck:** Liefert ein belastbares Steuermemo auf Grundlage zitierter Quellen, mit vorsichtiger Schlussfolgerung und Bewertung unsicherer Positionen.

**Wann nutzen:** Bei konkreten Steuerfragen, deren Antwort von einer Norm, einem Schreiben oder einem Urteil abhängt. Nicht für allgemeine Einordnung.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: Vorgehen skizzieren, wie geprüft wird, ob ein Arbeitsmittel bis zu einer Nettogrenze sofort absetzbar ist, und welche Quellen maßgeblich sind. Ohne Recherchewerkzeuge, keine Datei.

**Ergebnis:** Prüfweg: Erst die Grenze im Gesetz nachschlagen (EStG §6 Abs. 2 für geringwertige Wirtschaftsgüter), dann Verwaltungsanweisungen (EStR, BMF-Schreiben), dann Rechtsprechung des BFH. Die Grenze wurde in den letzten Jahren geändert, deshalb ist der Wert aus dem aktuellen Gesetzestext zu übernehmen, nicht aus dem Gedächtnis. Ergebnis ist ein Memo mit Zitat, Anwendung und Vorbehalt, nicht eine Zahl allein.

**Gelernt:**
- Der Skill ist auf Unternehmensbilanzen gebaut (Rückstellung für unsichere Steuerpositionen). Für eine einzelne Aufwandsfrage ist der Kern das Zitat und die Rangfolge, nicht die Bilanzierung.
- Die Rangfolge Gesetz vor Verwaltung vor Rechtsprechung verhindert, dass eine Verwaltungsmeinung als Gesetz gelesen wird.

**Grenzen:**
- Keine Recherche durchgeführt, keine Grenzwerte geprüft, keine Quelle wörtlich zitiert.
- Der Skill verlangt ein Memo mit Konzernbezug, FIN 48 und Schedule UTP. Für Privatpersonen nur eingeschränkt anwendbar.
- Keine Rechtsberatung. Der Skill selbst nennt das Memo als Arbeitspapier für Steuerfunktion und Berater.
