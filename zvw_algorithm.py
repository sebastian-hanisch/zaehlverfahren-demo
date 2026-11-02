"""Rechenkern: sieben Familien von Zählaufgaben, je mehrere Verfahren aus den Stücken 1 bis 15 mit demselben Aufwandsmaß (Zahl der Grundschritte mit Obergrenze), plus Schätzer für den Aufwand-Vergleich.

Jedes Verfahren bekommt einen Zähler `Work` und wirft `OverBudget`, wenn er die Obergrenze überschreitet; `run` macht daraus ein Ergebnis (Status, Wert, Schritte).
Die Einheit „Schritt“ ist je Verfahren festgelegt (siehe Docstrings) und nur der Größenordnung nach vergleichbar. Alles mit `int` und `Fraction`; Zufall nur über feste Seeds."""

from __future__ import annotations

import itertools
import math
import random
import statistics
from fractions import Fraction

SEED = 20261102
EXACT, OVER = "exakt", "über Budget"


class OverBudget(Exception):
    """Das Verfahren hat die Obergrenze an Grundschritten überschritten."""


class Work:
    def __init__(self, budget: int):
        if budget < 1:
            raise ValueError("Das Budget muss mindestens 1 Schritt betragen.")
        self.n, self.budget = 0, budget

    def add(self, k: int = 1):
        self.n += k
        if self.n > self.budget:
            raise OverBudget

    def set(self, value: int):
        """Aufwand als Ganzes setzen (für Verfahren, die ihn erst am Ende kennen)."""
        self.n = value
        if self.n > self.budget:
            raise OverBudget


def run(method, budget: int, *args) -> tuple:
    """(Status, Ergebnis oder None, Schritte); bei Überschreitung ist Schritte gleich dem Budget."""
    w = Work(budget)
    try:
        return EXACT, method(w, *args), w.n
    except OverBudget:
        return OVER, None, budget


# ---------------------------------------------------------------- F1: Binärketten ohne zwei Einsen hintereinander
def f1_brute(w: Work, n: int) -> int:
    """Aufzählen: ein Schritt je besuchtem Knoten des Suchbaums der gültigen Präfixe."""
    if n > 100:
        raise OverBudget   # Knotenzahl wächst wie 1,6^n; die Rekursionstiefe des Aufzählens reicht nicht
    count = 0

    def rec(length, last):
        nonlocal count
        w.add()
        if length == n:
            count += 1
            return
        rec(length + 1, 0)
        if not last:
            rec(length + 1, 1)

    rec(0, 0)
    return count


def f1_table(w: Work, n: int) -> int:
    """Rekursion a(n) = a(n−1) + a(n−2) mit Tabelle: ein Schritt je Eintrag."""
    if n == 0:
        return 1
    a, b = 1, 2
    for _ in range(n - 1):
        w.add()
        a, b = b, a + b
    return b


def f1_matrix(w: Work, n: int) -> int:
    """Transfermatrix [[1,1],[1,0]] hoch n + 1 durch wiederholtes Quadrieren: acht Multiplikationen je 2×2-Produkt."""
    def mul(x, y):
        w.add(8)
        return [[x[0][0] * y[0][0] + x[0][1] * y[1][0], x[0][0] * y[0][1] + x[0][1] * y[1][1]], [x[1][0] * y[0][0] + x[1][1] * y[1][0], x[1][0] * y[0][1] + x[1][1] * y[1][1]]]

    result, base, e = [[1, 0], [0, 1]], [[1, 1], [1, 0]], n + 1
    while e:
        if e & 1:
            result = mul(result, base)
        base = mul(base, base)
        e >>= 1
    return result[0][0]


# ---------------------------------------------------------------- F2: Surjektionen von n Elementen auf k
def f2_brute(w: Work, n: int, k: int) -> int:
    """Aufzählen aller k^n Abbildungen: ein Schritt je Abbildung."""
    if k ** n > w.budget:
        raise OverBudget
    count = 0
    for word in itertools.product(range(k), repeat=n):
        w.add()
        count += len(set(word)) == k
    return count


