"""Eigenschaften (Schicht 2): Gesetze, die für alle Zellen gelten müssen, unabhängig von einzelnen Zahlen."""

import pytest

import zvw_algorithm as A
import zvw_constants as C
import zvw_evaluation as ev

BUDGETS = (1000, 100000, 1000000)


def cells(budget=100000, question=C.QUESTION_ZAHL, keys=C.FAMILY_KEYS):
    return [ev.compute_cell(k, s, budget, question, False) for k in keys for s in C.SIZES[k][:5]]


def test_the_winner_has_the_least_work_among_the_valid_methods():
    for c in cells():
        valid = [r for r in c["methods"] if r["gültig"]]
        if valid:
            assert c["winner_work"] == min(r["Schritte"] for r in valid) and c["winner"] in {r["Verfahren"] for r in valid}
        else:
            assert c["winner"] is None and c["winner_work"] is None


def test_a_larger_budget_never_turns_an_exact_method_into_over_budget():
    for key in C.FAMILY_KEYS:
        size = C.SIZES[key][2]
        small = ev.compute_cell(key, size, 10000, C.QUESTION_ZAHL, False)
        big = ev.compute_cell(key, size, 1000000, C.QUESTION_ZAHL, False)
        for a, b in zip(small["methods"], big["methods"]):
            if a["Status"] == A.EXACT:
                assert b["Status"] == A.EXACT and a["Schritte"] == b["Schritte"] and a["Wert"] == b["Wert"], (key, a["Verfahren"])


def test_valid_methods_agree_on_the_value_in_every_cell():
    for c in cells(1000000):
        assert len({r["Wert"] for r in c["methods"] if r["gültig"]}) <= 1


def test_the_work_of_the_table_and_the_matrix_power_follow_their_formulas():
    for n in (5, 50, 500, 5000):
        assert A.run(A.f1_table, 10 ** 7, n)[2] == n - 1
    ws = [A.run(A.f1_matrix, 10 ** 7, n)[2] for n in (10, 100, 1000, 10000, 100000)]
    assert ws == sorted(ws) and ws[-1] < 300


def test_brute_force_work_grows_with_the_size_until_it_leaves_the_budget():
    for key, method, sizes in (("F4", A.f4_brute, (2, 4, 6)), ("F5", A.f5_brute, (2, 3, 4, 5)), ("F1", A.f1_brute, (5, 10, 15, 20))):
        works = [A.run(method, 10 ** 7, n)[2] for n in sizes]
        assert works == sorted(works) and len(set(works)) == len(works), key


def test_the_winner_changes_with_the_size_in_the_expected_families():
    grid = {k: [ev.compute_cell(k, s, 1000000, C.QUESTION_ZAHL, False)["winner"] for s in C.SIZES[k]] for k in ("F1", "F2", "F4", "F5", "F6")}
    for key, winners in grid.items():
        assert len(set(winners)) >= 2, key


def test_burnside_wins_every_necklace_count_and_fkm_every_list():
    for size in C.SIZES["F3"]:
        assert ev.compute_cell("F3", size, 1000000, C.QUESTION_ZAHL, False)["winner"] == "Burnside"
    for size in C.SIZES["F3"][:4]:
        c = ev.compute_cell("F3", size, 1000000, C.QUESTION_MORE, False)
        assert c["winner"] in ("FKM", "Aufzählen aller Wörter") or c["winner"] is None
        assert [r["Status"] for r in c["methods"] if r["Verfahren"] == "Burnside"] == ["liefert keine Liste"]


def test_the_polynomial_wins_the_four_color_question_and_the_matrix_wins_one_color():
    c4 = ev.compute_cell("F6", 4, 10 ** 7, C.QUESTION_MORE, False)
    assert c4["winner"] == "Tutte-Frontier" and c4["winner_work"] == 18574
    c6 = ev.compute_cell("F6", 6, 3000000, C.QUESTION_MORE, False)
    assert c6["winner"] == "Tutte-Frontier" and [r["Status"] for r in c6["methods"] if r["Verfahren"] == "Transfermatrix"] == [A.OVER]
    for n in (3, 4, 5, 6):
        assert ev.compute_cell("F6", n, 3000000, C.QUESTION_ZAHL, False)["winner"] == "Transfermatrix", n


def test_the_estimator_is_never_cheaper_than_the_best_exact_method_where_both_exist():
    for key, sizes in (("F4", C.EXP_ESTIMATOR_F4), ("F5", C.EXP_ESTIMATOR_F5[:4])):
        for size in sizes:
            c = ev.compute_cell(key, size, 1000000, C.QUESTION_ZAHL)
            assert c["estimator"]["Aufwand"] > c["winner_work"], (key, size)


def test_rule_statuses_cover_every_cell_and_version_two_is_not_worse():
    cs = [ev.compute_cell(k, s, 1000000, C.QUESTION_ZAHL, False) for k in C.FAMILY_KEYS for s in C.SIZES[k]]
    rr = ev.rule_rows(cs)
    assert sum(rr[1]["Zahlen"].values()) == sum(rr[2]["Zahlen"].values()) == len(cs)
    assert rr[2]["Zahlen"]["verfehlt"] <= rr[1]["Zahlen"]["verfehlt"]


def test_surjection_costs_choose_the_sieve_for_large_k_and_the_table_for_small_n():
    assert ev.surjection_costs(6, 3)["Gewinner"] == "Stirling-Tabelle" and ev.surjection_costs(40, 20)["Gewinner"] == "Siebformel" and ev.surjection_costs(200, 100)["Gewinner"] == "Siebformel"
    assert ev.surjection_costs(3, 3)["Gewinner"] in ("Stirling-Tabelle", "Siebformel", "Aufzählen")
    c = ev.surjection_costs(6, 3)["Kosten"]
    assert c["Aufzählen"] == 3 ** 6 and c["Stirling-Tabelle"] == 6 * 3 - 3 and c["Siebformel"] == 4 * (3 + 2)


def test_cell_computation_is_deterministic():
    a = ev.compute_cell("F5", 6, 1000000, C.QUESTION_ZAHL)
    b = ev.compute_cell("F5", 6, 1000000, C.QUESTION_ZAHL)
    assert a == b and a["estimator"]["nötig"] == b["estimator"]["nötig"]
