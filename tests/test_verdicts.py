"""Urteilstexte (Schicht 3): die Texte, die die App zeigt, mit genauem Wortlaut für alle Voreinstellungen und Experimente, damit jede Zahl darin geprüft ist."""

import zvw_constants as C
import zvw_evaluation as ev

S = ev.Settings


def answer(name):
    return ev.verdict_answers(ev.analyse(S(**C.PRESETS[name])))


def test_answer_standard_case_exact():
    assert answer("Standardfall: Dominosteine 12×12 (Kasteleyn falsch)") == ("warning",
        "Dominosteine im n×n-Brett, 12×12, Budget 1.000.000 Schritte: Gewinner ist Profil-Rechnung mit 104.283 Schritten. Ergebnis: 53.060.477.521.960.000. Über dem Budget: Aufzählen. "
        "Kasteleyn wäre schneller (36 Schritte), liefert aber 53.060.477.521.959.928 statt 53.060.477.521.960.000: falsch (Gleitkomma). "
        "Der Schätzer kostet für 5 % Standardfehler etwa 9.376.667 Schritte: 89,9-mal so viel wie der Gewinner. Das Regelwerk empfiehlt Profil-Rechnung: gleich.")


def test_answer_chains_paths_and_colors_exact():
    assert answer("Binärketten: Wechsel von der Tabelle zur Matrixpotenz") == ("success",
        "Binärketten ohne zwei Einsen hintereinander, n = 1.000, Budget 300.000 Schritte: Gewinner ist Matrixpotenz mit 136 Schritten. Ergebnis: 1,13·10²⁰⁹ (210 Stellen). "
        "Zweiter ist Tabelle mit dem 7,3-Fachen. Über dem Budget: Aufzählen. Das Regelwerk empfiehlt Tabelle: verfehlt.")
    assert answer("Wege im 8×8-Gitter: das Frontier-Diagramm gewinnt") == ("success",
        "Einfache Wege im n×n-Gitter, 8×8, Budget 1.000.000 Schritte: Gewinner ist Frontier-Diagramm mit 64.993 Schritten. Ergebnis: 789.360.053.252. Über dem Budget: Aufzählen. "
        "Der Schätzer kostet für 5 % Standardfehler etwa 15.029.869 Schritte: 231,3-mal so viel wie der Gewinner. Das Regelwerk empfiehlt Frontier-Diagramm: gleich.")
    assert answer("Dreifärbungen 6×6, vier Farbenzahlen: das Polynom gewinnt") == ("success",
        "Dreifärbungen des n×n-Gitters, 6×6, Budget 3.000.000 Schritte: Gewinner ist Tutte-Frontier mit 2.586.431 Schritten. Ergebnis: 2, 101.596.896, 380.053.267.505.964, 32.921.147.633.979.091.400. "
        "Über dem Budget: Aufzählen, Transfermatrix. Das Regelwerk empfiehlt Tutte-Frontier: gleich.")


def test_answer_necklaces_and_subsets_exact():
    assert answer("Halsketten n = 14 als Liste: FKM statt Burnside") == ("success",
        "Halsketten mit 3 Farben, n = 14 Perlen, Budget 1.000.000 Schritte: Gewinner ist FKM mit 836.410 Schritten. Ergebnis: 341.802. Über dem Budget: Aufzählen aller Wörter. Das Regelwerk empfiehlt FKM: gleich.")
    assert answer("Teilmengensumme n = 24: nichts geht mehr") == ("warning",
        "Teilmengen mit halber Gesamtsumme, n = 24 Gegenstände, Gewichte bis 100.000, Budget 1.000.000 Schritte: kein Verfahren liefert innerhalb des Budgets ein geprüftes Ergebnis (über dem Budget: Aufzählen, Tabelle (EF)). "
        "Der Schätzer bräuchte für 5 % Standardfehler 1.199.600 Sondierungen mit etwa 28.790.400 Schritten.")


def test_method_table_of_the_standard_case():
    a = ev.analyse(S(**C.PRESETS["Standardfall: Dominosteine 12×12 (Kasteleyn falsch)"]))
    assert ev.method_rows(a) == [
        {"Verfahren": "Aufzählen", "Ausgabe": "Liste", "Status": "über Budget", "Ergebnis": "–", "Schritte": "mehr als 1.000.000", "Hinweis": ""},
        {"Verfahren": "Profil-Rechnung", "Ausgabe": "Zahl", "Status": "exakt", "Ergebnis": "53.060.477.521.960.000", "Schritte": "104.283", "Hinweis": "Gewinner"},
        {"Verfahren": "Kasteleyn", "Ausgabe": "Zahl", "Status": "falsch", "Ergebnis": "53.060.477.521.959.928", "Schritte": "36", "Hinweis": "weicht von 53.060.477.521.960.000 ab"},
        {"Verfahren": "Schätzer (5 % Standardfehler)", "Ausgabe": "Schätzung", "Status": "geschätzt", "Ergebnis": "Variationskoeffizient 18,12", "Schritte": "9.376.667", "Hinweis": "131.405 Sondierungen"}]


def test_error_text_when_the_integer_methods_disagree():
    a = ev.analyse(S(**C.PRESETS["Standardfall: Dominosteine 12×12 (Kasteleyn falsch)"]))
    a.problems.append("zwei Verfahren weichen ab")
    assert ev.verdict_answers(a) == ("error", "Die Rechenwege widersprechen sich: zwei Verfahren weichen ab")


