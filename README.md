# Verfahrenswahl beim Zählen – welches Verfahren, gemessen woran? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-zaehlverfahren-demo.streamlit.app/)** -->

Stück 16 von 16, der Abschluss der Reihe **„Abzählen und erzeugende Funktionen“** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (die Linie wird erst vollständig veröffentlicht). Vorgänger sind `aufzaehlen-rekursion-demo` (Stück 1), `rationale-ef-demo` (Stück 2), `symbolische-methode-demo` (Stück 3), `semiring-rekursion-demo` (Stück 4), `multimengen-partitionen-demo` (Stück 5), `beschriftete-strukturen-demo` (Stück 6), `siebformel-demo` (Stück 7), `zaehlen-nach-parameter-demo` (Stück 8), `asymptotik-demo` (Stück 9), `gleichverteilt-ziehen-demo` (Stück 10), `burnside-polya-demo` (Stück 11), `isomorphieausschluss-demo` (Stück 12), `frontier-diagramm-demo` (Stück 13), `tutte-polynom-demo` (Stück 14) und `knuth-schaetzer-demo` (Stück 15). Diese Demo lässt die **Verfahren** dieser Stücke auf denselben Aufgaben nebeneinander laufen, mit demselben Maß für den Aufwand (**Grundschritte** mit einer Obergrenze, dem **Budget**), und prüft jede exakte Zahl gegen die anderen Verfahren der Zeile. Das Gegenstück in der Inverse-Linie ist `verfahrensvergleich-demo` (Regularisierungsverfahren auf einer gemeinsamen Welt).

## Warum dieses Problem

Wer eine Zahl von Möglichkeiten braucht, hat die Wahl: Tabelle, Transfermatrix, erzeugende Funktion, Siebformel, Burnside, Frontier-Diagramm, Tutte-Polynom, Schätzer. Welches passt, hängt an der **Struktur**, an der **Frage** (nur die Zahl, die Liste aller Vertreter, ein Polynom für viele Parameter) und an der **Größe**. Die Demo misst, wo welches gewinnt, wo es **falsch** wird und wo **nichts** mehr geht.

## Befunde und Korrekturen gegenüber dem Plan

- **Hook bestätigt, differenzierter:** In 45 Zellen aus sieben Familien (Budget 1.000.000 Schritte) gewinnen **zwölf verschiedene Verfahren** (zwölf Bezeichnungen, etwa sieben Grundideen); in 4 Zellen gewinnt keines. In **sechs von sieben Familien wechselt der Gewinner** mit der Größe.
- **Budget 1.000.000 statt 5.000.000 in der App (Rechenzeit):** Die Tabelle rechnet beim ersten Aufruf rund 36 Sekunden; mit 3 Millionen waren es 71. Das verschiebt gegenüber Phase 0 einzelne Zellen: Dominosteine 16×16 ohne Gewinner (die Profil-Rechnung braucht 2.661.721 Schritte), Dreifärbungen 6×6 und 7×7 mit dem Tutte-Polynom über dem Budget, Teilmengensumme n = 20 mit Gewichten bis 1.000 ohne Aufzählen (1.233.265). Phase 0 hatte 3 Zellen ohne Gewinner, die App 4.
- **Neue Zellen:** Binärketten mit n = 100 (Wende: Matrixpotenz 88 gegen Tabelle 99 Schritte), Halsketten mit n = 14 und 16.
- **Das Regelwerk trifft weniger genau als in Phase 0:** Version 1 (vor der Messung geschrieben) hat 41 von 45 gleich, 2 gleichwertig (Binärketten n = 100: Faktor 1,125; Dreifärbungen 2×2: Faktor 1,03), 2 verfehlt (Binärketten n = 1.000: die Schwelle 10.000 war falsch; Dominosteine 16×16: die Regel nennt die Profil-Rechnung, die im Budget nicht fertig wird). Version 2 mit der Schwelle 100: 42 gleich, 2 gleichwertig, 1 verfehlt, aber **angepasst, nicht vorhergesagt**.
- **Kasteleyn:** in Gleitkomma ab 12×12 falsch (Abweichung −72 bei 53.060.477.521.960.000, der Wert liegt über 2⁵³). Der Gewinner muss deshalb dem **Ganzzahl-Referenzwert** entsprechen; ohne ganzzahliges Verfahren im Budget bleibt Kasteleyn „exakt, ungeprüft“ und kann nicht gewinnen.
- **Eigene Fehler im Bau (nicht in der Messung):** (1) Der Vergleich der Werte über `repr` scheiterte an der Grenze von 4300 Stellen (Binärketten mit n = 100.000 haben 20.899); die Werte werden jetzt direkt verglichen. (2) Die Ergebnisse mit 17 Stellen standen als „5,30·10¹⁶ statt 5,30·10¹⁶“ im Urteilstext: Zahlen, bei denen jede Stelle zählt, stehen jetzt voll ausgeschrieben. (3) Ein Test der Vierfarben-Frage mit Budget 10⁹ ließ die Transfermatrix wirklich rechnen (215 Sekunden); er läuft jetzt mit echtem Budget. (4) Der erste Entwurf des Plans zählte „21 Zellen“ mit Schätzer statt der 14 vergleichbaren.
- **Präfix `zvw_`, Port 9329; Repo `zaehlverfahren-demo`.**

