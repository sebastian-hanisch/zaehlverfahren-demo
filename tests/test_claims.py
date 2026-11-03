"""Jede Zahl aus der README und aus den Texten der App, nachgerechnet (DEMO-PLAYBOOK §4). Aufwand und Ergebnisse sind deterministisch; Schätzer laufen mit festem Seed; Zeiten kommen nicht vor."""

import math
from pathlib import Path

import zvw_algorithm as A
import zvw_constants as C
import zvw_evaluation as ev

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
S = ev.Settings


def cells():
    return ev.grid_cells()


def by(key):
    return [c for c in cells() if c["key"] == key]


def work(c, name):
    r = next(r for r in c["methods"] if r["Verfahren"] == name)
    return r["Schritte"] if r["Status"] in (A.EXACT, "falsch", "exakt, ungeprüft") else "über"


def test_readme_grid_dimensions_and_distinct_winners():
    cs = cells()
    assert len(cs) == 45 and C.GRID_BUDGET == 1000000
    assert sum(1 for c in cs if c["winner"] is None) == 4 and len({c["winner"] for c in cs if c["winner"]}) == 12
    families_changing = [k for k in C.FAMILY_KEYS if len({c["winner"] for c in by(k)}) > 1]
    assert families_changing == ["F1", "F2", "F4", "F5", "F6", "F7"]


def test_readme_f1_row():
    rows = [(work(c, "Aufzählen"), work(c, "Tabelle"), work(c, "Matrixpotenz"), c["winner"]) for c in by("F1")]
    assert rows == [(375, 9, 56, "Tabelle"), (46366, 19, 64, "Tabelle"), ("über", 29, 80, "Tabelle"), ("über", 99, 88, "Matrixpotenz"), ("über", 999, 136, "Matrixpotenz"), ("über", 99999, 192, "Matrixpotenz")]
    assert [math.floor(math.log10(A.run(A.f1_matrix, 10 ** 6, n)[1])) + 1 for n in (1000, 100000)] == [210, 20899]


def test_readme_f2_row():
    rows = [(work(c, "Aufzählen"), work(c, "Stirling-Tabelle"), work(c, "Siebformel"), work(c, "EF-Potenz"), c["winner"]) for c in by("F2")]
    assert rows == [(729, 15, 20, 84, "Stirling-Tabelle"), ("über", 34, 30, 264, "Siebformel"), ("über", 132, 63, 1848, "Siebformel"), ("über", 610, 168, 17220, "Siebformel"), ("über", 15050, 1111, "über", "Siebformel")]


def test_readme_f3_row():
    rows = [(work(c, "Aufzählen aller Wörter"), work(c, "FKM"), work(c, "Burnside"), c["winner"]) for c in by("F3")]
    assert rows == [(4374, 332, 28, "Burnside"), ("über", 110234, 45, "Burnside"), ("über", 836410, 30, "Burnside"), ("über", "über", 40, "Burnside"), ("über", "über", 48, "Burnside"), ("über", "über", 64, "Burnside"), ("über", "über", 102, "Burnside")]


def test_readme_f4_row():
    rows = [(work(c, "Aufzählen"), work(c, "Profil-Rechnung"), work(c, "Kasteleyn"), c["winner"]) for c in by("F4")]
    assert rows == [(146, 69, 4, "Kasteleyn"), (33094, 526, 9, "Kasteleyn"), ("über", 3360, 16, "Kasteleyn"), ("über", 19359, 25, "Kasteleyn"), ("über", 104283, 36, "Profil-Rechnung"), ("über", 535997, 49, "Profil-Rechnung"), ("über", "über", 64, None)]
    status = [next(r["Status"] for r in c["methods"] if r["Verfahren"] == "Kasteleyn") for c in by("F4")]
    assert status == ["exakt"] * 4 + ["falsch", "falsch", "exakt, ungeprüft"]


def test_readme_f5_row():
    rows = [(work(c, "Aufzählen"), work(c, "Frontier-Diagramm"), c["winner"]) for c in by("F5")]
    assert rows == [(51, 54, "Aufzählen"), (1271, 285, "Frontier-Diagramm"), (90111, 1246, "Frontier-Diagramm"), ("über", 4926, "Frontier-Diagramm"), ("über", 18271, "Frontier-Diagramm"), ("über", 64993, "Frontier-Diagramm"),
                    ("über", 224462, "Frontier-Diagramm"), ("über", 758682, "Frontier-Diagramm")]