def f2_table(w: Work, n: int, k: int) -> int:
    """Stirling-Tabelle S(i, j), mal k!: ein Schritt je Eintrag."""
    s = [[0] * (k + 1) for _ in range(n + 1)]
    s[0][0] = 1
    for i in range(1, n + 1):
        for j in range(1, min(i, k) + 1):
            w.add()
            s[i][j] = j * s[i - 1][j] + s[i - 1][j - 1]
    return s[n][k] * math.factorial(k)


def f2_sieve_cost(n: int, k: int) -> int:
    """Aufwand der Siebformel: (k + 1) Potenzen, je Potenz Bitlänge von n plus gesetzte Bits Multiplikationen."""
    return (k + 1) * (n.bit_length() + bin(n).count("1"))


def f2_sieve(w: Work, n: int, k: int) -> int:
    total = 0
    for j in range(k + 1):
        w.add(n.bit_length() + bin(n).count("1"))
        total += (-1) ** j * math.comb(k, j) * (k - j) ** n
    return total


def f2_egf_cost(n: int, k: int) -> int:
    """Aufwand der k-fachen Potenz der Reihe e^z − 1 bis z^n: je Faktor (n + 1)(n + 2)/2 Multiplikationen und Additionen."""
    return k * ((n + 1) * (n + 2) // 2)


def f2_egf(w: Work, n: int, k: int) -> int:
    base = [Fraction(0)] + [Fraction(1, math.factorial(i)) for i in range(1, n + 1)]
    result = [Fraction(1)] + [Fraction(0)] * n
    for _ in range(k):
        w.add((n + 1) * (n + 2) // 2)
        new = [Fraction(0)] * (n + 1)
        for i, a in enumerate(result):
            if a:
                for j in range(1, n + 1 - i):
                    new[i + j] += a * base[j]
        result = new
    return int(result[n] * math.factorial(n))


# ---------------------------------------------------------------- F3: Halsketten mit 3 Farben
def f3_brute(w: Work, n: int, k: int = 3) -> int:
    """Alle k^n Wörter, je auf die kleinste Drehung gebracht: n Schritte je Wort."""
    if n * k ** n > w.budget:
        raise OverBudget
    seen = set()
    for word in itertools.product(range(k), repeat=n):
        w.add(n)
        seen.add(min(word[i:] + word[:i] for i in range(n)))
    return len(seen)


def f3_fkm(w: Work, n: int, k: int = 3) -> int:
    """FKM-Rekursion (Stück 12): ein Schritt je Rekursionsaufruf; sie gibt jede Halskette einmal aus (liefert die Liste)."""
    a = [0] * (n + 1)
    count = 0

    def gen(t, p):
        nonlocal count
        w.add()
        if t > n:
            if n % p == 0:
                count += 1
            return
        a[t] = a[t - p]
        gen(t + 1, p)
        for j in range(a[t - p] + 1, k):
            a[t] = j
            gen(t + 1, t)

    gen(1, 1)
    return count


def _phi(m: int) -> int:
    return sum(1 for i in range(1, m + 1) if math.gcd(i, m) == 1)


def f3_burnside(w: Work, n: int, k: int = 3) -> int:
    """Burnside: Summe über die Teiler d von n; je Teiler Bitlänge von d plus 5 Schritte."""
    total = 0
    for d in range(1, n + 1):
        if n % d == 0:
            w.add(d.bit_length() + 5)
            total += _phi(n // d) * k ** d
    return total // n


# ---------------------------------------------------------------- F4: Dominosteine im n×n-Brett
def f4_brute(w: Work, n: int) -> int:
    """Aufzählen durch Rückverfolgung: ein Schritt je besuchtem Knoten."""
    covered = [False] * (n * n)
    count = 0

    def rec(pos):
        nonlocal count
        w.add()
        while pos < n * n and covered[pos]:
            pos += 1
        if pos == n * n:
            count += 1
            return
        r, c = divmod(pos, n)
        if c + 1 < n and not covered[pos + 1]:
            covered[pos] = covered[pos + 1] = True
            rec(pos + 1)
            covered[pos] = covered[pos + 1] = False
        if r + 1 < n:
            covered[pos] = covered[pos + n] = True
            rec(pos + 1)
            covered[pos] = covered[pos + n] = False

    rec(0)
    return count


def f4_profile(w: Work, n: int) -> int:
    """Zellenweise Profil-Rechnung (die Frontier-Methode für Dominosteine): Zustand = Bitmaske der nächsten n Zellen; ein Schritt je Zustand und Zelle."""
    states = {0: 1}
    for pos in range(n * n):
        c = pos % n
        new: dict = {}
        for mask, cnt in states.items():
            w.add()
            if mask & 1:
                nm = mask >> 1
                new[nm] = new.get(nm, 0) + cnt
            else:
                if c + 1 < n and not mask & 2:
                    nm = (mask >> 1) | 1
                    new[nm] = new.get(nm, 0) + cnt
                if pos + n < n * n:
                    nm = (mask >> 1) | (1 << (n - 1))
                    new[nm] = new.get(nm, 0) + cnt
        states = new
    return states.get(0, 0)


def f4_kasteleyn(w: Work, n: int) -> int:
    """Kasteleyns Kosinusprodukt in Gleitkomma (double), auf die nächste ganze Zahl gerundet: ein Schritt je Faktor. Ab Werten über 2^53 nicht mehr exakt."""
    prod = 1.0
    for j in range(1, n // 2 + 1):
        for k in range(1, n // 2 + 1):
            w.add()
            prod *= 4 * math.cos(math.pi * j / (n + 1)) ** 2 + 4 * math.cos(math.pi * k / (n + 1)) ** 2
    return round(prod) if n % 2 == 0 else 0


# ---------------------------------------------------------------- F5: einfache Wege im n×n-Gitter
def grid_neighbor_lists(n: int) -> list:
    out = []
    for v in range(n * n):
        r, c = divmod(v, n)
        out.append([(r + dr) * n + c + dc for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)) if 0 <= r + dr < n and 0 <= c + dc < n])
    return out


def f5_brute(w: Work, n: int) -> int:
    """Aufzählen aller einfachen Wege von Ecke zu Ecke durch Rückverfolgung: ein Schritt je besuchtem Knoten."""
    nb = grid_neighbor_lists(n)
    target = n * n - 1

    def rec(v, visited):
        w.add()
        if v == target:
            return 1
        return sum(rec(u, visited | 1 << u) for u in nb[v] if not visited >> u & 1)

    return rec(0, 1)


def grid_edges(rows: int, cols: int) -> list:
    right = lambda r, c: (r * cols + c, r * cols + c + 1)
    down = lambda r, c: (r * cols + c, (r + 1) * cols + c)
    return [e for r in range(rows) for c in range(cols) for e in ((right(r, c),) if c + 1 < cols else ()) + ((down(r, c),) if r + 1 < rows else ())]


DONE, S_MARK, T_MARK, S_UNUSED, T_UNUSED = -1, -2, -3, -4, -5
FIN = ("fin",)


def _frontier_info(edges: list) -> tuple:
    first, last = {}, {}
    for i, (a, b) in enumerate(edges):
        for x in (a, b):
            first.setdefault(x, i)
            last[x] = i
    enter = [[x for x in (a, b) if first[x] == i] for i, (a, b) in enumerate(edges)]
    leave = [[x for x in (a, b) if last[x] == i] for i, (a, b) in enumerate(edges)]
    return enter, leave


def _path_step(edges: list, s: int, t: int):
    """Schritt der Frontier-Methode für einfache Wege von s nach t (Zustand: Partner jedes Frontier-Knotens, Simpath)."""
    enter, leave = _frontier_info(edges)
    last_edge = len(edges) - 1

    def step(state, i, inc):
        if state == FIN:
            return "reject" if inc else ("accept" if i == last_edge else FIN)
        mate = dict(state)
        for x in enter[i]:
            mate[x] = S_UNUSED if x == s else T_UNUSED if x == t else x
        u, v = edges[i]
        done_path = False
        if inc:
            if mate[u] == DONE or mate[v] == DONE:
                return "reject"

            def far(x):
                m = mate[x]
                return S_MARK if m == S_UNUSED else T_MARK if m == T_UNUSED else m

            fu, fv = far(u), far(v)
            if fu == v or fv == u:
                return "reject"
            if {fu, fv} == {S_MARK, T_MARK}:
                for x, m in mate.items():
                    if x not in (u, v) and m not in (x, DONE):
                        return "reject"
                done_path = True
                mate = dict(mate)
                mate[u] = DONE
                mate[v] = DONE
            else:
                new = dict(mate)
                if fu >= 0:
                    new[fu] = fv
                if fv >= 0:
                    new[fv] = fu
                if mate[u] != u:
                    new[u] = DONE
                if mate[v] != v:
                    new[v] = DONE
                mate = new
        for x in leave[i]:
            m = mate[x]
            if m not in (x, DONE):
                return "reject"
            del mate[x]
        if done_path:
            return "accept" if i == last_edge else FIN
        if i == last_edge:
            return "reject"
        return tuple(sorted(mate.items()))

    return step


def f5_frontier(w: Work, n: int) -> int:
    """Frontier-Methode (Stück 13): ein Schritt je Zustand je Schicht (einschließlich der Wurzelschicht), gezählt wird vorwärts mit der Zahl der Teilauswahlen je Zustand."""
    if n < 2:
        raise ValueError("Das Gitter braucht mindestens 2×2 Knoten.")
    edges = grid_edges(n, n)
    step = _path_step(edges, 0, n * n - 1)
    states = {(): 1}
    total = 0
    w.add(1)
    for i in range(len(edges)):
        nxt: dict = {}
        for state, cnt in states.items():
            for inc in (0, 1):
                ns = step(state, i, inc)
                if ns == "accept":
                    total += cnt
                elif ns != "reject":
                    nxt[ns] = nxt.get(ns, 0) + cnt
        states = nxt
        w.add(len(states))
    return total


# ---------------------------------------------------------------- F6: Dreifärbungen des n×n-Gitters
def f6_brute(w: Work, n: int, ks: tuple = (3,)) -> tuple:
    """Zählen aller k^(n²) Färbungen für jede Farbenzahl: ein Schritt je Färbung."""
    edges = grid_edges(n, n)
    out = []
    for k in ks:
        if k ** (n * n) + w.n > w.budget:
            raise OverBudget
        w.add(k ** (n * n))
        out.append(sum(all(col[a] != col[b] for a, b in edges) for col in itertools.product(range(k), repeat=n * n)))
    return tuple(out)


def f6_transfer_cost(n: int, k: int) -> int:
    """Zeilen-Transfermatrix: (gültige Zeilen)² · (n − 1) Vergleiche."""
    return (k * (k - 1) ** (n - 1)) ** 2 * (n - 1)


def f6_transfer(w: Work, n: int, ks: tuple = (3,)) -> tuple:
    out = []
    for k in ks:
        w.add(f6_transfer_cost(n, k))      # vor der Rechnung zählen: bei Überschreitung wird nicht gerechnet
        rows = [r for r in itertools.product(range(k), repeat=n) if all(r[i] != r[i + 1] for i in range(n - 1))]
        vec = {r: 1 for r in rows}
        for _ in range(n - 1):
            vec = {r2: sum(c for r1, c in vec.items() if all(a != b for a, b in zip(r1, r2))) for r2 in rows}
        out.append(sum(vec.values()))
    return tuple(out)


def _padd(a: dict, b: dict) -> dict:
    out = dict(a)
    for key, v in b.items():
        out[key] = out.get(key, 0) + v
        if out[key] == 0:
            del out[key]
    return out


def _pmul(a: dict, b: dict) -> dict:
    out: dict = {}
    for (i, j), v in a.items():
        for (k, l), x in b.items():
            out[(i + k, j + l)] = out.get((i + k, j + l), 0) + v * x
    return {key: v for key, v in out.items() if v}


def _shifted_power(i: int, j: int) -> dict:
    px = {(a, 0): math.comb(i, a) * (-1) ** (i - a) for a in range(i + 1)}
    py = {(0, b): math.comb(j, b) * (-1) ** (j - b) for b in range(j + 1)}
    return _pmul(px, py)


def tutte_frontier(w: Work | None, n_vertices: int, edges: list) -> tuple:
    """Tutte-Polynom durch die Frontier-Rechnung im Polynom-Semiring (Stück 14). Aufwand = (Summe der Zustände) · (größte Koeffizientenzahl je Zustand), nach jeder Schicht geprüft."""
    last: dict = {}
    for i, (a, b) in enumerate(edges):
        last[a] = i
        last[b] = i
    states = {((), ()): {(0, 0): 1}}
    total_states, max_coeffs = 0, 1
    for i, (a, b) in enumerate(edges):
        new: dict = {}
        for (front, lab), val in states.items():
            front, lab = list(front), list(lab)
            for v in (a, b):
                if v not in front:
                    front.append(v)
                    lab.append(max(lab, default=-1) + 1)
            order = sorted(range(len(front)), key=lambda t: front[t])
            front = [front[t] for t in order]
            lab = [lab[t] for t in order]
            la, lb = lab[front.index(a)], lab[front.index(b)]
            options = [(lab, 0, 0), ([la if x == lb else x for x in lab], 1, 0) if la != lb else (lab, 0, 1)]
            keep = [t for t in range(len(front)) if last[front[t]] > i]
            kf = tuple(front[t] for t in keep)
            for newlab, dk, de in options:
                remap: dict = {}
                canon = tuple(remap.setdefault(newlab[t], len(remap)) for t in keep)
                tgt = new.setdefault((kf, canon), {})
                for (k, e), c in val.items():
                    key = (k + dk, e + de)
                    tgt[key] = tgt.get(key, 0) + c
        states = new
        total_states += len(states)
        max_coeffs = max(max_coeffs, max((len(v) for v in states.values()), default=1))
        if w is not None:
            w.set(total_states * max_coeffs)
    counts: dict = {}
    for val in states.values():
        for key, c in val.items():
            counts[key] = counts.get(key, 0) + c
    poly: dict = {}
    for (k, e), c in counts.items():
        poly = _padd(poly, {m: c * v for m, v in _shifted_power(n_vertices - 1 - k, e).items()})
    return poly, total_states * max_coeffs


def chromatic_values(poly: dict, n_vertices: int, ks: tuple) -> tuple:
    """P(G, k) = (−1)^(n−1) · k · T(1−k, 0) für zusammenhängende Graphen."""
    return tuple((-1) ** (n_vertices - 1) * k * sum(v * (1 - k) ** i for (i, j), v in poly.items() if j == 0) for k in ks)


def f6_tutte(w: Work, n: int, ks: tuple = (3,)) -> tuple:
    poly, _ = tutte_frontier(w, n * n, grid_edges(n, n))
    return chromatic_values(poly, n * n, ks)


def spanning_trees_from_poly(poly: dict) -> int:
    return sum(poly.values())


# ---------------------------------------------------------------- F7: Zahl der Teilmengen mit gegebener Summe
def f7_instance(n: int, wmax: int, seed: int = SEED) -> tuple:
    rng = random.Random(seed + n * 1000 + wmax)
    ws = [rng.randint(1, wmax) for _ in range(n)]
    return ws, sum(ws) // 2


def f7_brute(w: Work, ws: list, s: int) -> int:
    """Aufzählen durch Rückverfolgung mit Abbruch bei Summe über s: ein Schritt je Knoten."""
    count = 0

    def rec(i, total):
        nonlocal count
        w.add()
        if total > s:
            return
        if i == len(ws):
            count += total == s
            return
        rec(i + 1, total)
        rec(i + 1, total + ws[i])

    rec(0, 0)
    return count


def f7_dp(w: Work, ws: list, s: int) -> int:
    """Tabelle (Koeffizient des Produkts der (1 + z^a)): (s + 1) Schritte je Gegenstand."""
    table = [0] * (s + 1)
    table[0] = 1
    for a in ws:
        w.add(s + 1)
        for t in range(s, a - 1, -1):
            table[t] += table[t - a]
    return table[s]


# ---------------------------------------------------------------- Schätzer: Aufwand für 5 Prozent Standardfehler
def _finish(values: list, steps: int, probes: int) -> dict:
    mean = statistics.fmean(values)
    cv = statistics.pstdev(values) / mean if mean else math.inf
    needed = math.ceil(cv ** 2 / 0.0025) if math.isfinite(cv) else None
    return {"Mittel": mean, "cv": cv, "nötig": needed, "Aufwand": (needed * steps / probes) if needed else None}


def estimator_tilings(n: int, probes: int = 2000) -> dict:
    """Zufallsabstieg für Dominosteine (Rosenbluth, Stück 15): Gewicht = Produkt der Möglichkeiten je Schritt; ein Schritt je gesetztem Stein."""
    rng = random.Random(SEED + n)
    values, steps = [], 0
    for _ in range(probes):
        covered = [False] * (n * n)
        weight, pos, ok = 1, 0, True
        while True:
            while pos < n * n and covered[pos]:
                pos += 1
            if pos == n * n:
                break
            r, c = divmod(pos, n)
            opts = []
            if c + 1 < n and not covered[pos + 1]:
                opts.append(pos + 1)
            if r + 1 < n:
                opts.append(pos + n)
            steps += 1
            if not opts:
                ok = False
                break
            weight *= len(opts)
            u = opts[rng.randrange(len(opts))]
            covered[pos] = covered[u] = True
        values.append(weight if ok else 0)
    return _finish(values, steps, probes)


def estimator_paths(n: int, probes: int = 300) -> dict:
    """Zufallsabstieg für einfache Wege mit Erreichbarkeitsprüfung; Schritte = gelaufene Schritte plus Besuche der Breitensuche."""
    rng = random.Random(SEED + 77 + n)
    nb = grid_neighbor_lists(n)
    target = n * n - 1
    values, work = [], 0
    for _ in range(probes):
        v, visited, weight, ok = 0, 1, 1, True
        while v != target:
            options = []
            for u in nb[v]:
                if visited >> u & 1:
                    continue
                if u == target:
                    options.append(u)
                    continue
                blocked, seen, stack, found = visited | 1 << u, 1 << u, [u], False
                while stack:
                    x = stack.pop()
                    work += 1
                    if x == target:
                        found = True
                        break
                    for y in nb[x]:
                        if not (blocked | seen) >> y & 1:
                            seen |= 1 << y
                            stack.append(y)
                if found:
                    options.append(u)
            if not options:
                ok = False
                break
            weight *= len(options)
            v = options[rng.randrange(len(options))]
            visited |= 1 << v
            work += 1
        values.append(weight if ok else 0)
    return _finish(values, work, probes)


def estimator_subsets(items: list, s: int, probes: int = 3000) -> dict:
    """Zufallsabstieg für Teilmengen mit Summe s: je Gegenstand nehmen oder weglassen, gestrichen wenn die Summe nicht mehr erreichbar ist; ein Schritt je Gegenstand."""
    rng = random.Random(SEED + len(items))
    n = len(items)
    suffix = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix[i] = suffix[i + 1] + items[i]
    values, steps = [], 0
    for _ in range(probes):
        total, weight, ok = 0, 1, True
        for i in range(n):
            steps += 1
            opts = [t for t in (total, total + items[i]) if t <= s and t + suffix[i + 1] >= s]
            if not opts:
                ok = False
                break
            weight *= len(opts)
            total = opts[rng.randrange(len(opts))]
        values.append(weight if ok and total == s else 0)
    return _finish(values, steps, probes)
