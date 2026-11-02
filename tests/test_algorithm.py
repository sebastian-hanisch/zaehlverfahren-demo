"""Einheiten des Rechenkerns, jede an einer von Hand gerechneten Mini-Instanz."""

import pytest

import zvw_algorithm as A


def exact(method, *args, budget=10 ** 7):
    status, value, work = A.run(method, budget, *args)
    assert status == A.EXACT, (method.__name__, args)
    return value, work


def test_every_method_gives_the_hand_value_on_the_mini_instances(hand):
    n, v = hand["F1"]
    assert [exact(f, n)[0] for f in (A.f1_brute, A.f1_table, A.f1_matrix)] == [v] * 3
    (n, k), v = hand["F2"]
    assert [exact(f, n, k)[0] for f in (A.f2_brute, A.f2_table, A.f2_sieve, A.f2_egf)] == [v] * 4
    n, v = hand["F3"]
    assert [exact(f, n)[0] for f in (A.f3_brute, A.f3_fkm, A.f3_burnside)] == [v] * 3
    n, v = hand["F4"]
    assert [exact(f, n)[0] for f in (A.f4_brute, A.f4_profile, A.f4_kasteleyn)] == [v] * 3
    n, v = hand["F5"]
    assert [exact(f, n)[0] for f in (A.f5_brute, A.f5_frontier)] == [v] * 2
    n, v = hand["F6"]
    assert [exact(f, n)[0] for f in (A.f6_brute, A.f6_transfer, A.f6_tutte)] == [(v,)] * 3
    (ws, s), v = hand["F7"]
    assert [exact(f, ws, s)[0] for f in (A.f7_brute, A.f7_dp)] == [v] * 2


def test_work_counter_and_budget():
    w = A.Work(5)
    w.add(5)
    with pytest.raises(A.OverBudget):
        w.add()
    assert A.run(A.f1_table, 100, 10) == (A.EXACT, 144, 9)
    assert A.run(A.f1_table, 5, 10) == (A.OVER, None, 5)
    with pytest.raises(ValueError):
        A.Work(0)
    w2 = A.Work(10)
    w2.set(7)
    assert w2.n == 7
    with pytest.raises(A.OverBudget):
        w2.set(11)


def test_step_counts_by_hand():
    assert exact(A.f1_table, 10)[1] == 9 and exact(A.f1_table, 30)[1] == 29 and exact(A.f1_table, 1)[1] == 0
    assert exact(A.f1_matrix, 1)[1] == 24        # Exponent 2: zwei Bits, ein gesetztes: 8 · (2 + 1)
    assert exact(A.f1_matrix, 1000)[1] == 136    # Exponent 1001 = 1111101001: 10 Bits, 7 gesetzt: 8 · 17
    assert exact(A.f2_table, 3, 2)[1] == 5       # S(1,1), S(2,1), S(2,2), S(3,1), S(3,2)
    assert exact(A.f2_sieve, 3, 2)[1] == A.f2_sieve_cost(3, 2) == 3 * (2 + 2)
    assert exact(A.f2_egf, 3, 2)[1] == A.f2_egf_cost(3, 2) == 2 * 10
    assert exact(A.f3_burnside, 4)[1] == (1 + 5) + (2 + 5) + (3 + 5) and exact(A.f3_brute, 4)[1] == 4 * 81
    assert exact(A.f4_kasteleyn, 2)[1] == 1 and exact(A.f4_kasteleyn, 12)[1] == 36
    assert exact(A.f6_transfer, 2)[1] == A.f6_transfer_cost(2, 3) == 6 ** 2 * 1
    assert exact(A.f6_brute, 2)[1] == 81


def test_matrix_power_step_formula():
    for n in (1, 2, 3, 10, 1000, 100000):
        e = n + 1
        assert exact(A.f1_matrix, n)[1] == 8 * (e.bit_length() + bin(e).count("1")), n


def test_known_values_of_larger_cells():
    assert exact(A.f1_table, 30)[0] == 2178309 and exact(A.f1_matrix, 30)[0] == 2178309
    assert exact(A.f2_sieve, 10, 4)[0] == 818520 == exact(A.f2_table, 10, 4)[0]
    assert exact(A.f3_burnside, 12)[0] == 44368 and exact(A.f3_fkm, 12)[0] == 44368
    assert exact(A.f4_profile, 8)[0] == 12988816 == exact(A.f4_kasteleyn, 8)[0]
    assert exact(A.f5_frontier, 6) == (1262816, 4926) and exact(A.f5_frontier, 4) == (184, 285)
    assert exact(A.f6_transfer, 5)[0] == exact(A.f6_tutte, 5)[0] == (580986,)


def test_frontier_and_tutte_helpers():
    poly, work = A.tutte_frontier(None, 3, A.grid_edges(1, 3))
    assert poly == {(2, 0): 1} and A.spanning_trees_from_poly(poly) == 1      # Weg mit drei Knoten: T = x²
    tri, _ = A.tutte_frontier(None, 3, [(0, 1), (1, 2), (0, 2)])
    assert tri == {(2, 0): 1, (1, 0): 1, (0, 1): 1} and A.chromatic_values(tri, 3, (2, 3, 4)) == (0, 6, 24)
    assert A.grid_edges(2, 2) == [(0, 1), (0, 2), (1, 3), (2, 3)]


def test_instances_and_estimators_are_deterministic():
    ws, s = A.f7_instance(16, 10)
    assert (len(ws), s) == (16, 44) and A.f7_instance(16, 10) == (ws, s) and A.f7_instance(16, 11) != (ws, s)
    assert A.estimator_tilings(4) == A.estimator_tilings(4) and A.estimator_subsets(ws, s)["nötig"] == 1382
    est = A.estimator_tilings(4)
    assert est["nötig"] == 201 and est["Aufwand"] == 1608.0


def test_guards():
    assert A.run(A.f1_brute, 10 ** 9, 101)[0] == A.OVER
    assert A.run(A.f2_brute, 1000, 10, 4)[0] == A.OVER          # 4^10 = 1.048.576 > 1000
    assert A.run(A.f3_brute, 1000, 10)[0] == A.OVER
    with pytest.raises(ValueError):
        A.f5_frontier(A.Work(10), 1)
