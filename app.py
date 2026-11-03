"""Verfahrenswahl beim Zählen – welches Verfahren, gemessen woran? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 16 der Reihe „Abzählen und erzeugende Funktionen“ (Abschluss): Sieben Familien von Zählaufgaben, je mehrere Verfahren aus den Stücken davor mit einem gemeinsamen Schrittzähler und Budget (jedes Verfahren zählt seine eigene Einheit, verglichen wird die Größenordnung).
In diesen Familien gibt es kein bestes Verfahren: Struktur, Frage und Größe entscheiden, und ein schneller Gewinner kann falsch sein.
Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import zvw_constants as C
from zvw_evaluation import (
    Settings,
    analyse,
    big_text,
    de,
    estimator_rows,
    full_text,
    grid_cells,
    grid_rows,
    kasteleyn_rows,
    method_rows,
    question_rows,
    rule_rows,
    surjection_costs,
    switch_points,
    switch_series,
    verdict_answers,
    verdict_estimator,
    verdict_grid,
    verdict_kasteleyn,
    verdict_play,
    verdict_question,
    verdict_rules,
    verdict_switch,
    work_text,
)
from zvw_layout import dunkles_design, kopf_css
from zvw_pdf_export import build_pdf
from zvw_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sidebar_presets,
    sync_query_params,
)
from zvw_visualization import build_cell, build_estimator, build_kasteleyn, build_play, build_question, build_switch

st.set_page_config(page_title="Verfahrenswahl – Sebastian Hanisch", layout="wide")

SPINNER = "Die Experimente werden einmal gerechnet …"


@st.cache_data(show_spinner="Die Verfahren werden gerechnet …")
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=SPINNER)
def _grid():
    return grid_cells()


@st.cache_data(show_spinner=SPINNER)
def _kasteleyn():
    return kasteleyn_rows()


@st.cache_data(show_spinner=SPINNER)
def _question():
    return question_rows()


def verdict(pair):
    kind, text = pair
    getattr(st, kind)(text)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in zvw_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("⚖️ Verfahrenswahl beim Zählen – welches Verfahren, gemessen woran?")
st.markdown(
    """
**Welches Zählverfahren nimmt man?** Die Stücke 1 bis 15 haben **Verfahren** gebaut: Tabelle und Rekursion, Transfermatrix, erzeugende Funktion, Siebformel, Burnside, Frontier-Diagramm, Tutte-Polynom, Schätzer. Hier laufen sie auf **denselben Aufgaben** nebeneinander, mit **einem gemeinsamen Zähler** für den Aufwand
(Zahl der **Grundschritte** mit einer Obergrenze, dem **Budget**; jedes Verfahren zählt seine eigene Einheit), und wo mindestens zwei Verfahren im Budget liegen (26 von 45 Zellen), wird die Zahl gegen die anderen Verfahren der Zeile geprüft. In diesen Familien gibt es **kein bestes Verfahren**: die Wahl hängt an der **Struktur** (Baukasten, Symmetrie, Nebenbedingung), an der **Frage** (nur die Zahl, die Liste aller Vertreter, ein Polynom für viele Parameter)
und an der **Größe**; in den meisten Familien wechselt der Gewinner mit der Größe (nicht bei den Halsketten), ein schneller Gewinner kann **falsch** sein, und manchmal geht nichts mehr.

