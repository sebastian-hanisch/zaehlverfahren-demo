"""Unabhängige Orakel: jede Zahl gegen mindestens einen zweiten Rechenweg, die Kasteleyn-Grenze gegen 2^53, der Aufwand gegen nachgezählte Schritte."""

import itertools
import math
import random
import statistics

import pytest

import zvw_algorithm as A
import zvw_constants as C
import zvw_evaluation as ev

BIG = 10 ** 8


def value(method, *args):
    status, v, w = A.run(method, BIG, *args)
    assert status == A.EXACT
    return v


def test_f1_methods_against_the_closed_form_fibonacci():
    fib = [0, 1]
    for _ in range(300):
        fib.append(fib[-1] + fib[-2])
    for n in (0, 1, 2, 5, 12, 40, 100, 250):
        assert value(A.f1_table, n) == value(A.f1_matrix, n) == fib[n + 2], n
    for n in range(0, 16):
        assert value(A.f1_brute, n) == fib[n + 2]


def test_f2_methods_against_counting_surjections_directly():
    for n in range(1, 8):
        for k in range(1, n + 1):
            direct = sum(len(set(w)) == k for w in itertools.product(range(k), repeat=n))
            assert value(A.f2_table, n, k) == value(A.f2_sieve, n, k) == value(A.f2_egf, n, k) == direct, (n, k)


def test_f2_larger_cells_agree_across_the_three_exact_methods():
    for n, k in ((20, 8), (40, 20), (30, 5)):
        assert value(A.f2_table, n, k) == value(A.f2_sieve, n, k) == value(A.f2_egf, n, k)


def test_f3_necklaces_against_a_direct_orbit_count_and_burnside_and_fkm():
    for n in range(1, 9):
        words = set()
        for w in itertools.product(range(3), repeat=n):
            words.add(min(w[i:] + w[:i] for i in range(n)))
        assert value(A.f3_brute, n) == len(words) == value(A.f3_fkm, n) == value(A.f3_burnside, n), n


def test_f3_burnside_equals_the_list_length_for_larger_n():
    for n in (10, 12, 14):
        assert value(A.f3_burnside, n) == value(A.f3_fkm, n)


def test_f4_tilings_three_ways_below_the_float_limit():
    for n in (2, 4, 6, 8):
        assert value(A.f4_profile, n) == value(A.f4_kasteleyn, n)
        if n <= 6:
            assert value(A.f4_profile, n) == value(A.f4_brute, n)
    assert [value(A.f4_profile, n) for n in (2, 4, 6, 8, 10)] == [2, 36, 6728, 12988816, 258584046368]
    assert value(A.f4_profile, 3) == 0 == value(A.f4_kasteleyn, 3)


def test_kasteleyn_fails_exactly_where_the_value_exceeds_2_to_the_53():
    for n in (2, 4, 6, 8, 10, 12, 14, 16):
        exact = value(A.f4_profile, n)
        kast = value(A.f4_kasteleyn, n)
        if exact < 2 ** 53:
            assert kast == exact, n
        else:
            assert kast != exact and abs(kast - exact) / exact < 1e-12, n


def test_f5_frontier_against_brute_force_and_known_values():
    for n in (2, 3, 4, 5):
        assert value(A.f5_frontier, n) == value(A.f5_brute, n), n
    assert [value(A.f5_frontier, n) for n in (6, 7, 8)] == [1262816, 575780564, 789360053252]


def test_f6_three_ways_on_small_grids_and_all_four_color_numbers():
    for n in (2, 3):
        brute = value(A.f6_brute, n, (2, 3))
        assert brute == value(A.f6_transfer, n, (2, 3)) == value(A.f6_tutte, n, (2, 3)), n
    for n in (4, 5):
        assert value(A.f6_transfer, n, C.FOUR_COLORS) == value(A.f6_tutte, n, C.FOUR_COLORS), n
    assert value(A.f6_tutte, 3, (2,)) == (2,)     # bipartit: zwei Färbungen


def test_f6_tutte_gives_the_spanning_trees_of_the_same_polynomial():
    poly, _ = A.tutte_frontier(None, 16, A.grid_edges(4, 4))
    assert A.spanning_trees_from_poly(poly) == 100352


def test_f7_methods_against_each_other_and_a_direct_count():
    rng = random.Random(3)
    for _ in range(20):
        ws = [rng.randint(1, 9) for _ in range(rng.randint(1, 12))]
        s = rng.randint(0, sum(ws))
        direct = sum(sum(c) == s for r in range(len(ws) + 1) for c in itertools.combinations(ws, r))
        assert value(A.f7_dp, ws, s) == value(A.f7_brute, ws, s) == direct, (ws, s)


def test_cost_formulas_equal_the_counted_steps():
    for n, k in ((6, 3), (10, 4), (40, 20), (200, 100)):
        assert A.run(A.f2_sieve, BIG, n, k)[2] == A.f2_sieve_cost(n, k)
    for n, k in ((6, 3), (10, 4), (20, 8)):
        assert A.run(A.f2_egf, BIG, n, k)[2] == A.f2_egf_cost(n, k)
    for n in (2, 3, 4):
        for k in (2, 3):
            assert A.run(A.f6_transfer, BIG, n, (k,))[2] == A.f6_transfer_cost(n, k)
    for n in (6, 8, 12):
        assert A.run(A.f4_profile, BIG, n)[2] == sum(len(layer) for layer in profile_layers(n))


def profile_layers(n):
    """Zustände je Zelle der Profil-Rechnung, unabhängig nachgezählt."""
    states = {0}
    out = []
    for pos in range(n * n):
        c = pos % n
        new = set()
        out.append(set(states))
        for mask in states:
            if mask & 1:
                new.add(mask >> 1)
            else:
                if c + 1 < n and not mask & 2:
                    new.add((mask >> 1) | 1)
                if pos + n < n * n:
                    new.add((mask >> 1) | (1 << (n - 1)))
        states = new
    return out


def test_f5_frontier_work_equals_the_known_state_counts_from_stueck_13():
    assert [A.run(A.f5_frontier, BIG, n)[2] for n in (3, 4, 5, 6, 7)] == [54, 285, 1246, 4926, 18271]


def test_f6_tutte_work_equals_the_known_numbers_from_stueck_14():
    states = {3: 46, 4: 251, 5: 1259, 6: 6001}
    for n, total in states.items():
        _, work = A.tutte_frontier(None, n * n, A.grid_edges(n, n))
        assert work % total == 0 and work // total >= 1, n
    assert A.run(A.f6_tutte, 10 ** 7, 6, C.FOUR_COLORS)[2] == 2586431


def test_estimators_stay_inside_their_band_against_the_exact_value():
    est = A.estimator_tilings(6, 4000)
    assert abs(est["Mittel"] - 6728) < 3.5 * 6728 * est["cv"] / 4000 ** 0.5
    est = A.estimator_paths(5, 500)
    assert abs(est["Mittel"] - 8512) < 3.5 * 8512 * est["cv"] / 500 ** 0.5
    ws, s = A.f7_instance(16, 10)
    est = A.estimator_subsets(ws, s, 6000)
    assert abs(est["Mittel"] - 1986) < 3.5 * 1986 * est["cv"] / 6000 ** 0.5


def test_cells_have_only_one_valid_value_per_row():
    for key in C.FAMILY_KEYS:
        for size in C.SIZES[key][:3]:
            cell = ev.compute_cell(key, size, 100000, C.QUESTION_ZAHL, False)
            values = {r["Wert"] for r in cell["methods"] if r["gültig"]}
            assert len(values) <= 1, (key, size)