def test_readme_f6_row():
    rows = [(work(c, "Aufzählen"), work(c, "Transfermatrix"), work(c, "Tutte-Frontier"), c["winner"]) for c in by("F6")]
    assert rows == [(81, 36, 35, "Tutte-Frontier"), (19683, 288, 1012, "Transfermatrix"), ("über", 1728, 18574, "Transfermatrix"), ("über", 9216, 245505, "Transfermatrix"), ("über", 46080, "über", "Transfermatrix"), ("über", 221184, "über", "Transfermatrix")]


def test_readme_f7_row():
    rows = [(work(c, "Aufzählen"), work(c, "Tabelle (EF)"), c["winner"]) for c in by("F7")]
    assert rows == [(88049, 720, "Tabelle (EF)"), ("über", 1160, "Tabelle (EF)"), ("über", 69340, "Tabelle (EF)"), ("über", "über", None), ("über", "über", None), ("über", "über", None)]
    est = [c["estimator"] for c in by("F7")]
    assert [round(e["Aufwand"]) if e["Aufwand"] else None for e in est] == [22112, 47586, 938106, 28790400, None, None]
    assert A.run(A.f7_brute, 10 ** 7, *A.f7_instance(20, 1000))[2] == 1233265 and len(A.f7_instance(16, 10)[0]) == 16


def test_readme_kasteleyn_row():
    rows = {r["n"]: r for r in ev.kasteleyn_rows()}
    assert [rows[n]["Schritte Kasteleyn"] for n in rows] == [1, 4, 9, 16, 25, 36, 49, 64] and [rows[n]["Schritte exakt"] for n in rows] == [6, 69, 526, 3360, 19359, 104283, 535997, 2661721]
    assert all(rows[n]["Abweichung"] == 0 for n in (2, 4, 6, 8, 10)) and rows[10]["exakt"] == 258584046368
    assert (rows[12]["exakt"], rows[12]["Kasteleyn"], rows[12]["Abweichung"]) == (53060477521960000, 53060477521959928, -72)
    assert (rows[14]["exakt"], rows[14]["Kasteleyn"], rows[14]["Abweichung"]) == (112202208776036178000000, 112202208776036598939648, 420939648)
    assert (rows[16]["exakt"], rows[16]["Kasteleyn"], rows[16]["Abweichung"]) == (2444888770250892795802079170816, 2444888770250909948854883319808, 17153052804148992)
    assert 2 ** 53 == 9007199254740992 and rows[10]["exakt"] < 2 ** 53 < rows[12]["exakt"]


def test_readme_question_rows():
    qs = ev.question_rows()
    rows = {r["n"]: r for r in qs["Färbungen"]}
    assert [(rows[n]["Transfermatrix vier"], rows[n]["Tutte"]) for n in (3, 4, 5, 6)] == [(15688, 1012), (343932, 18574), (6982736, 245505), (135842020, 2586431)]
    assert round(rows[6]["Faktor"], 1) == 52.5 and (rows[6]["Transfermatrix k=3"], round(rows[6]["Faktor eine Zahl"])) == (46080, 56)
    assert rows[6]["Werte"] == (2, 101596896, 380053267505964, 32921147633979091400)
    hals = {r["n"]: r for r in qs["Halsketten"]}
    assert [(hals[n]["Zahl"], hals[n]["Burnside"], hals[n]["FKM"], round(hals[n]["Faktor"])) for n in (6, 12, 14, 16)] == [(130, 28, 332, 12), (44368, 45, 110234, 2450), (341802, 30, 836410, 27880), (2690844, 40, 6507232, 162681)]


def test_readme_estimator_rows():
    rows = {(r["Familie"], r["Größe"]): r for r in ev.estimator_rows(cells())}
    f4 = [(rows[("F4", f"{n}×{n}")]["exakt"], round(rows[("F4", f"{n}×{n}")]["Schätzer"])) for n in (4, 6, 8, 10, 12)]
    assert f4 == [(4, 1608), (9, 16659), (16, 115585), (25, 265026), (104283, 9376667)]
    f5 = [(rows[("F5", f"{n}×{n}")]["exakt"], round(rows[("F5", f"{n}×{n}")]["Schätzer"])) for n in (3, 4, 5, 6, 7, 8)]
    assert f5 == [(51, 902), (285, 30599), (1246, 183024), (4926, 886267), (18271, 2711823), (64993, 15029869)]
    comparable = [r for r in rows.values() if r["exakt"] is not None and r["Schätzer"] is not None]
    assert len(comparable) == 14 and all(r["Schätzer"] > r["exakt"] for r in comparable)