## Modell

**Sieben Familien:** F1 Binärketten ohne zwei Einsen hintereinander (Aufzählen, Tabelle, Matrixpotenz), F2 Surjektionen von n Elementen auf k (Aufzählen, Stirling-Tabelle, Siebformel, Potenz der erzeugenden Funktion), F3 Halsketten mit drei Farben (alle Wörter, FKM, Burnside), F4 Dominosteine im n×n-Brett (Aufzählen, Profil-Rechnung, Kasteleyn), F5 einfache Wege im n×n-Gitter (Aufzählen, Frontier-Diagramm), F6 Dreifärbungen des n×n-Gitters (Aufzählen, Transfermatrix, Tutte-Frontier), F7 Zahl der Teilmengen mit halber Gesamtsumme (Aufzählen, Tabelle).

**Grundschritte (je Verfahren festgelegt):** Aufzählen: besuchte Knoten (oder Abbildungen, Färbungen, mit n Schritten je Wort bei den Halsketten); Tabelle: Einträge; Matrixpotenz: acht Multiplikationen je 2×2-Produkt; Siebformel: (k + 1) Potenzen mit Bitlänge plus gesetzten Bits; Potenz der erzeugenden Funktion: k · (n + 1)(n + 2)/2; FKM: Rekursionsaufrufe; Burnside: Bitlänge plus 5 je Teiler; Profil-Rechnung und Frontier-Diagramm: Zustände je Zelle oder Schicht; Kasteleyn: Kosinusfaktoren; Transfermatrix: (gültige Zeilen)² · (n − 1); Tutte-Frontier: Summe der Zustände mal größte Koeffizientenzahl; Schätzer: Schritte der Sondierungen (bei den Wegen mit Besuchen der Breitensuche) mal Zahl der Sondierungen für 5 Prozent Standardfehler. Die Einheiten sind nur der **Größenordnung** nach vergleichbar.

**Gewinner:** das billigste Verfahren, dessen Ergebnis dem Ganzzahl-Referenzwert (dem Ergebnis des billigsten ganzzahligen Verfahrens) gleicht; ein Verfahren mit anderem Ergebnis ist „falsch“. **Fragen:** Bei den Halsketten die Liste aller Halsketten (nur Aufzählen und FKM liefern sie), bei den Färbungen vier Farbenzahlen k = 2 bis 5 statt einer (k = 3).

## Methodik

- **Prüfungen in der App:** In jeder Zelle laufen alle Verfahren mit demselben Budget; die ganzzahligen müssen dieselbe Zahl geben (sonst Fehler), Kasteleyn wird dagegen geprüft.
- **Eingabe:** Familie (sieben), Größenstufe (1 bis 8, je Familie höchstens so viele wie Größen), Frage (nur bei Halsketten und Färbungen wirksam), Budget (1.000 bis 3.000.000). Die Adresszeile spiegelt die Einstellung.
- **Sechs Experimente:** (1) Wer gewinnt wo (alle 45 Zellen), (2) der Gewinner wechselt mit der Größe, (3) schnell, aber falsch (Kasteleyn), (4) die Frage entscheidet, (5) wo nichts mehr geht und der Schätzer, (6) Regelwerk aus Merkmalen gegen die gemessenen Gewinner. Dazu eine Spielwiese: Aufwandsrechner für Surjektionen (n bis 5.000). Zufall nur im Schätzer, mit festem Seed.

