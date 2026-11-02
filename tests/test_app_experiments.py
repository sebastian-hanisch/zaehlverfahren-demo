"""Oberfläche: jede Familie, jedes Preset, Permalink mit Müll, die Spielwiese und das PDF laufen ohne Ausnahme und zeigen die erwarteten Texte."""

import os
from pathlib import Path

from streamlit.testing.v1 import AppTest

import zvw_constants as C
import zvw_evaluation as ev
import zvw_visualization as V

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "400"))


def _run(query=None, **state):
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (query or {}).items():
        at.query_params[key] = value
    at.run()
    for key, value in state.items():
        at.session_state[key] = value
    if state:
        at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texts(at):
    return [e.value for e in at.success] + [e.value for e in at.warning] + [e.value for e in at.info] + [e.value for e in at.error]


def test_standard_case_shows_all_six_experiments_and_the_answer():
    at = _run()
    heads = [s.value for s in at.subheader]
    assert [h for h in heads if h.startswith("🔬 Experiment")] == [
        "🔬 Experiment 1: Wer gewinnt wo?", "🔬 Experiment 2: Der Gewinner wechselt mit der Größe", "🔬 Experiment 3: Schnell, aber falsch", "🔬 Experiment 4: Die Frage entscheidet",
        "🔬 Experiment 5: Wo nichts mehr geht, und der Schätzer", "🔬 Experiment 6: Lässt sich das Verfahren aus Merkmalen vorhersagen?"]
    assert any(t.startswith("Dominosteine im n×n-Brett, 12×12, Budget 1.000.000 Schritte: Gewinner ist Profil-Rechnung") for t in _texts(at)) and not at.error


def test_metrics_of_the_standard_case():
    at = _run()
    assert [(m.label, m.value) for m in at.metric] == [("Gewinner", "Profil-Rechnung"), ("Schritte des Gewinners", "104.283"), ("Ergebnis", "53.060.477.521.960.000"), ("Regelwerk", "gleich")]


def test_every_preset_runs_and_shows_its_family():
    for name, p in C.PRESETS.items():
        at = _run(family_select=p["family"], size_slider=p["size"], budget_select=p["budget"], question_select=p["question"])
        assert at.selectbox(key="family_select").value == p["family"], name
        assert not at.error, name


def test_every_family_runs_at_its_smallest_and_largest_stage():
    for label in C.FAMILY_LABELS:
        for stage in (1, 3):
            at = _run(family_select=label, size_slider=stage, budget_select=100000)
            assert not at.error, (label, stage)


def test_the_second_question_runs_for_the_two_families_that_use_it():
    for key in ("F3", "F6"):
        at = _run(family_select=f"{key}: {C.FAMILY_NAMES[key]}", size_slider=2, budget_select=300000, question_select=C.QUESTION_MORE)
        assert not at.error, key
    at = _run(family_select=f"F1: {C.FAMILY_NAMES['F1']}", question_select=C.QUESTION_MORE, budget_select=10000)
    assert any("nur bei den Halsketten" in t for t in _texts(at))


def test_permalink_garbage_falls_back_to_defaults():
    at = _run(query={"family": "Unsinn", "size": "abc", "budget": "7", "question": "Zauber"})
    assert at.selectbox(key="family_select").value == C.DEFAULT_FAMILY_LABEL and at.slider(key="size_slider").value == C.DEFAULT_SIZE
    assert at.select_slider(key="budget_select").value == C.DEFAULT_BUDGET and at.selectbox(key="question_select").value == C.DEFAULT_QUESTION


def test_play_ground_answers_and_warns_for_k_above_n():
    at = _run()
    assert any(t.startswith("Surjektionen von 40 Elementen auf 20:") for t in _texts(at)) and "play_chart" in [c.key for c in at.get("plotly_chart")]
    bad = _run(play_n=5, play_k=9)
    assert any("k darf nicht größer als n sein" in w.value for w in bad.warning) and "play_chart" not in [c.key for c in bad.get("plotly_chart")]
    big = _run(play_n=5000, play_k=2500)
    assert any("mehr als 10^600" in t for t in _texts(big))


def test_pdf_button_makes_a_download():
    at = _run()
    at.button(key="pdf_make").click().run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert len(at.get("download_button")) == 1


def test_charts_have_unique_keys():
    at = _run()
    keys = [c.key for c in at.get("plotly_chart")]
    assert len(keys) == len(set(keys)) and set(keys) == {"main_chart", "switch_chart_F1", "switch_chart_F2", "switch_chart_F4", "switch_chart_F5", "kasteleyn_chart", "question_chart", "estimator_chart", "play_chart"}


def test_pdf_builds_for_every_family_and_both_questions():
    from zvw_pdf_export import build_pdf
    for label in C.FAMILY_LABELS:
        for question in C.QUESTIONS:
            a = ev.analyse(ev.Settings(label, 2, 100000, question))
            assert build_pdf(a)[:4] == b"%PDF", (label, question)


def test_chart_builders_return_locked_axes():
    cells = ev.grid_cells()
    a = ev.analyse(ev.Settings(C.DEFAULT_FAMILY_LABEL, 5, 1000000, C.QUESTION_ZAHL))
    figs = (V.build_cell(a.cell), V.build_switch(ev.switch_series(cells, "F1"), "x"), V.build_kasteleyn(ev.kasteleyn_rows()), V.build_question(ev.question_rows()), V.build_estimator(ev.estimator_rows(cells)), V.build_play(ev.surjection_costs(40, 20)))
    for fig in figs:
        assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange
