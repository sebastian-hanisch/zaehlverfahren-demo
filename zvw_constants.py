"""Konstanten: Familien, Größenstufen, Budgets, Fragen, Farben und Presets."""

FAMILY_KEYS = ("F1", "F2", "F3", "F4", "F5", "F6", "F7")
DEFAULT_FAMILY = "F4"
FAMILY_NAMES = {
    "F1": "Binärketten ohne zwei Einsen hintereinander",
    "F2": "Surjektionen von n Elementen auf k",
    "F3": "Halsketten mit 3 Farben",
    "F4": "Dominosteine im n×n-Brett",
    "F5": "Einfache Wege im n×n-Gitter",
    "F6": "Dreifärbungen des n×n-Gitters",
    "F7": "Teilmengen mit halber Gesamtsumme",
}
FAMILY_STUECKE = {"F1": "Stück 1, 2", "F2": "Stück 6, 7", "F3": "Stück 11, 12", "F4": "Stück 13", "F5": "Stück 13, 15", "F6": "Stück 14", "F7": "Stück 4, 15"}
FAMILY_LABELS = tuple(f"{k}: {FAMILY_NAMES[k]}" for k in FAMILY_KEYS)
LABEL_TO_KEY = {f"{k}: {FAMILY_NAMES[k]}": k for k in FAMILY_KEYS}
DEFAULT_FAMILY_LABEL = f"{DEFAULT_FAMILY}: {FAMILY_NAMES[DEFAULT_FAMILY]}"

SIZES = {
    "F1": (10, 20, 30, 100, 1000, 100000),
    "F2": ((6, 3), (10, 4), (20, 8), (40, 20), (200, 100)),
    "F3": (6, 12, 14, 16, 20, 24, 60),
    "F4": (4, 6, 8, 10, 12, 14, 16),
    "F5": (3, 4, 5, 6, 7, 8, 9, 10),
    "F6": (2, 3, 4, 5, 6, 7),
    "F7": ((16, 10), (20, 10), (20, 1000), (24, 100000), (30, 100000), (40, 1000000)),   # (Gegenstände, größtes Gewicht)
}
SIZE_MIN, SIZE_MAX, DEFAULT_SIZE = 1, 8, 5          # Größenstufe 1 bis 8; je Familie gibt es höchstens so viele Stufen
BUDGET_CHOICES = (1000, 10000, 100000, 300000, 1000000, 3000000)
DEFAULT_BUDGET = 1000000
GRID_BUDGET = 1000000                                # Budget der Gesamttabelle (Experiment 1 und 2)
QUESTIONS = ("Zahl", "Liste (Halsketten) oder vier Farbenzahlen (Färbungen)")
QUESTION_ZAHL, QUESTION_MORE = QUESTIONS
DEFAULT_QUESTION = QUESTION_ZAHL
FLOAT_METHODS = ("Kasteleyn",)
FOUR_COLORS = (2, 3, 4, 5)
ONE_COLOR = (3,)
TIE_FACTOR = 3.0                                     # Verfahren mit höchstens so viel Aufwand wie der Gewinner gelten als gleichwertig

EXP_KASTELEYN_NS = (2, 4, 6, 8, 10, 12, 14, 16)
EXP_KASTELEYN_BUDGET = 3500000
EXP_COLOR_GRIDS = (3, 4, 5, 6)
EXP_NECKLACE_NS = (6, 12, 14, 16)
EXP_NECKLACE_BUDGET = 7000000
EXP_ESTIMATOR_F4 = (4, 6, 8, 10, 12)
EXP_ESTIMATOR_F5 = (3, 4, 5, 6, 7, 8)

PLAY_N_DEFAULT, PLAY_K_DEFAULT = 40, 20
PLAY_N_MAX = 5000

COLOR_MAIN = "#2F6B65"
COLOR_ALL = "rgba(150,150,150,0.75)"
COLOR_WARN = "#c0504d"
COLOR_LINE = "#4c78a8"
COLOR_SAND = "#c9a227"

PRESETS = {
    "Standardfall: Dominosteine 12×12 (Kasteleyn falsch)": {"family": "F4: Dominosteine im n×n-Brett", "size": 5, "budget": 1000000, "question": QUESTION_ZAHL},
    "Binärketten: Wechsel von der Tabelle zur Matrixpotenz": {"family": "F1: Binärketten ohne zwei Einsen hintereinander", "size": 5, "budget": 300000, "question": QUESTION_ZAHL},
    "Wege im 8×8-Gitter: das Frontier-Diagramm gewinnt": {"family": "F5: Einfache Wege im n×n-Gitter", "size": 6, "budget": 1000000, "question": QUESTION_ZAHL},
    "Dreifärbungen 6×6, vier Farbenzahlen: das Polynom gewinnt": {"family": "F6: Dreifärbungen des n×n-Gitters", "size": 5, "budget": 3000000, "question": QUESTION_MORE},
    "Halsketten n = 14 als Liste: FKM statt Burnside": {"family": "F3: Halsketten mit 3 Farben", "size": 3, "budget": 1000000, "question": QUESTION_MORE},
    "Teilmengensumme n = 24: nichts geht mehr": {"family": "F7: Teilmengen mit halber Gesamtsumme", "size": 4, "budget": 1000000, "question": QUESTION_ZAHL},
}
PRESET_HELP = {
    "Standardfall: Dominosteine 12×12 (Kasteleyn falsch)": "Kasteleyns Kosinusformel ist in Gleitkomma ab 12×12 falsch (53.060.477.521.959.928 statt 53.060.477.521.960.000, durch Rundungsfehler im Produkt; der Wert liegt über 2⁵³); die Profil-Rechnung ist 2.897-mal teurer, aber richtig und gewinnt.",
    "Binärketten: Wechsel von der Tabelle zur Matrixpotenz": "Bei n = 1.000 gewinnt die Matrixpotenz (136 Schritte) gegen die Tabelle (999 Schritte); bei n = 30 war es noch die Tabelle (29 gegen 80).",
    "Wege im 8×8-Gitter: das Frontier-Diagramm gewinnt": "789.360.053.252 einfache Wege: das Frontier-Diagramm braucht 64.993 Schritte, das Aufzählen über eine Million; der Schätzer wäre für 5 Prozent Standardfehler noch viel teurer.",
    "Dreifärbungen 6×6, vier Farbenzahlen: das Polynom gewinnt": "Für k = 2 bis 5 braucht die Transfermatrix 135.842.020 Schritte, das Tutte-Polynom einmal 2.586.431 (Faktor 52,5) und liefert dazu Spannbäume und Zuverlässigkeit.",
    "Halsketten n = 14 als Liste: FKM statt Burnside": "Die Zahl 341.802 kostet Burnside 30 Schritte; die Liste aller Halsketten kostet FKM 836.410 Schritte (Faktor 27.880).",
    "Teilmengensumme n = 24: nichts geht mehr": "24 Gegenstände mit Gewichten bis 100.000: Tabelle und Aufzählen liegen über dem Budget, und der Schätzer bräuchte für 5 Prozent Standardfehler schätzungsweise mehr als eine Million Sondierungen (die Streuung ist selbst unsicher).",
}
