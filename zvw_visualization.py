"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import zvw_constants as C

METHOD_COLORS = {"Aufzählen": C.COLOR_ALL, "Aufzählen aller Wörter": C.COLOR_ALL, "Tabelle": C.COLOR_MAIN, "Tabelle (EF)": C.COLOR_MAIN, "Stirling-Tabelle": C.COLOR_MAIN, "Matrixpotenz": C.COLOR_LINE, "Siebformel": C.COLOR_SAND,
                 "EF-Potenz": "#8e5ea2", "FKM": "#5a8f29", "Burnside": C.COLOR_LINE, "Profil-Rechnung": C.COLOR_MAIN, "Kasteleyn": C.COLOR_WARN, "Frontier-Diagramm": C.COLOR_MAIN, "Transfermatrix": C.COLOR_LINE,
                 "Tutte-Frontier": C.COLOR_SAND}


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_cell(cell: dict):
    """Schritte je Verfahren in der gewählten Zelle (logarithmische Achse); über dem Budget: Balken bis zum Budget in Rot, falsche Verfahren hell."""
    fig = go.Figure()
    names, ys, colors = [], [], []
    for r in cell["methods"]:
        if r["Schritte"] is None:
            continue
        names.append(r["Verfahren"])
        ys.append(r["Schritte"])
        colors.append(C.COLOR_WARN if r["Status"] == "über Budget" else (C.COLOR_SAND if r["Status"] == "falsch" else C.COLOR_MAIN))
    fig.add_trace(go.Bar(x=names, y=ys, marker_color=colors, name="Schritte", showlegend=False))
    fig.add_hline(y=cell["budget"], line=dict(color=C.COLOR_WARN, dash="dash"), annotation_text="Budget", annotation_position="top left")
    fig.update_yaxes(title_text="Grundschritte (rot: über dem Budget, gelb: falsch)", type="log")
    return _base(fig, 320)


def build_switch(series: dict, title: str):
    """Aufwand je Verfahren gegen die Größe einer Familie (logarithmische Achse; fehlende Punkte: über Budget)."""
    fig = go.Figure()
    for name, points in series.items():
        fig.add_trace(go.Scatter(x=[p[0] for p in points], y=[p[1] for p in points], mode="lines+markers", name=name, line=dict(color=METHOD_COLORS.get(name)), connectgaps=False))
    fig.update_xaxes(title_text=title, type="category")
    fig.update_yaxes(title_text="Grundschritte", type="log")
    return _base(fig, 320)


def build_kasteleyn(rows: list):
    """Schritte der Profil-Rechnung gegen Kasteleyns Formel je Brettgröße (logarithmische Achse); falsche Bretter sind in der Beschriftung markiert."""
    fig = go.Figure()
    xs = [f"{r['n']}×{r['n']}" + (" ✗" if r["Abweichung"] != 0 else "") for r in rows]
    fig.add_trace(go.Bar(x=xs, y=[r["Schritte exakt"] for r in rows], name="Profil-Rechnung (ganzzahlig)", marker_color=C.COLOR_MAIN))
    fig.add_trace(go.Bar(x=xs, y=[r["Schritte Kasteleyn"] for r in rows], name="Kasteleyn (Gleitkomma)", marker_color=C.COLOR_WARN))
    fig.update_yaxes(title_text="Grundschritte", type="log")
    fig.update_layout(barmode="group")
    return _base(fig, 320)


def build_question(res: dict):
    """Färbungen: Transfermatrix für vier Farbenzahlen gegen das Tutte-Polynom je Gittergröße (logarithmische Achse)."""
    rows = res["Färbungen"]
    fig = go.Figure()
    xs = [f"{r['n']}×{r['n']}" for r in rows]
    fig.add_trace(go.Bar(x=xs, y=[r["Transfermatrix k=3"] for r in rows], name="Transfermatrix, eine Farbenzahl", marker_color=C.COLOR_LINE))
    fig.add_trace(go.Bar(x=xs, y=[r["Transfermatrix vier"] for r in rows], name="Transfermatrix, vier Farbenzahlen", marker_color=C.COLOR_WARN))
    fig.add_trace(go.Bar(x=xs, y=[r["Tutte"] for r in rows], name="Tutte-Frontier (einmal, alle Farbenzahlen)", marker_color=C.COLOR_SAND))
    fig.update_yaxes(title_text="Grundschritte", type="log")
    fig.update_layout(barmode="group")
    return _base(fig, 340)


def build_estimator(rows: list):
    """Bestes exaktes Verfahren gegen den Schätzer (5 Prozent Standardfehler) je Zelle (logarithmische Achse)."""
    rows = [r for r in rows if r["exakt"] is not None and r["Schätzer"] is not None]
    fig = go.Figure()
    xs = [f"{r['Familie']} {r['Größe']}" for r in rows]
    fig.add_trace(go.Bar(x=xs, y=[r["exakt"] for r in rows], name="bestes exaktes Verfahren", marker_color=C.COLOR_MAIN))
    fig.add_trace(go.Bar(x=xs, y=[r["Schätzer"] for r in rows], name="Schätzer", marker_color=C.COLOR_WARN))
    fig.update_yaxes(title_text="Grundschritte", type="log")
    fig.update_layout(barmode="group")
    return _base(fig, 360)


def build_play(res: dict):
    """Aufwand der Verfahren für Surjektionen (logarithmische Achse; das Aufzählen fehlt, wenn die Zahl zu groß ist)."""
    fig = go.Figure()
    costs = res["Kosten"]
    names = [m for m, c in costs.items() if c is not None and c.bit_length() < 1000]
    fig.add_trace(go.Bar(x=names, y=[float(costs[m]) for m in names], marker_color=[METHOD_COLORS.get(m) for m in names], showlegend=False))
    fig.update_yaxes(title_text="Grundschritte", type="log")
    return _base(fig, 280)
