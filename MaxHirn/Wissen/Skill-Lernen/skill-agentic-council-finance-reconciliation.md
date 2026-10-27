---
name: skill-agentic-council-finance-reconciliation
description: Stimmt ein Hauptbuch- oder Bankkonto gegen seine Quelle ab, mit Saldoprobe, Erklärung jeder Differenz und Freigabe; für den monatlichen Abgleich von Kontoauszug und Belegablage als Drei-Spalten-Vorlage mit Umgang für fehlende Belege im Chat erprobt, ohne Datei.
metadata:
  type: reference
---

**Zweck:** Bringt ein Bilanzkonto auf seine Quelle zurück und erklärt jede verbleibende Differenz, sodass ein Prüfer den Stand nachvollziehen kann.

**Wann nutzen:** Am Monatsende für jedes Konto, das gegen eine externe oder interne Quelle prüfbar ist (Bank, Nebenbuch, Plan). Nicht für Vorgänge ohne Saldo.

**Lauf:** 2026-10-26, trockenlauf, Aufgabe: monatlicher Abgleich Kontoauszug gegen Belegablage im Chat als Vorlage mit drei Spalten, einschließlich Umgang mit fehlenden Belegen. Keine Datei, nichts abgeglichen.

**Ergebnis:** Drei Spalten: Kontoauszug (Datum, Betrag, Text), Beleg (Nummer, Datum, Betrag, Gegenpartei), Status. Status-Werte: abgeglichen, Betrag abweichend, Beleg fehlt, Beleg ohne Umsatz, Zeitversatz. Saldoprobe: Anfangssaldo plus Summe der Umsätze gleich Endsaldo. Fehlende Belege: offene Liste mit Frist, verantwortlicher Person, Nachforderung beim Gegenüber, Eskalation nach Frist; Buchung ohne Beleg nur mit ausdrücklicher Begründung.

**Gelernt:**
- Die Saldoprobe kommt vor allem anderen. Solange sie nicht aufgeht, sagt die Zeilenprüfung nichts Verlässliches.
- Fehlende Belege sind keine Differenz, sondern eine offene Aufgabe mit Halbwertszeit. Der Wert liegt in Frist und Verantwortlichem, nicht in der Liste.

**Grenzen:**
- Der Skill setzt Hauptbuch und Nebenbuch voraus. Eine private Belegablage hat keines, die Vorlage ist deshalb eine vereinfachte Form.
- Keine Kontoauszüge gelesen, keine Belege geprüft, keine Summen gegengerechnet.
- Wesentlichkeitsgrenze und Freigabe-Rollen (Ersteller, Prüfer, Freigeber) sind für einen Einzelhaushalt nicht anwendbar.