## Befunde (gemessen, keine Behauptungen)

Jede Zahl steht in `tests/test_claims.py`, `tests/test_verdicts.py`, `tests/test_algorithm.py` oder `tests/test_oracle_zvw.py`. Zeiten stehen in keinem Test.

| Frage | Befund |
|---|---|
| Handinstanzen | Binärketten n = 4: 8; Surjektionen 3 auf 2: 6; Halsketten n = 4 mit 3 Farben: 24; Dominosteine 2×2: 2; Wege 2×2: 2; Dreifärbungen 2×2: 18; Teilmengen von {1, 2, 3} mit Summe 3: 2 |
| F1 Binärketten: Aufzählen / Tabelle / Matrixpotenz (Schritte) | n = 10: 375 / 9 / 56; 20: 46.366 / 19 / 64; 30: über / 29 / 80; 100: über / 99 / 88; 1.000: über / 999 / 136 (210 Stellen); 100.000: über / 99.999 / 192 (20.899 Stellen); Gewinner Tabelle, Tabelle, Tabelle, Matrixpotenz, Matrixpotenz, Matrixpotenz |
| F2 Surjektionen: Aufzählen / Stirling-Tabelle / Siebformel / Potenz der EF | (6, 3): 729 / 15 / 20 / 84; (10, 4): über / 34 / 30 / 264; (20, 8): über / 132 / 63 / 1.848; (40, 20): über / 610 / 168 / 17.220; (200, 100): über / 15.050 / 1.111 / über; Gewinner Stirling-Tabelle, dann Siebformel |
| F3 Halsketten: alle Wörter / FKM / Burnside | n = 6: 4.374 / 332 / 28; 12: über / 110.234 / 45; 14: über / 836.410 / 30; 16: über / über / 40; 20, 24, 60: über / über / 48, 64, 102; Gewinner immer Burnside |
| F4 Dominosteine: Aufzählen / Profil / Kasteleyn | 4×4: 146 / 69 / 4; 6×6: 33.094 / 526 / 9; 8×8: über / 3.360 / 16; 10×10: über / 19.359 / 25; 12×12: über / 104.283 / 36 (falsch); 14×14: über / 535.997 / 49 (falsch); 16×16: über / über / 64 (ungeprüft); Gewinner Kasteleyn bis 10×10, Profil-Rechnung bei 12×12 und 14×14, keines bei 16×16 |
| F5 Wege: Aufzählen / Frontier | 3×3: 51 / 54; 4×4: 1.271 / 285; 5×5: 90.111 / 1.246; 6×6: über / 4.926; 7×7: über / 18.271; 8×8: über / 64.993; 9×9: über / 224.462; 10×10: über / 758.682; Gewinner Aufzählen bei 3×3, sonst Frontier-Diagramm |
| F6 Dreifärbungen: Aufzählen / Transfermatrix / Tutte-Frontier | 2×2: 81 / 36 / 35; 3×3: 19.683 / 288 / 1.012; 4×4: über / 1.728 / 18.574; 5×5: über / 9.216 / 245.505; 6×6: über / 46.080 / über; 7×7: über / 221.184 / über; Gewinner Tutte-Frontier (2×2, knapp), sonst Transfermatrix |
| F7 Teilmengen: Aufzählen / Tabelle / Schätzer | n = 16, Gewichte bis 10: 88.049 / 720 / 22.112; n = 20, bis 10: über / 1.160 / 47.586; n = 20, bis 1.000: über / 69.340 / 938.106; n = 24, bis 100.000: über / über / 28.790.400; n = 30, bis 100.000 und n = 40, bis 1.000.000: über / über / nicht bestimmbar |
| Kasteleyn gegen Profil-Rechnung (Schritte Kasteleyn 1, 4, 9, 16, 25, 36, 49, 64 für 2×2 bis 16×16, Profil-Rechnung 6, 69, 526, 3.360, 19.359, 104.283, 535.997, 2.661.721) | 2×2 bis 10×10 gleich (10×10: 258.584.046.368); 12×12: 53.060.477.521.960.000 gegen 53.060.477.521.959.928 (−72); 14×14: 112.202.208.776.036.178.000.000 gegen 112.202.208.776.036.598.939.648 (420.939.648); 16×16: 2.444.888.770.250.892.795.802.079.170.816 gegen 2.444.888.770.250.909.948.854.883.319.808 (17.153.052.804.148.992) |
| Dreifärbungen für k = 2 bis 5: Transfermatrix gegen Tutte | 3×3: 15.688 gegen 1.012; 4×4: 343.932 gegen 18.574; 5×5: 6.982.736 gegen 245.505; 6×6: 135.842.020 gegen 2.586.431 (Faktor 52,5); Werte des 6×6-Gitters: 2, 101.596.896, 380.053.267.505.964, 32.921.147.633.979.091.400; für k = 3 allein: Transfermatrix 46.080, Tutte 2.586.431 (56-mal) |
| Halsketten: Zahl gegen Liste (Burnside / FKM, Faktor) | n = 6: 130 Halsketten, 28 / 332 (12); n = 12: 44.368, 45 / 110.234 (2.450); n = 14: 341.802, 30 / 836.410 (27.880); n = 16: 2.690.844, 40 / 6.507.232 (162.681) |
| Schätzer (5 % Standardfehler) gegen das beste exakte Verfahren | F4 4×4 bis 12×12: 4 / 1.608, 9 / 16.659, 16 / 115.585, 25 / 265.026, 104.283 / 9.376.667; F5 3×3 bis 8×8: 51 / 902, 285 / 30.599, 1.246 / 183.024, 4.926 / 886.267, 18.271 / 2.711.823, 64.993 / 15.029.869; F7 n = 16, 20, 20: 720 / 22.112, 1.160 / 47.586, 69.340 / 938.106; in allen 14 Zellen ist das exakte Verfahren billiger |
| Regelwerk | Version 1: 41 gleich, 2 gleichwertig, 2 verfehlt von 45; Version 2: 42, 2, 1 |
| Spielwiese | Surjektionen n = 40 auf k = 20: Aufzählen rund 10⁵², Stirling-Tabelle 610, Siebformel 168, Potenz der erzeugenden Funktion 17.220 |

