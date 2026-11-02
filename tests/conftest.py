"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def hand():
    """Handwerte der sieben Familien.
    F1: Binärketten der Länge 4 ohne 11: 0000, 0001, 0010, 0100, 0101, 1000, 1001, 1010 = 8 (= F(6)).
    F2: Surjektionen von 3 Elementen auf 2: 2³ − 2 = 6 (Sieb: 8 − 2 · 1 + 0 = 6; Stirling S(3,2) = 3, mal 2! = 6).
    F3: Halsketten mit 3 Farben, vier Perlen: (3⁴ + 3 + 3² + 3)/4 = 96/4 = 24.
    F4: Dominosteine im 2×2-Brett: zwei (zwei waagerechte oder zwei senkrechte); Kasteleyn 4 cos²(π/3) + 4 cos²(π/3) = 2.
    F5: einfache Wege im 2×2-Gitter von oben links nach unten rechts: zwei (über rechts oder über unten).
    F6: Dreifärbungen des 2×2-Gitters (Viereck): 2⁴ + 2 = 18.
    F7: Teilmengen von {1, 2, 3} mit Summe 3: {3} und {1, 2}: zwei."""
    return {"F1": (4, 8), "F2": ((3, 2), 6), "F3": (4, 24), "F4": (2, 2), "F5": (2, 2), "F6": (2, 18), "F7": (([1, 2, 3], 3), 2)}
