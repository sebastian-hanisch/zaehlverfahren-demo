"""Randfälle: Klemmen der Eingaben, Hinweise, Fehler bei unbekannten Werten, Budget 1, ungeprüfte Gleitkomma-Verfahren, Spielwiese."""

import pytest

import zvw_algorithm as A
import zvw_constants as C
import zvw_evaluation as ev

S = ev.Settings
F = C.FAMILY_LABELS


def settings(family="F4", stage=3, budget=100000, question=C.QUESTION_ZAHL):
    return S(f"{family}: {C.FAMILY_NAMES[family]}", stage, budget, question)


def test_stage_is_clamped_to_the_number_of_stages_with_a_note():
    a = ev.analyse(settings("F2", stage=8))
    assert a.size_label == "n = 200, k = 100" and any("5 Größenstufen" in n for n in a.notes)
    b = ev.analyse(settings("F4", stage=0))
    assert b.size_label == "4×4"


def test_second_question_note_for_other_families_and_no_effect():
    a = ev.analyse(settings("F1", question=C.QUESTION_MORE))
    assert any("nur bei den Halsketten" in n for n in a.notes) and a.question == C.QUESTION_ZAHL
    b = ev.analyse(settings("F3", question=C.QUESTION_MORE))
    assert b.notes == [] and b.question == C.QUESTION_MORE


def test_unknown_family_question_and_budget_raise():
    with pytest.raises(ValueError):
        ev.analyse(S("Zauber", 3, 1000, C.QUESTION_ZAHL))
    with pytest.raises(ValueError):
        ev.analyse(S(F[0], 3, 1000, "Frage"))
    with pytest.raises(ValueError):
        ev.analyse(S(F[0], 3, 0, C.QUESTION_ZAHL))
    with pytest.raises(ValueError):
        ev.compute_cell("F9", 3, 1000, C.QUESTION_ZAHL)


def test_budget_one_leaves_every_method_over_budget_with_no_winner():
    for key in C.FAMILY_KEYS:
        c = ev.compute_cell(key, C.SIZES[key][0], 1, C.QUESTION_ZAHL, False)
        assert c["winner"] is None and all(r["Status"] in (A.OVER, "exakt, ungeprüft") or r["Verfahren"] in C.FLOAT_METHODS for r in c["methods"]), key


def test_kasteleyn_alone_is_unchecked_and_cannot_win():
    c = ev.compute_cell("F4", 16, 1000, C.QUESTION_ZAHL, False)
    assert c["winner"] is None
    kast = next(r for r in c["methods"] if r["Verfahren"] == "Kasteleyn")
    assert kast["Status"] == "exakt, ungeprüft" and not kast["gültig"]
    a = ev.analyse(settings("F4", stage=7, budget=1000))
    assert ev.verdict_answers(a)[0] == "warning" and "kein Verfahren liefert innerhalb des Budgets ein geprüftes Ergebnis" in ev.verdict_answers(a)[1]
    assert any(r["Hinweis"].startswith("kein ganzzahliges Verfahren") for r in ev.method_rows(a))


def test_wrong_method_is_flagged_and_excluded():
    c = ev.compute_cell("F4", 12, 1000000, C.QUESTION_ZAHL, False)
    kast = next(r for r in c["methods"] if r["Verfahren"] == "Kasteleyn")
    assert kast["Status"] == "falsch" and kast["Wert"] == 53060477521959928 and c["value"] == 53060477521960000 and c["winner"] == "Profil-Rechnung"


def test_list_question_excludes_burnside_and_four_colors_change_the_values():
    c = ev.compute_cell("F3", 14, 1000000, C.QUESTION_MORE, False)
    assert c["winner"] == "FKM" and c["value"] == 341802
    f = ev.compute_cell("F6", 3, 1000000, C.QUESTION_MORE, False)
    assert f["value"] == (2, 246, 9612, 142820)


def test_no_winner_text_and_estimator_sentences():
    a = ev.analyse(settings("F7", stage=4, budget=1000000))
    kind, text = ev.verdict_answers(a)
    assert kind == "warning" and "Der Schätzer bräuchte für 5 % Standardfehler 1.199.600 Sondierungen" in text
    b = ev.analyse(settings("F7", stage=5, budget=1000000))
    assert "Der Schätzer trifft keine Lösung" in ev.verdict_answers(b)[1]
    assert any(r["Ergebnis"] == "keine Sondierung trifft" for r in ev.method_rows(b))


def test_float_methods_never_win_without_matching_value():
    for size in C.SIZES["F4"]:
        c = ev.compute_cell("F4", size, 1000000, C.QUESTION_ZAHL, False)
        if c["winner"] == "Kasteleyn":
            assert c["value"] == A.run(A.f4_kasteleyn, 10 ** 6, size)[1]


def test_surjection_calculator_validation_and_large_inputs():
    with pytest.raises(ValueError):
        ev.surjection_costs(5, 6)
    with pytest.raises(ValueError):
        ev.surjection_costs(0, 0)
    with pytest.raises(ValueError):
        ev.surjection_costs(C.PLAY_N_MAX + 1, 3)
    big = ev.surjection_costs(5000, 2500)
    assert big["Kosten"]["Aufzählen"] is None and big["Gewinner"] == "Siebformel"
    kind, text = ev.verdict_play(big)
    assert kind == "success" and "mehr als 10^600" in text
    mid = ev.surjection_costs(700, 5)
    assert mid["Kosten"]["Aufzählen"].bit_length() > 1000 and "rund 10^" in ev.verdict_play(mid)[1]


def test_formatting_helpers():
    assert ev.de(1.5, 2) == "1,50" and ev.de(-0.25, 1) == "−0,2"
    assert ev.big_text(999999999999999) == "999.999.999.999.999" and ev.big_text(10 ** 15) == "1,00·10¹⁵ (16 Stellen)" and ev.big_text(-1234) == "−1.234"
    assert ev.full_text(53060477521960000) == "53.060.477.521.960.000" and ev.full_text(-72) == "−72"
    assert ev.value_text(None) == "–" and ev.value_text((2, 246)) == "2, 246" and ev.value_text(10 ** 50).startswith("1,00·10⁵⁰")
    assert ev.work_text(1496.0) == "1.496" and ev.work_text(float("inf")) == "–"
    assert ev.plural(1, "Schritt", "Schritte") == "1 Schritt" and ev.plural(1000, "Schritt", "Schritte") == "1.000 Schritte"
    assert ev.big_text(10 ** 6000).startswith("rund 6001")