## Ehrliche Grenzen

- **Grundschritte sind nur der Größenordnung nach vergleichbar:** jedes Verfahren zählt seine eigene Einheit (Tabelleneintrag, Zustand, Multiplikation, Besuch der Breitensuche). Zellen mit Faktor unter 3 zwischen zwei Verfahren gelten als gleichwertig. Gemessene Zeit kann anders ordnen.
- **Sieben Familien sind gewählt, nicht gezogen:** die Aussage lautet „in diesen Familien“, nie „im Allgemeinen“. Nicht gebaut sind Meet-in-the-middle für die Teilmengensumme, Baumzerlegungen, Parallelisierung und Kasteleyn mit exakter Arithmetik; sie könnten Wendepunkte verschieben.
- **Das Budget ist eine Annahme:** mit mehr Budget rücken die Grenzen (Wege jenseits 10×10, Dreifärbungen 6×6 mit dem Polynom), und der Schätzer bleibt trotzdem in jeder gemessenen Zelle teurer als das beste exakte Verfahren.
- **Das Regelwerk ist angepasst:** Version 1 wurde mit Kenntnis der ersten Messreihe geschrieben (Schwellen für Kasteleyn und Wege kommen daraus), Version 2 passt eine Schwelle nach der Messung an. Beide beschreiben, sie sagen nicht voraus.
- **Literaturwerte aus dem Gedächtnis:** Kasteleyns Formel, Burnside, Tutte-Polynom, Knuths Schätzer; alle durch exakte Gegenrechnung gestützt, nicht aus der Quelle gelesen.
- **Aufwand als Schritte, nicht als Zeit;** der erste Aufruf braucht etwa 40 Sekunden, weil die Tabelle einmal rechnet (danach zwischengespeichert).
- **Browser:** Seitentext, Zahlen, Diagrammbreiten, Preset-Klick im Browser geprüft; Handy-Breite nicht.
- Alles gerechnet, keine echten Daten.

## Verifikation

