"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt etwas anderes."""

import zvw_constants as C
import zvw_evaluation as ev
import zvw_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for name, preset in C.PRESETS.items():
        assert preset["family"] in C.FAMILY_LABELS and preset["budget"] in C.BUDGET_CHOICES and preset["question"] in C.QUESTIONS, name
        key = C.LABEL_TO_KEY[preset["family"]]
        assert C.SIZE_MIN <= preset["size"] <= len(C.SIZES[key]), name


def test_default_preset_equals_default_settings_and_comes_first():
    first = next(iter(C.PRESETS.values()))
    for field, key in P.PRESET_KEYS.items():
        assert first[field] == P.SETTING_SPECS[key].default


def test_every_preset_passes_the_checker_without_notes_or_problems():
    for name, preset in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**preset))
        assert a.problems == [] and a.notes == [], name


def test_presets_differ_from_each_other():
    seen = set()
    for name, preset in C.PRESETS.items():
        key = tuple(preset[f] for f in P.PRESET_KEYS)
        assert key not in seen, name
        seen.add(key)


def test_presets_show_the_promised_stories():
    stories = {name: ev.analyse(ev.Settings(**p)) for name, p in C.PRESETS.items()}
    names = list(C.PRESETS)
    assert stories[names[0]].cell["winner"] == "Profil-Rechnung" and any(r["Status"] == "falsch" for r in stories[names[0]].cell["methods"])
    assert stories[names[1]].cell["winner"] == "Matrixpotenz" and stories[names[2]].cell["winner"] == "Frontier-Diagramm"
    assert stories[names[3]].cell["winner"] == "Tutte-Frontier" and stories[names[4]].cell["winner"] == "FKM" and stories[names[5]].cell["winner"] is None


def test_every_family_appears_in_a_preset_except_the_ones_covered_by_the_grid():
    keys = {C.LABEL_TO_KEY[p["family"]] for p in C.PRESETS.values()}
    assert keys == {"F1", "F3", "F4", "F5", "F6", "F7"}


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert P.SETTING_SPECS["family_select"].choices == C.FAMILY_LABELS and P.SETTING_SPECS["budget_select"].choices == C.BUDGET_CHOICES and P.SETTING_SPECS["question_select"].choices == C.QUESTIONS