def test_grid_and_switch_verdicts_exact():
    cells = ev.grid_cells()
    assert ev.verdict_grid(cells) == ("success",
        "In 45 Zellen aus 7 Familien (Budget 1.000.000 Schritte) gewinnen 12 verschiedene Bezeichnungen (etwa sieben Grundideen); in 4 Zellen gewinnt keines. "
        "In 5 von 7 Familien wechselt der Gewinner zwischen zwei Verfahren (F1, F2, F4, F5, F6); in 1 weiteren (F7) fällt er irgendwann weg. In diesen 7 Familien gibt es kein Verfahren, das überall gewinnt, nur eines, das zu Struktur, Frage und Größe passt.")
    assert ev.verdict_switch(cells) == ("success",
        "Der Gewinner wechselt an 7 Stellen: F1: von n = 30 (Tabelle) zu n = 100 (Matrixpotenz); F2: von n = 6, k = 3 (Stirling-Tabelle) zu n = 10, k = 4 (Siebformel); F4: von 10×10 (Kasteleyn) zu 12×12 (Profil-Rechnung); "
        "F4: von 14×14 (Profil-Rechnung) zu 16×16 (keines); F5: von 3×3 (Aufzählen) zu 4×4 (Frontier-Diagramm); F6: von 2×2 (Tutte-Frontier) zu 3×3 (Transfermatrix); "
        "F7: von n = 20 Gegenstände, Gewichte bis 1.000 (Tabelle (EF)) zu n = 24 Gegenstände, Gewichte bis 100.000 (keines).")


def test_kasteleyn_and_question_verdicts_exact():
    assert ev.verdict_kasteleyn(ev.kasteleyn_rows()) == ("success",
        "Kasteleyns Kosinusprodukt in Gleitkomma stimmt bis 10×10 und ist ab 12×12 falsch: 53.060.477.521.959.928 statt 53.060.477.521.960.000 (Abweichung −72; der Wert liegt über 2⁵³ = 9.007.199.254.740.992). "
        "Beim 16×16-Brett beträgt die Abweichung 17.153.052.804.148.992. Dafür braucht die Formel 36 bis 64 Schritte gegen 104.283 bis 2.661.721 der Profil-Rechnung: schneller, aber nur richtig, wo sie stimmt.")
    assert ev.verdict_question(ev.question_rows()) == ("success",
        "Dreifärbungen des 6×6-Gitters: für einen Wert kostet die Transfermatrix 46.080 Schritte, das Tutte-Polynom 2.586.431 (56-mal so viel); für die vier Farbenzahlen 2 bis 5 braucht die Transfermatrix zusammen 135.842.020, "
        "das Polynom einmal 2.586.431: Faktor 52,5 zugunsten des Polynoms, und es liefert dazu Spannbäume und die Zuverlässigkeit. "
        "Halsketten: die Zahl 2.690.844 (n = 16) kostet Burnside 40 Schritte, die Liste aller Halsketten FKM 6.507.232 (Faktor 162.681).")


def test_estimator_and_rule_verdicts_exact():
    cells = ev.grid_cells()
    assert ev.verdict_estimator(ev.estimator_rows(cells)) == ("success",
        "In allen 14 Zellen, in denen ein exaktes Verfahren im Budget liegt und der Schätzer bestimmbar ist, ist das beste exakte Verfahren billiger (am deutlichsten bei F4 10×10: 25 gegen 265.026 Schritte). "
        "In 3 Zellen liegt kein exaktes Verfahren im Budget; dort ist der Schätzer entweder nicht bestimmbar (2 Zellen) oder braucht mehr als das Budget.")
    assert ev.verdict_rules(ev.rule_rows(cells)) == ("success",
        "Das Regelwerk aus Merkmalen (Version 1, mit Kenntnis der ersten Messreihe geschrieben) beschreibt 41 von 45 Gewinnern gleich, 2 gleichwertig, 2 verfehlt (F1 n = 1.000: Gewinner Matrixpotenz, Regel Tabelle; F4 16×16: Gewinner keines, Regel Profil-Rechnung). "
        "Version 2 (Schwelle nach der Messung angepasst): 42 gleich, 2 gleichwertig, 1 verfehlt: angepasst, nicht vorhergesagt.")


def test_play_verdict_exact():
    assert ev.verdict_play(ev.surjection_costs(40, 20)) == ("success",
        "Surjektionen von 40 Elementen auf 20: Aufzählen rund 10^52 Schritte, Stirling-Tabelle 610, Siebformel 168, Potenz der erzeugenden Funktion 17.220. Gewinner nach dem Aufwandsmaß: Siebformel.")
    assert ev.verdict_play(ev.surjection_costs(6, 3))[1].startswith("Surjektionen von 6 Elementen auf 3: Aufzählen 729 Schritte, Stirling-Tabelle 15, Siebformel 20, Potenz der erzeugenden Funktion 84.")


def test_verdicts_turn_into_errors_when_a_check_fails():
    only_burnside = [c for c in ev.grid_cells() if c["key"] == "F3"]
    assert ev.verdict_grid(only_burnside)[0] == "error"   # ein einziger Gewinner: die Aussage „kein bestes Verfahren“ wäre nicht belegt
    rows = [dict(r) for r in ev.kasteleyn_rows()]
    for r in rows:
        r["Abweichung"] = 0
    assert ev.verdict_kasteleyn(rows)[0] == "error"
    est = [dict(r) for r in ev.estimator_rows(ev.grid_cells())]
    est[0]["Schätzer"] = 1
    assert ev.verdict_estimator(est)[0] == "error"