- **Kern:** Handinstanzen für alle sieben Familien und alle Verfahren; Zähler und Budget; Schrittzahlen von Hand (Tabelle n − 1, Matrixpotenz 8 · (Bitlänge + gesetzte Bits), Siebformel, Stirling-Tabelle, Burnside, Kasteleyn).
- **Orakel:** Binärketten gegen die Fibonacci-Folge; Surjektionen gegen direktes Zählen (n ≤ 7) und über die drei Verfahren bei größeren Zellen; Halsketten gegen direktes Zählen der Bahnen (n ≤ 8); Dominosteine gegen drei Wege (bis 8×8) und gegen die Grenze 2⁵³ für Kasteleyn; Wege gegen Rückverfolgung (n ≤ 5) und die Zahlen aus Stück 13; Färbungen gegen alle drei Verfahren und alle vier Farbenzahlen; Teilmengensumme gegen `itertools.combinations`; Aufwandsformeln gegen nachgezählte Schritte; Schätzer gegen die exakten Werte im 3,5-Fehler-Band.
- **Eigenschaften:** Gewinner hat den kleinsten Aufwand unter den gültigen Verfahren; mehr Budget macht nie aus „exakt“ „über Budget“; gültige Verfahren geben in jeder Zelle denselben Wert; Aufzählen wächst monoton; Gewinner wechselt mit der Größe in fünf Familien; Burnside gewinnt jede Zahl der Halsketten; das Polynom gewinnt die Vierfarben-Frage; der Schätzer ist nie billiger; die Zellen sind deterministisch.
- **Randfälle:** Größenstufe außerhalb, zweite Frage bei anderen Familien (Hinweis), unbekannte Familie und Frage, Budget 1 und 0, Kasteleyn allein (ungeprüft, kein Gewinner), falsches Verfahren erkannt, Liste ohne Burnside, Schätzer ohne Treffer, Aufwandsrechner mit k > n und n = 5.000, Formatierung.
- **Urteilstexte:** genauer Wortlaut für alle Voreinstellungen und Experimente, Fehlerfälle.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), jedes Preset, jede Familie an kleinster und mittlerer Stufe, beide Fragen, Permalink mit Müll, Spielwiese, PDF für jede Familie und beide Fragen, eindeutige Diagrammschlüssel; Footer-Test; Layout-Test.
- **Nicht gemacht:** Mutationstests (seit 2026-10-28 nicht mehr verlangt), Docker-Lauf der Linux-CI (Docker fehlt auf diesem Rechner; die CI nach dem Push entscheidet).

111 Tests (`pytest tests`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, sechs Experimente, Spielwiese, Grenzen, Formeln |
| `zvw_algorithm.py` | Kern: Aufwandszähler, die Verfahren der sieben Familien, Frontier- und Tutte-Rechnung, Schätzer |
| `zvw_constants.py` | Familien, Größenstufen, Budgets, Fragen, Presets |
| `zvw_evaluation.py` | Zellen, Gewinner, Regelwerk, Experimente, Urteilstexte, Formatierung |
| `zvw_layout.py` | Fester Kopf (Stylesheet) |
| `zvw_pdf_export.py` | PDF der aktuellen Zelle (fpdf2) |
| `zvw_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben) |
| `zvw_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handwerte, Orakel, Eigenschaften, Randfälle, Urteilstexte, Claims, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Automatische Auswahl in einem Löser (Algorithm Selection) und Lernen der Auswahl aus Daten:** nur genannt; das Regelwerk ist handgeschrieben.
- **Zeitmessung auf Hardware, Parallelisierung:** die Demo misst Schritte.
- **Meet-in-the-middle, Baumzerlegungen (Härte-Linie), Kasteleyn mit exakter Arithmetik:** nur genannt.
- **Verwandte Demos:** alle fünfzehn Vorgänger (jede Familie verweist auf ihre Stücke), `verfahrensvergleich-demo` (derselbe Aufbau in der Inverse-Linie), `graph-coloring-demo`, `random-spanning-tree-demo`, `branch-bound-demo`, `dynamic-programming-demo`; nur Verweise.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud: Python-Version nach der Voreinstellung der Plattform (lokal `3.14`, CI `3.12`); der Code nutzt nur Merkmale, die in `3.12` laufen.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
