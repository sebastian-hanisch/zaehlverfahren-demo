"""Auswertung: eine Zelle (Familie, Größe, Budget, Frage) mit allen Verfahren, das Regelwerk aus Merkmalen, fünf Experimente, die Spielwiese und die Urteilstexte. Alle Zufallsziehungen laufen mit festen Seeds."""

import functools
import math
from dataclasses import dataclass

import zvw_algorithm as A
import zvw_constants as C

_SUPER = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
NO_WINNER = "keines"
RULE_TIE = 1.5   # Faktor, bis zu dem die Empfehlung des Regelwerks als gleichwertig zum Gewinner zählt


@dataclass(frozen=True)
class Settings:
    family: str       # Beschriftung der Familie wie in FAMILY_LABELS
    size: int         # Größenstufe 1 bis 8
    budget: int
    question: str


@dataclass
class Analysis:
    settings: Settings
    key: str
    label: str
    size_label: str
    budget: int
    question: str
    cell: dict
    rule: str | None
    rule_status: str
    problems: list
    notes: list


# ----------------------------------------------------------------------------- Formatierung
def de(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f}".replace(".", ",").replace("-", "−")


def big_text(x: int) -> str:
    """Ganze Zahl lesbar: bis 15 Stellen mit Tausenderpunkt, darüber Mantisse mal Zehnerpotenz mit Stellenzahl."""
    if x < 0:
        return "−" + big_text(-x)
    if x < 10 ** 15:
        return f"{x:,}".replace(",", ".")
    d = (len(str(x)) if x.bit_length() < 14000 else int(x.bit_length() * 0.30103) + 1)
    if x.bit_length() < 14000:
        s = str(x // 10 ** (d - 3))
        return f"{s[0]},{s[1:3]}·10{str(d - 1).translate(_SUPER)} ({d} Stellen)"
    return f"rund {d} Stellen"


def full_text(x: int) -> str:
    """Ganze Zahl in allen Stellen mit Tausenderpunkten (für Zahlen, bei denen jede Stelle zählt)."""
    return f"{x:,}".replace(",", ".") if x >= 0 else "−" + full_text(-x)


def value_text(v) -> str:
    if v is None:
        return "–"
    if isinstance(v, tuple):
        return ", ".join(full_text(x) if x < 10 ** 40 else big_text(x) for x in v)
    return full_text(v) if v < 10 ** 40 else big_text(v)


def work_text(w: float) -> str:
    return big_text(round(w)) if math.isfinite(w) else "–"


def plural(n: int, one: str, many: str) -> str:
    return f"{big_text(n)} {one if n == 1 else many}"


# ----------------------------------------------------------------------------- Familien, Größen, Verfahren
def size_value(key: str, stage: int):
    sizes = C.SIZES[key]
    return sizes[max(C.SIZE_MIN, min(stage, len(sizes))) - 1]


def size_label(key: str, size) -> str:
    if key == "F1":
        return f"n = {big_text(size)}"
    if key == "F2":
        return f"n = {size[0]}, k = {size[1]}"
    if key == "F3":
        return f"n = {size} Perlen"
    if key in ("F4", "F5", "F6"):
        return f"{size}×{size}"
    return f"n = {size[0]} Gegenstände, Gewichte bis {big_text(size[1])}"


def _methods(key: str, size, question: str) -> list:
    """Liste von (Name, Funktion, Argumente, Ausgabe) für die Familie; `Ausgabe` ist "Zahl" oder "Liste"."""
    more = question == C.QUESTION_MORE
    if key == "F1":
        return [("Aufzählen", A.f1_brute, (size,), "Liste"), ("Tabelle", A.f1_table, (size,), "Zahl"), ("Matrixpotenz", A.f1_matrix, (size,), "Zahl")]
    if key == "F2":
        n, k = size
        return [("Aufzählen", A.f2_brute, (n, k), "Liste"), ("Stirling-Tabelle", A.f2_table, (n, k), "Zahl"), ("Siebformel", A.f2_sieve, (n, k), "Zahl"), ("EF-Potenz", A.f2_egf, (n, k), "Zahl")]
    if key == "F3":
        return [("Aufzählen aller Wörter", A.f3_brute, (size,), "Liste"), ("FKM", A.f3_fkm, (size,), "Liste"), ("Burnside", A.f3_burnside, (size,), "Zahl")]
    if key == "F4":
        return [("Aufzählen", A.f4_brute, (size,), "Liste"), ("Profil-Rechnung", A.f4_profile, (size,), "Zahl"), ("Kasteleyn", A.f4_kasteleyn, (size,), "Zahl")]
    if key == "F5":
        return [("Aufzählen", A.f5_brute, (size,), "Liste"), ("Frontier-Diagramm", A.f5_frontier, (size,), "Zahl")]
    if key == "F6":
        ks = C.FOUR_COLORS if more else C.ONE_COLOR
        return [("Aufzählen", A.f6_brute, (size, ks), "Zahl"), ("Transfermatrix", A.f6_transfer, (size, ks), "Zahl"), ("Tutte-Frontier", A.f6_tutte, (size, ks), "Polynom")]
    ws, s = A.f7_instance(*size)
    return [("Aufzählen", A.f7_brute, (ws, s), "Liste"), ("Tabelle (EF)", A.f7_dp, (ws, s), "Zahl")]


def uses_question(key: str) -> bool:
    return key in ("F3", "F6")


@functools.cache
def estimator_for(key: str, size) -> dict | None:
    """Schätzer-Aufwand für 5 Prozent Standardfehler, wo die App ihn rechnet (Dominosteine bis 12×12, Wege bis 8×8, Teilmengensumme)."""
    if key == "F4" and size in C.EXP_ESTIMATOR_F4:
        return A.estimator_tilings(size)
    if key == "F5" and size in C.EXP_ESTIMATOR_F5:
        return A.estimator_paths(size)
    if key == "F7":
        ws, s = A.f7_instance(*size)
        return A.estimator_subsets(ws, s)
    return None


@functools.cache
def compute_cell(key: str, size, budget: int, question: str, with_estimator: bool = True) -> dict:
    """Alle Verfahren der Familie in einer Zelle mit gleichem Budget; Gewinner = billigstes gültiges Verfahren (Ergebnis gleich dem Ganzzahl-Referenzwert)."""
    if key not in C.FAMILY_KEYS:
        raise ValueError(f"unbekannte Familie {key!r}")
    if budget < 1:
        raise ValueError("Das Budget muss mindestens 1 sein.")
    list_wanted = question == C.QUESTION_MORE and key == "F3"
    rows = []
    for name, func, args, output in _methods(key, size, question):
        if list_wanted and output != "Liste":
            rows.append({"Verfahren": name, "Status": "liefert keine Liste", "Wert": None, "Schritte": None, "gültig": False, "Ausgabe": output})
            continue
        status, value, work = A.run(func, budget, *args)
        rows.append({"Verfahren": name, "Status": status, "Wert": value, "Schritte": work, "gültig": False, "Ausgabe": output})
    ints = [r for r in rows if r["Status"] == A.EXACT and r["Verfahren"] not in C.FLOAT_METHODS]
    ref = min(ints, key=lambda r: r["Schritte"])["Wert"] if ints else None
    for r in rows:
        if r["Status"] != A.EXACT:
            continue
        if ref is None:
            r["Status"] = "exakt, ungeprüft" if r["Verfahren"] in C.FLOAT_METHODS else r["Status"]
        elif r["Wert"] == ref:
            r["gültig"] = True
        else:
            r["Status"] = "falsch"
    valid = sorted((r for r in rows if r["gültig"]), key=lambda r: r["Schritte"])
    winner = valid[0] if valid else None
    second = (valid[1], valid[1]["Schritte"] / winner["Schritte"]) if len(valid) > 1 else None
    est = estimator_for(key, size) if with_estimator else None
    return {"key": key, "size": size, "label": size_label(key, size), "budget": budget, "question": question, "methods": rows, "winner": winner["Verfahren"] if winner else None,
            "winner_work": winner["Schritte"] if winner else None, "value": ref, "second": ((second[0]["Verfahren"], second[1]) if second else None), "estimator": est}


# ----------------------------------------------------------------------------- Regelwerk aus Merkmalen
def rule(key: str, size, question: str = C.QUESTION_ZAHL, version: int = 1) -> str | None:
    """Empfehlung des Regelwerks aus Merkmalen der Struktur (Version 1: a priori; Version 2: Schwelle der Binärketten nach der Messung angepasst)."""
    if key == "F1":
        return "Tabelle" if size <= (10_000 if version == 1 else 100) else "Matrixpotenz"
    if key == "F2":
        return "Siebformel" if size[1] >= 4 else "Stirling-Tabelle"
    if key == "F3":
        return "FKM" if question == C.QUESTION_MORE else "Burnside"
    if key == "F4":
        return "Kasteleyn" if size <= 10 else "Profil-Rechnung"
    if key == "F5":
        return "Frontier-Diagramm" if size >= 4 else "Aufzählen"
    if key == "F6":
        return "Tutte-Frontier" if question == C.QUESTION_MORE else "Transfermatrix"
    ws, s = A.f7_instance(*size)
    return "Tabelle (EF)" if len(ws) * s <= 5_000_000 else ("Aufzählen" if len(ws) <= 20 else None)


def rule_status(cell: dict, recommended: str | None) -> str:
    """"gleich", "gleichwertig" (höchstens RULE_TIE-facher Aufwand des Gewinners) oder "verfehlt"."""
    win = cell["winner"]
    if win == recommended:
        return "gleich"
    if win is None or recommended is None:
        return "verfehlt"
    row = next((r for r in cell["methods"] if r["Verfahren"] == recommended), None)
    if row and row["gültig"] and row["Schritte"] <= RULE_TIE * cell["winner_work"]:
        return "gleichwertig"
    return "verfehlt"


# ----------------------------------------------------------------------------- die eingestellte Zelle
def effective_settings(s: Settings) -> tuple:
    if s.family not in C.LABEL_TO_KEY:
        raise ValueError(f"unbekannte Familie {s.family!r}")
    if s.question not in C.QUESTIONS:
        raise ValueError(f"unbekannte Frage {s.question!r}")
    if s.budget < 1:
        raise ValueError("Das Budget muss mindestens 1 sein.")
    key = C.LABEL_TO_KEY[s.family]
    notes: list = []
    top = len(C.SIZES[key])
    stage = max(C.SIZE_MIN, min(s.size, top))
    if stage != s.size:
        notes.append(f"Diese Familie hat {top} Größenstufen: gerechnet wird mit Stufe {stage}.")
    if s.question == C.QUESTION_MORE and not uses_question(key):
        notes.append("Die zweite Frage gibt es nur bei den Halsketten (Liste) und den Färbungen (vier Farbenzahlen): gerechnet wird die Zahl.")
    return key, stage, notes


def analyse(s: Settings) -> Analysis:
    key, stage, notes = effective_settings(s)
    size = size_value(key, stage)
    question = s.question if uses_question(key) else C.QUESTION_ZAHL
    cell = compute_cell(key, size, s.budget, question)
    problems = []
    rec = rule(key, size, question, 1)
    ints = [r for r in cell["methods"] if r["Status"] == A.EXACT and r["Verfahren"] not in C.FLOAT_METHODS]
    if len({r["Wert"] for r in ints}) > 1:
        problems.append("Die ganzzahligen Verfahren geben verschiedene Zahlen")
    return Analysis(s, key, C.FAMILY_NAMES[key], cell["label"], s.budget, question, cell, rec, rule_status(cell, rec), problems, notes)


def method_rows(a: Analysis) -> list:
    """Tabelle der Verfahren einer Zelle für die Anzeige."""
    c = a.cell
    out = []
    for r in c["methods"]:
        if r["Status"] in (A.EXACT, "falsch", "exakt, ungeprüft"):
            note = ""
            if r["Status"] == "falsch":
                note = f"weicht von {value_text(c['value'])} ab"
            elif r["Status"] == "exakt, ungeprüft":
                note = "kein ganzzahliges Verfahren im Budget zum Vergleich"
            elif r["Verfahren"] == c["winner"]:
                note = "Gewinner"
            out.append({"Verfahren": r["Verfahren"], "Ausgabe": r["Ausgabe"], "Status": r["Status"], "Ergebnis": value_text(r["Wert"]), "Schritte": work_text(r["Schritte"]), "Hinweis": note})
        else:
            out.append({"Verfahren": r["Verfahren"], "Ausgabe": r["Ausgabe"], "Status": r["Status"], "Ergebnis": "–", "Schritte": "–" if r["Schritte"] is None else f"mehr als {work_text(r['Schritte'])}", "Hinweis": ""})
    est = c["estimator"]
    if est is not None:
        if est["Aufwand"]:
            out.append({"Verfahren": "Schätzer (5 % Standardfehler)", "Ausgabe": "Schätzung", "Status": "geschätzt", "Ergebnis": f"Variationskoeffizient {de(est['cv'], 2)}", "Schritte": work_text(est["Aufwand"]), "Hinweis": f"{big_text(est['nötig'])} Sondierungen"})
        else:
            out.append({"Verfahren": "Schätzer (5 % Standardfehler)", "Ausgabe": "Schätzung", "Status": "geschätzt", "Ergebnis": "keine Sondierung trifft", "Schritte": "–", "Hinweis": "Streuung nicht bestimmbar"})
    return out


def verdict_answers(a: Analysis):
    if a.problems:
        return "error", "Die Rechenwege widersprechen sich: " + "; ".join(a.problems)
    c = a.cell
    head = f"{a.label}, {a.size_label}, Budget {big_text(a.budget)} Schritte: "
    wrong = [r for r in c["methods"] if r["Status"] == "falsch"]
    over = [r["Verfahren"] for r in c["methods"] if r["Status"] == A.OVER]
    if c["winner"] is None:
        text = head + "kein Verfahren liefert innerhalb des Budgets ein geprüftes Ergebnis"
        if over:
            text += f" (über dem Budget: {', '.join(over)})"
        text += "."
        est = c["estimator"]
        if est is not None and est["Aufwand"]:
            text += f" Der Schätzer bräuchte für 5 % Standardfehler {big_text(est['nötig'])} Sondierungen mit etwa {work_text(est['Aufwand'])} Schritten."
        elif est is not None:
            text += " Der Schätzer trifft keine Lösung: seine Streuung ist nicht bestimmbar."
        return "warning", text
    text = head + f"Gewinner ist {c['winner']} mit {work_text(c['winner_work'])} Schritten. Ergebnis: {value_text(c['value'])}."
    if c["second"]:
        name, factor = c["second"]
        text += f" Zweiter ist {name} mit dem {de(factor, 1)}-Fachen" + (" (gleichwertig)." if factor <= C.TIE_FACTOR else ".")
    if over:
        text += f" Über dem Budget: {', '.join(over)}."
    kind = "success"
    if wrong:
        r = wrong[0]
        text += f" {r['Verfahren']} wäre schneller ({work_text(r['Schritte'])} Schritte), liefert aber {value_text(r['Wert'])} statt {value_text(c['value'])}: falsch (Gleitkomma)."
        kind = "warning"
    est = c["estimator"]
    if est is not None and est["Aufwand"]:
        text += f" Der Schätzer kostet für 5 % Standardfehler etwa {work_text(est['Aufwand'])} Schritte: {de(est['Aufwand'] / c['winner_work'], 1)}-mal so viel wie der Gewinner."
    text += f" Das Regelwerk empfiehlt {a.rule or NO_WINNER}: {a.rule_status}."
    return kind, text


# ----------------------------------------------------------------------------- Experiment 1 und 2: die ganze Tabelle
@functools.cache
def grid_cells() -> list:
    cells = []
    for key in C.FAMILY_KEYS:
        for size in C.SIZES[key]:
            cells.append(compute_cell(key, size, C.GRID_BUDGET, C.QUESTION_ZAHL))
    return cells


def grid_rows(cells: list) -> list:
    rows = []
    for c in cells:
        wrong = [r["Verfahren"] for r in c["methods"] if r["Status"] == "falsch"]
        rows.append({"Familie": c["key"], "Größe": c["label"], "Gewinner": c["winner"] or NO_WINNER, "Schritte": c["winner_work"], "zweiter": c["second"], "falsch": wrong,
                     "über Budget": [r["Verfahren"] for r in c["methods"] if r["Status"] == A.OVER]})
    return rows


def verdict_grid(cells: list):
    winners = [c["winner"] for c in cells if c["winner"]]
    distinct = sorted(set(winners))
    none = sum(1 for c in cells if c["winner"] is None)
    by_family = {}
    for c in cells:
        by_family.setdefault(c["key"], []).append(c["winner"] or NO_WINNER)
    changing = [k for k, ws in by_family.items() if len(set(ws)) > 1]
    ok = len(distinct) >= 5 and all(len({r["Wert"] for r in c["methods"] if r["gültig"]}) <= 1 for c in cells)
    return ("success" if ok else "error"), (f"In {len(cells)} Zellen aus {len(by_family)} Familien (Budget {big_text(C.GRID_BUDGET)} Schritte) gewinnen {len(distinct)} verschiedene Verfahren; in {none} Zellen gewinnt keines. "
                                            f"In {len(changing)} von {len(by_family)} Familien wechselt der Gewinner mit der Größe ({', '.join(changing)}). Es gibt kein bestes Verfahren, nur eines, das zu Struktur, Frage und Größe passt.")


def switch_series(cells: list, key: str) -> dict:
    """Aufwand je Verfahren gegen die Größenstufe für eine Familie (None = über Budget oder falsch)."""
    out: dict = {}
    for i, c in enumerate(x for x in cells if x["key"] == key):
        for r in c["methods"]:
            out.setdefault(r["Verfahren"], []).append((c["label"], r["Schritte"] if r["Status"] in (A.EXACT, "falsch") else None))
    return out


def switch_points(cells: list) -> list:
    """Je Familie die Stellen, an denen der Gewinner wechselt: (Familie, von Größe, bis Größe, alter Gewinner, neuer Gewinner)."""
    out = []
    for key in C.FAMILY_KEYS:
        fam = [c for c in cells if c["key"] == key]
        for a, b in zip(fam, fam[1:]):
            if a["winner"] != b["winner"]:
                out.append((key, a["label"], b["label"], a["winner"] or NO_WINNER, b["winner"] or NO_WINNER))
    return out


def verdict_switch(cells: list):
    pts = switch_points(cells)
    return "success", (f"Der Gewinner wechselt an {len(pts)} Stellen: " + "; ".join(f"{k}: von {a} ({o}) zu {b} ({n})" for k, a, b, o, n in pts) + ".")


# ----------------------------------------------------------------------------- Experiment 3: schnell, aber falsch
@functools.cache
def kasteleyn_rows() -> list:
    rows = []
    for n in C.EXP_KASTELEYN_NS:
        _, exact, exact_work = A.run(A.f4_profile, C.EXP_KASTELEYN_BUDGET, n)
        _, kast, kast_work = A.run(A.f4_kasteleyn, C.EXP_KASTELEYN_BUDGET, n)
        rows.append({"n": n, "exakt": exact, "Kasteleyn": kast, "Abweichung": kast - exact, "Schritte exakt": exact_work, "Schritte Kasteleyn": kast_work, "über 2^53": exact > 2 ** 53})
    return rows


def verdict_kasteleyn(rows: list):
    first = next((r for r in rows if r["Abweichung"] != 0), None)
    ok = first is not None and all((r["Abweichung"] != 0) == (r["exakt"] > 2 ** 53 or r["n"] >= first["n"]) for r in rows) and all(r["Abweichung"] == 0 for r in rows if r["exakt"] <= 2 ** 53)
    if first is None:
        return "error", "Kasteleyn weicht nirgends ab: das widerspricht der Rechnung in Gleitkomma."
    last = rows[-1]
    return ("success" if ok else "error"), (f"Kasteleyns Kosinusprodukt in Gleitkomma stimmt bis {rows[rows.index(first) - 1]['n']}×{rows[rows.index(first) - 1]['n']} und ist ab {first['n']}×{first['n']} falsch: {full_text(first['Kasteleyn'])} statt {full_text(first['exakt'])} "
                                            f"(Abweichung {full_text(first['Abweichung'])}; der Wert liegt über 2⁵³ = {full_text(2 ** 53)}). Beim {last['n']}×{last['n']}-Brett beträgt die Abweichung {full_text(last['Abweichung'])}. "
                                            f"Dafür braucht die Formel {first['Schritte Kasteleyn']} bis {last['Schritte Kasteleyn']} Schritte gegen {big_text(first['Schritte exakt'])} bis {big_text(last['Schritte exakt'])} der Profil-Rechnung: schneller, aber nur richtig, wo sie stimmt.")


# ----------------------------------------------------------------------------- Experiment 4: die Frage entscheidet
@functools.cache
def question_rows() -> dict:
    colors = []
    for n in C.EXP_COLOR_GRIDS:
        one = A.f6_transfer_cost(n, 3)
        four = sum(A.f6_transfer_cost(n, k) for k in C.FOUR_COLORS)
        _, poly_values, tutte = A.run(A.f6_tutte, 10 ** 9, n, C.FOUR_COLORS)
        _, tr_value, _ = A.run(A.f6_transfer, 10 ** 9, n, C.ONE_COLOR) if n <= 5 else (None, None, None)
        colors.append({"n": n, "Transfermatrix k=3": one, "Transfermatrix vier": four, "Tutte": tutte, "Faktor": four / tutte, "Werte": poly_values, "Faktor eine Zahl": tutte / one, "Prüfwert": tr_value})
    necklaces = []
    for n in C.EXP_NECKLACE_NS:
        wf, wb = A.Work(C.EXP_NECKLACE_BUDGET), A.Work(C.EXP_NECKLACE_BUDGET)
        listed = A.f3_fkm(wf, n)
        count = A.f3_burnside(wb, n)
        necklaces.append({"n": n, "Zahl": count, "Burnside": wb.n, "Liste": listed, "FKM": wf.n, "Faktor": wf.n / wb.n})
    return {"Färbungen": colors, "Halsketten": necklaces}


def verdict_question(res: dict):
    c6 = next(r for r in res["Färbungen"] if r["n"] == 6)
    n_last = res["Halsketten"][-1]
    ok = all(r["Liste"] == r["Zahl"] for r in res["Halsketten"]) and c6["Faktor"] > 1 and all(r["Prüfwert"] is None or r["Prüfwert"][0] == r["Werte"][1] for r in res["Färbungen"])
    return ("success" if ok else "error"), (f"Dreifärbungen des 6×6-Gitters: für einen Wert kostet die Transfermatrix {big_text(c6['Transfermatrix k=3'])} Schritte, das Tutte-Polynom {big_text(c6['Tutte'])} ({de(c6['Faktor eine Zahl'], 0)}-mal so viel); "
                                            f"für die vier Farbenzahlen 2 bis 5 braucht die Transfermatrix zusammen {big_text(c6['Transfermatrix vier'])}, das Polynom einmal {big_text(c6['Tutte'])}: Faktor {de(c6['Faktor'], 1)} zugunsten des Polynoms, und es liefert dazu Spannbäume und die Zuverlässigkeit. "
                                            f"Halsketten: die Zahl {big_text(n_last['Zahl'])} (n = {n_last['n']}) kostet Burnside {n_last['Burnside']} Schritte, die Liste aller Halsketten FKM {big_text(n_last['FKM'])} (Faktor {big_text(round(n_last['Faktor']))}).")


# ----------------------------------------------------------------------------- Experiment 5: wo nichts mehr geht, und der Schätzer
def estimator_rows(cells: list) -> list:
    rows = []
    for c in cells:
        est = c["estimator"]
        if est is None:
            continue
        rows.append({"Familie": c["key"], "Größe": c["label"], "bester exakter": c["winner"], "exakt": c["winner_work"], "Schätzer": est["Aufwand"], "cv": est["cv"], "nötig": est["nötig"]})
    return rows


def verdict_estimator(rows: list):
    comparable = [r for r in rows if r["exakt"] is not None and r["Schätzer"] is not None]
    never = all(r["Schätzer"] > r["exakt"] for r in comparable)
    none_exact = [r for r in rows if r["exakt"] is None]
    undetermined = [r for r in rows if r["Schätzer"] is None]
    worst = max(comparable, key=lambda r: r["Schätzer"] / r["exakt"])
    return ("success" if never else "error"), (f"In allen {len(comparable)} Zellen, in denen ein exaktes Verfahren im Budget liegt und der Schätzer bestimmbar ist, ist das beste exakte Verfahren billiger (am deutlichsten bei {worst['Familie']} {worst['Größe']}: {work_text(worst['exakt'])} gegen {work_text(worst['Schätzer'])} Schritte). "
                                               f"In {len(none_exact)} Zellen liegt kein exaktes Verfahren im Budget; dort ist der Schätzer entweder nicht bestimmbar ({len([r for r in none_exact if r['Schätzer'] is None])} Zellen) oder braucht mehr als das Budget.")


# ----------------------------------------------------------------------------- Experiment 6: Regelwerk
def rule_rows(cells: list) -> dict:
    out = {}
    for version in (1, 2):
        counts = {"gleich": 0, "gleichwertig": 0, "verfehlt": 0}
        misses = []
        for c in cells:
            rec = rule(c["key"], c["size"], C.QUESTION_ZAHL, version)
            st = rule_status(c, rec)
            counts[st] += 1
            if st == "verfehlt":
                misses.append((c["key"], c["label"], c["winner"] or NO_WINNER, rec or NO_WINNER))
        out[version] = {"Zahlen": counts, "Verfehlungen": misses}
    return out


def verdict_rules(res: dict):
    v1, v2 = res[1], res[2]
    n = sum(v1["Zahlen"].values())
    miss = "; ".join(f"{k} {g}: Gewinner {w}, Regel {r}" for k, g, w, r in v1["Verfehlungen"]) or "keine"
    return "success", (f"Das Regelwerk aus Merkmalen (Version 1, vor der Messung geschrieben) trifft {v1['Zahlen']['gleich']} von {n} Gewinnern, {v1['Zahlen']['gleichwertig']} gleichwertig, {v1['Zahlen']['verfehlt']} verfehlt ({miss}). "
                       f"Version 2 (Schwelle nach der Messung angepasst): {v2['Zahlen']['gleich']} gleich, {v2['Zahlen']['gleichwertig']} gleichwertig, {v2['Zahlen']['verfehlt']} verfehlt: angepasst, nicht vorhergesagt.")


# ----------------------------------------------------------------------------- Spielwiese: Aufwandsrechner für Surjektionen
def surjection_costs(n: int, k: int) -> dict:
    if not (1 <= k <= n <= C.PLAY_N_MAX):
        raise ValueError(f"Es muss 1 ≤ k ≤ n ≤ {C.PLAY_N_MAX} gelten.")
    costs = {"Aufzählen": k ** n if n <= 2000 else None, "Stirling-Tabelle": n * k - k * (k - 1) // 2, "Siebformel": A.f2_sieve_cost(n, k), "EF-Potenz": A.f2_egf_cost(n, k)}
    exact = {m: c for m, c in costs.items() if c is not None and m != "Aufzählen"}
    best = min(exact, key=exact.get)
    if costs["Aufzählen"] is not None and costs["Aufzählen"] < exact[best]:
        best = "Aufzählen"
    return {"n": n, "k": k, "Kosten": costs, "Gewinner": best}


def verdict_play(res: dict):
    c = res["Kosten"]
    brute = "mehr als 10^600" if c["Aufzählen"] is None else (big_text(c["Aufzählen"]) if c["Aufzählen"] < 10 ** 15 else f"rund 10^{len(str(c['Aufzählen'])) - 1}" if c["Aufzählen"].bit_length() < 14000 else "unvorstellbar viele")
    return "success", (f"Surjektionen von {res['n']} Elementen auf {res['k']}: Aufzählen {brute} Schritte, Stirling-Tabelle {big_text(c['Stirling-Tabelle'])}, Siebformel {big_text(c['Siebformel'])}, Potenz der erzeugenden Funktion {big_text(c['EF-Potenz'])}. Gewinner nach dem Aufwandsmaß: {res['Gewinner']}.")