def test_readme_rule_row():
    rr = ev.rule_rows(cells())
    assert rr[1]["Zahlen"] == {"gleich": 41, "gleichwertig": 2, "verfehlt": 2} and rr[2]["Zahlen"] == {"gleich": 42, "gleichwertig": 2, "verfehlt": 1}
    assert [(k, g) for k, g, w, r in rr[1]["Verfehlungen"]] == [("F1", "n = 1.000"), ("F4", "16×16")]
    f1 = {c["label"]: c for c in by("F1")}
    assert ev.rule_status(f1["n = 100"], ev.rule("F1", 100, C.QUESTION_ZAHL, 1)) == "gleichwertig" and round(work(f1["n = 100"], "Tabelle") / work(f1["n = 100"], "Matrixpotenz"), 3) == 1.125
    f6 = by("F6")[0]
    assert ev.rule_status(f6, ev.rule("F6", 2, C.QUESTION_ZAHL, 1)) == "gleichwertig" and round(36 / 35, 2) == 1.03


def test_readme_hand_values_and_play_row(hand):
    assert hand["F1"][1] == A.run(A.f1_table, 100, hand["F1"][0])[1] and hand["F3"][1] == A.run(A.f3_burnside, 100, 4)[1]
    res = ev.surjection_costs(40, 20)
    assert (len(str(res["Kosten"]["Aufzählen"])) - 1, res["Kosten"]["Stirling-Tabelle"], res["Kosten"]["Siebformel"], res["Kosten"]["EF-Potenz"]) == (52, 610, 168, 17220)


def test_preset_help_numbers_match_the_computation():
    h = C.PRESET_HELP
    std = ev.analyse(S(**C.PRESETS["Standardfall: Dominosteine 12×12 (Kasteleyn falsch)"])).cell
    assert round(work(std, "Profil-Rechnung") / work(std, "Kasteleyn")) == 2897 and "2.897-mal" in h["Standardfall: Dominosteine 12×12 (Kasteleyn falsch)"] and "53.060.477.521.959.928" in h["Standardfall: Dominosteine 12×12 (Kasteleyn falsch)"]
    f1 = ev.analyse(S(**C.PRESETS["Binärketten: Wechsel von der Tabelle zur Matrixpotenz"])).cell
    assert (work(f1, "Matrixpotenz"), work(f1, "Tabelle")) == (136, 999) and all(x in h["Binärketten: Wechsel von der Tabelle zur Matrixpotenz"] for x in ("136", "999", "n = 30", "29 gegen 80"))
    f5 = ev.analyse(S(**C.PRESETS["Wege im 8×8-Gitter: das Frontier-Diagramm gewinnt"])).cell
    assert (work(f5, "Frontier-Diagramm"), f5["value"], work(f5, "Aufzählen")) == (64993, 789360053252, "über") and "64.993" in h["Wege im 8×8-Gitter: das Frontier-Diagramm gewinnt"]
    f6 = ev.analyse(S(**C.PRESETS["Dreifärbungen 6×6, vier Farbenzahlen: das Polynom gewinnt"])).cell
    assert f6["winner"] == "Tutte-Frontier" and all(x in h["Dreifärbungen 6×6, vier Farbenzahlen: das Polynom gewinnt"] for x in ("135.842.020", "2.586.431", "52,5"))
    f3 = ev.analyse(S(**C.PRESETS["Halsketten n = 14 als Liste: FKM statt Burnside"])).cell
    assert f3["winner"] == "FKM" and all(x in h["Halsketten n = 14 als Liste: FKM statt Burnside"] for x in ("341.802", "30 Schritte", "836.410", "27.880"))
    f7 = ev.analyse(S(**C.PRESETS["Teilmengensumme n = 24: nichts geht mehr"])).cell
    assert f7["winner"] is None and f7["estimator"]["nötig"] == 1199600 and "mehr als eine Million" in h["Teilmengensumme n = 24: nichts geht mehr"]


def test_readme_mentions_every_module_file():
    root = Path(__file__).resolve().parent.parent
    for p in root.glob("zvw_*.py"):
        assert f"`{p.name}`" in README, p.name
    assert "`app.py`" in README and "Stück 16 von 16" in README