Weiter unten: **fünf Experimente** (**🔬**), eine **🎲 Spielwiese**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So wird gemessen", expanded=True):
    st.markdown(
        """
1. **Familie und Größe:** sieben Zählaufgaben aus den Stücken (Binärketten, Surjektionen, Halsketten, Dominosteine, einfache Wege, Dreifärbungen, Teilmengensumme), je mit acht oder weniger Größenstufen.
2. **Grundschritte:** Jedes Verfahren zählt seine eigenen Schritte (Tabelleneinträge, Zustände, Rekursionsaufrufe, Multiplikationen); überschreitet es das **Budget**, bricht es ab („über Budget“). Die Einheiten sind nur der **Größenordnung** nach vergleichbar.
3. **Gewinner:** das billigste Verfahren, dessen Ergebnis dem **Ganzzahl-Referenzwert** entspricht. Ein schnelleres Verfahren mit anderem Ergebnis ist **falsch** und gewinnt nicht.
4. **Frage:** Bei den Halsketten kann man die **Zahl** oder die **Liste aller Vertreter** wollen, bei den Färbungen **eine** Farbenzahl oder **vier**: die Antwort ändert den Gewinner.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Aufgabe**")
    family = st.selectbox("Familie", list(C.FAMILY_LABELS), key="family_select", help="Die sieben Zählaufgaben, auf denen die Verfahren nebeneinander laufen.")
    size = st.slider("Größenstufe", *bounds("size_slider"), key="size_slider", help="Stufe 1 ist die kleinste Größe der Familie; die größte Stufe hat jede Familie nur bis zu ihrer Zahl an Stufen (Dominosteine 7, Wege 8, Binärketten 6 …).")
    question = st.selectbox("Frage", list(C.QUESTIONS), key="question_select", help="Nur bei den Halsketten (Zahl oder Liste aller Halsketten) und den Färbungen (eine oder vier Farbenzahlen) wirksam.")
    st.markdown("**Budget**")
    budget = st.select_slider("Budget (Grundschritte)", options=list(C.BUDGET_CHOICES), key="budget_select", help="Obergrenze an Grundschritten je Verfahren; darüber bricht es ab.")

sync_query_params({"family_select": family, "size_slider": int(size), "budget_select": int(budget), "question_select": question})

settings = Settings(family, int(size), int(budget), question)
a = _analysis(settings)
for note in a.notes:
    st.info(note)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
c = a.cell
m1, m2, m3, m4 = st.columns(4)
m1.metric("Gewinner", c["winner"] or "keines", help="Das billigste Verfahren, dessen Ergebnis mit dem Ganzzahl-Referenzwert übereinstimmt.")
m2.metric("Schritte des Gewinners", "–" if c["winner_work"] is None else work_text(c["winner_work"]), help="Grundschritte (Einheit je Verfahren festgelegt).")
m3.metric("Ergebnis", "–" if c["value"] is None else (full_text(c["value"]) if isinstance(c["value"], int) and c["value"] < 10 ** 30 else big_text(c["value"]) if isinstance(c["value"], int) else ", ".join(big_text(x) for x in c["value"])), help="Zahl der Lösungen (bei vier Farbenzahlen die Werte für k = 2 bis 5).")
m4.metric("Regelwerk", a.rule_status, help=f"Empfehlung des Regelwerks aus Merkmalen: {a.rule or 'keines'}; verglichen mit dem Gewinner.")
st.plotly_chart(build_cell(c), width="stretch", key="main_chart")
st.caption("Schritte je Verfahren in dieser Zelle; die gestrichelte Linie ist das Budget. Verfahren über dem Budget haben abgebrochen.")
st.dataframe(method_rows(a), hide_index=True, width="stretch")

if st.button("📄 PDF der aktuellen Zelle erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="verfahrenswahl.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Welches Verfahren für welche Struktur, gemessen woran?")
verdict(verdict_answers(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

cells = _grid()

st.subheader("🔬 Experiment 1: Wer gewinnt wo?")
st.caption(f"Alle {len(cells)} Zellen (sieben Familien, je mehrere Größen) mit demselben Budget von {big_text(C.GRID_BUDGET)} Schritten: Gewinner, sein Aufwand, der Zweite mit seinem Faktor, falsche Verfahren und Verfahren über dem Budget.")
st.dataframe([{"Familie": r["Familie"], "Größe": r["Größe"], "Gewinner": r["Gewinner"], "Schritte": "–" if r["Schritte"] is None else work_text(r["Schritte"]),
               "Zweiter": "–" if r["zweiter"] is None else f"{r['zweiter'][0]} (Faktor {de(r['zweiter'][1], 1)}{', gleichwertig' if r['zweiter'][1] <= C.TIE_FACTOR else ''})",
               "falsch": ", ".join(r["falsch"]) or "–", "über Budget": ", ".join(r["über Budget"]) or "–"} for r in grid_rows(cells)], hide_index=True, width="stretch")
verdict(verdict_grid(cells))

st.markdown("---")

st.subheader("🔬 Experiment 2: Der Gewinner wechselt mit der Größe")
st.caption("Aufwand je Verfahren gegen die Größe in vier Familien (logarithmische Achse); fehlende Punkte sind über dem Budget.")
tabs = st.tabs(["F1 Binärketten", "F2 Surjektionen", "F4 Dominosteine", "F5 Wege"])
for tab, (key, title) in zip(tabs, (("F1", "Länge n"), ("F2", "n und k"), ("F4", "Brettgröße"), ("F5", "Gittergröße"))):
    with tab:
        st.plotly_chart(build_switch(switch_series(cells, key), title), width="stretch", key=f"switch_chart_{key}")
verdict(verdict_switch(cells))

st.markdown("---")

st.subheader("🔬 Experiment 3: Schnell, aber falsch")
st.caption("Kasteleyns Kosinusprodukt zählt Dominosteinparkettierungen in wenigen Schritten, aber in Gleitkomma (double). Gegen die ganzzahlige Profil-Rechnung zeigt sich, wo es falsch wird: bei Werten über 2⁵³ summieren sich Rundungsfehler im Produkt zu einer falschen ganzen Zahl.")
kas = _kasteleyn()
st.plotly_chart(build_kasteleyn(kas), width="stretch", key="kasteleyn_chart")
st.dataframe([{"Brett": f"{r['n']}×{r['n']}", "exakt (Profil-Rechnung)": full_text(r["exakt"]), "Kasteleyn (Gleitkomma)": full_text(r["Kasteleyn"]), "Abweichung": full_text(r["Abweichung"]), "über 2^53": "ja" if r["über 2^53"] else "nein",
               "Schritte exakt": big_text(r["Schritte exakt"]), "Schritte Kasteleyn": big_text(r["Schritte Kasteleyn"])} for r in kas], hide_index=True, width="stretch")
verdict(verdict_kasteleyn(kas))

st.markdown("---")

st.subheader("🔬 Experiment 4: Die Frage entscheidet")
st.caption("Dreifärbungen des Gitters: für **einen** Wert gewinnt die Transfermatrix, für **mehrere** Farbenzahlen das Tutte-Polynom (einmal gerechnet, dazu Spannbäume und Zuverlässigkeit). Halsketten: die **Zahl** durch Burnside gegen die **Liste** aller Halsketten durch FKM.")
qs = _question()
st.plotly_chart(build_question(qs), width="stretch", key="question_chart")
st.dataframe([{"Gitter": f"{r['n']}×{r['n']}", "Transfermatrix, k = 3": big_text(r["Transfermatrix k=3"]), "Transfermatrix, k = 2 bis 5": big_text(r["Transfermatrix vier"]), "Tutte-Frontier (einmal)": big_text(r["Tutte"]),
               "Faktor vier Werte": de(r["Faktor"], 1), "P(2), P(3), P(4), P(5)": ", ".join(big_text(x) for x in r["Werte"])} for r in qs["Färbungen"]], hide_index=True, width="stretch")
st.dataframe([{"Perlen n": r["n"], "Zahl der Halsketten": big_text(r["Zahl"]), "Burnside (Schritte)": big_text(r["Burnside"]), "FKM, Liste (Schritte)": big_text(r["FKM"]), "Faktor": big_text(round(r["Faktor"]))} for r in qs["Halsketten"]], hide_index=True, width="stretch")
verdict(verdict_question(qs))

st.markdown("---")

st.subheader("🔬 Experiment 5: Wo nichts mehr geht, und der Schätzer")
st.caption("Der Schätzer (Stück 15) gegen das beste exakte Verfahren: Aufwand für 5 Prozent Standardfehler. Bei der Teilmengensumme mit großen Gewichten geht exakt nichts mehr im Budget; auch der Schätzer braucht dort sehr viel oder trifft keine Lösung.")
est = estimator_rows(cells)
st.plotly_chart(build_estimator(est), width="stretch", key="estimator_chart")
st.dataframe([{"Familie": r["Familie"], "Größe": r["Größe"], "bestes exaktes Verfahren": r["bester exakter"] or "keines", "Schritte exakt": "–" if r["exakt"] is None else work_text(r["exakt"]),
               "Variationskoeffizient": "–" if r["Schätzer"] is None else de(r["cv"], 2), "Sondierungen für 5 %": "–" if r["nötig"] is None else big_text(r["nötig"]), "Schritte Schätzer": "nicht bestimmbar" if r["Schätzer"] is None else work_text(r["Schätzer"])} for r in est],
             hide_index=True, width="stretch")
verdict(verdict_estimator(est))

st.markdown("---")

st.subheader("🔬 Experiment 6: Lässt sich das Verfahren aus Merkmalen vorhersagen?")
st.caption("Ein Regelwerk aus Merkmalen der Struktur (zum Beispiel „Symmetrie: Burnside“, „Nebenbedingung auf Teilgraphen im Gitter: Frontier“) gegen die gemessenen Gewinner. Version 1 wurde mit Kenntnis der ersten Messreihe geschrieben, Version 2 passt eine Schwelle nach der Messung an.")
rr = rule_rows(cells)
st.dataframe([{"Version": f"Version {v}", "gleich": r["Zahlen"]["gleich"], "gleichwertig": r["Zahlen"]["gleichwertig"], "verfehlt": r["Zahlen"]["verfehlt"], "Verfehlungen": "; ".join(f"{k} {g}: Gewinner {w}, Regel {x}" for k, g, w, x in r["Verfehlungen"]) or "keine"} for v, r in rr.items()],
             hide_index=True, width="stretch")
verdict(verdict_rules(rr))

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🎲 Spielwiese: Aufwandsrechner für Surjektionen")
st.caption("Surjektionen von n Elementen auf k: die Aufwandsformeln der vier Verfahren, ohne zu rechnen (n bis 5.000). Tabelle: n · k Einträge, Siebformel: (k + 1) Potenzen, Potenz der erzeugenden Funktion: k Reihenprodukte, Aufzählen: k^n Abbildungen.")
p1, p2 = st.columns(2)
pn = p1.number_input("n (Elemente)", min_value=1, max_value=C.PLAY_N_MAX, value=C.PLAY_N_DEFAULT, step=1, key="play_n", help="Zahl der Elemente.")
pk = p2.number_input("k (Ziele)", min_value=1, max_value=C.PLAY_N_MAX, value=C.PLAY_K_DEFAULT, step=1, key="play_k", help="Zahl der Ziele, höchstens n.")
if int(pk) > int(pn):
    st.warning("k darf nicht größer als n sein: Surjektionen auf mehr Ziele als Elemente gibt es nicht.")
else:
    play = surjection_costs(int(pn), int(pk))
    st.plotly_chart(build_play(play), width="stretch", key="play_chart")
    verdict(verdict_play(play))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Grundschritte sind vergleichbar** | Jedes Verfahren zählt seine eigene Einheit (Tabelleneintrag, Zustand, Multiplikation, Besuch der Breitensuche); verglichen wird die Größenordnung. Bei Faktoren unter {int(C.TIE_FACTOR)} gilt: gleichwertig. Gemessene Zeit kann anders ordnen. | Experiment 1 |
| **Die sieben Familien sind repräsentativ** | Sie sind gewählt, nicht gezogen. Die Aussage lautet „in diesen Familien“, nicht „im Allgemeinen“. | Experiment 1 |
| **Das Budget ist fest** | Mit mehr Budget rücken die Wendepunkte (Teilmengensumme, Wege jenseits 10×10); das Budget von {big_text(C.GRID_BUDGET)} Schritten ist eine Annahme. | Ergebnis |
| **Das Regelwerk sagt voraus** | Version 1 wurde mit Kenntnis der ersten Messreihe geschrieben, die Trefferquote ist angepasst. Die Regeln beschreiben, sie sagen nicht voraus. | Experiment 6 |
| **Gleitkomma genügt** | Kasteleyns Formel in double ist ab 12×12 falsch; mit exakter Arithmetik (hier nicht gebaut) wäre sie es nicht. | Experiment 3 |
| **Eine Zahl genügt** | Wer die Liste aller Vertreter oder viele Parameter will, braucht andere Verfahren (FKM, Tutte-Polynom): der Gewinner hängt an der Frage. | Experiment 4 |
| **Die Verfahren sind optimal umgesetzt** | Reines Python der Demos; Meet-in-the-middle für die Teilmengensumme, Baumzerlegungen und Parallelisierung fehlen und könnten Wendepunkte verschieben. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Aufwandsmaß.** Jedes Verfahren $V$ zählt die Grundschritte $W_V(\text{Aufgabe})$ bis zu einem Budget $B$; $W_V = \infty$ bedeutet „über Budget“. Der **Gewinner** ist $\arg\min_V W_V$ unter den Verfahren, deren Ergebnis dem Ganzzahl-Referenzwert gleicht.

**Verfahren und ihre Aufwände.**
Tabelle für $a_n = a_{n-1} + a_{n-2}$: $n - 1$ Schritte; Matrixpotenz: $8 \cdot (\text{Bitlänge von } n+1 + \text{Zahl der gesetzten Bits von } n+1)$.
Surjektionen: $k! \, S(n, k)$ mit Tabelle $n k$ Schritte; Siebformel $\sum_{j=0}^{k} (-1)^j \binom{k}{j} (k-j)^n$ mit $k + 1$ Potenzen; $n! [z^n] (e^z - 1)^k$ mit $k (n+1)(n+2)/2$ Schritten.
Halsketten: Burnside $\frac{1}{n} \sum_{d \mid n} \varphi(n/d) \, k^d$; FKM gibt jede Halskette aus.
Dominosteine: Profil-Rechnung (Frontier) mit Zuständen je Zelle; Kasteleyn $\prod_{j=1}^{n/2} \prod_{l=1}^{n/2} \left( 4 \cos^2 \frac{\pi j}{n+1} + 4 \cos^2 \frac{\pi l}{n+1} \right)$ in Gleitkomma.
Wege: Frontier-Diagramm (Stück 13); Färbungen: Zeilen-Transfermatrix mit $\bigl(k (k-1)^{n-1}\bigr)^2 (n-1)$ Vergleichen, Tutte-Polynom (Stück 14) mit Summe der Zustände mal Koeffizientenzahl.

**Schätzer.** Für 5 Prozent Standardfehler braucht man $N \ge \mathrm{cv}^2 / 0{,}05^2$ Sondierungen (Stück 15); der Aufwand ist $N$ mal die Schritte einer Sondierung.

**Literatur** (Titel und Fundstelle aus dem Gedächtnis, nicht eingesehen). Die Verfahren und ihre Quellen stehen bei den Stücken 1 bis 15; zum Vergleich von Verfahren auf gemeinsamen Aufgaben vergleiche das letzte Stück der Linie *Inverse Probleme und Regularisierung* (`verfahrensvergleich-demo`).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
