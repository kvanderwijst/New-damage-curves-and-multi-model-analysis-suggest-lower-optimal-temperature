"""
SI plot: stacked area chart with direct damages using separate damage function
(SLR vs non-SLR) with lines for combined damage function
"""

import numpy as np
from plotly.subplots import make_subplots

from .. import colorutils


def fig_SI_combined_vs_separate(data):
    selection = data[
        data["Model"].isin(["MIMOSA", "MIMOSA_combined"])
        & data["Variable"].isin(
            ["Damage Cost|SLR|%", "Damage Cost|Non-SLR|%", "Damage Cost|%"]
        )
        & (data["Region"] == "World")
        & data["Target"].isin(["rcp26", "rcp60"])
    ].sort_values(["Model", "Damage quantile", "Target", "Variable", "Year"])

    damage_quantiles = ["5", "50", "95"]
    targets = ["RCP 6.0", "RCP 2.6"]
    fig = make_subplots(
        2,
        3,
        shared_xaxes=True,
        shared_yaxes=True,
        column_titles=[f"<b>Damage quantile: {q}</b><br> " for q in damage_quantiles],
        row_titles=[f"<b>{t}</b><br> " for t in targets],
        horizontal_spacing=0.04,
        vertical_spacing=0.08,
    )

    def pos_neg_area(fig, x, y, stackgroup, showlegend, **kwargs):
        for is_pos, suffix in [(True, "_pos"), (False, "_neg")]:
            clipped = (
                np.clip(y, a_min=0, a_max=np.inf)
                if is_pos
                else np.clip(y, a_min=-np.inf, a_max=0)
            )
            fig.add_scatter(
                x=x,
                y=clipped,
                stackgroup=f"{stackgroup}{suffix}",
                showlegend=showlegend and is_pos,
                **kwargs,
            )

    for i, q in enumerate(damage_quantiles):
        for j, target in enumerate(targets):
            subselection = lambda slr_adapt: selection[
                (selection["Damage quantile"] == q)
                & (
                    selection["Target"]
                    == target.replace(" ", "").replace(".", "").lower()
                )
                & (selection["SLR adaptation"] == slr_adapt)
            ]
            subselection_withadapt = subselection("with")
            subselection_withoutadapt = subselection("without")

            # 1. Add area plot for SLR/non-SLR separate damages
            for variable, name, lighten in [
                ("Non-SLR", "Non-SLR", -0.15),
                ("SLR", "SLR (with adapt)", 0),
                ("extra_without_adapt", "SLR (extra costs w/o adapt)", 0.3),
            ]:
                model = "MIMOSA"
                if variable == "extra_without_adapt":
                    values_with = subselection_withadapt[
                        (subselection_withadapt["Model"] == model)
                        & (subselection_withadapt["Variable"] == "Damage Cost|SLR|%")
                    ]
                    values_without = subselection_withoutadapt[
                        (subselection_withoutadapt["Model"] == model)
                        & (subselection_withoutadapt["Variable"] == "Damage Cost|SLR|%")
                    ]
                    values = values_with.copy()
                    values["Value"] = (
                        values_without["Value"].values - values_with["Value"].values
                    )
                    color = colorutils.colors_PBL[13]
                else:
                    values = subselection_withadapt[
                        (subselection_withadapt["Model"] == model)
                        & (
                            subselection_withadapt["Variable"]
                            == f"Damage Cost|{variable}|%"
                        )
                    ]
                    color = colorutils.lighten_hex(
                        colorutils.model_to_color[model], lighten
                    )
                pos_neg_area(
                    fig,
                    x=values["Year"].astype(float),
                    y=values["Value"],
                    row=j + 1,
                    col=i + 1,
                    stackgroup="separate",
                    name=name,
                    showlegend=i + j == 0,
                    legendgroup=variable,
                    fillcolor=color,
                    line={"color": color, "width": 0},
                )

            if i + j == 0:
                fig.add_bar(x=[None], y=[None], opacity=0, name="<br><b>Separate:</b>")

            # 2. Add line for combined damages
            model = "MIMOSA_combined"
            for slr_adapt, dash in [("with", "solid"), ("without", "dot")]:
                values = subselection(slr_adapt)
                values_comb = values[
                    (values["Model"] == model) & (values["Variable"] == "Damage Cost|%")
                ].set_index("Year")["Value"]
                slr_adapt_str = "with" if slr_adapt == "with" else "w/o"
                name = f"Combined ({slr_adapt_str} SLR adapt)"
                fig.add_scatter(
                    x=values_comb.index.astype(float),
                    y=values_comb.values,
                    row=j + 1,
                    col=i + 1,
                    name=name,
                    showlegend=i + j == 0,
                    legendgroup=name,
                    line={
                        "color": colorutils.model_to_color[model],
                        "width": 2,
                        "dash": dash,
                    },
                    mode="lines",
                )

                # 3. Add gap between combined/separate
                values_sep = values[
                    (values["Model"] == "MIMOSA")
                    & (values["Variable"] == "Damage Cost|%")
                ].set_index("Year")["Value"]
                dx = 1.5 if slr_adapt == "with" or (i > 0 and j == 0) else 3.5
                fig.add_scatter(
                    x=[2100 + dx, 2100 + dx],
                    y=[values_comb["2100"], values_sep["2100"]],
                    row=j + 1,
                    col=i + 1,
                    name=name + " gap",
                    showlegend=False,
                    legendgroup=name,
                    line={"color": "#888", "width": 2, "dash": dash},
                    mode="lines",
                )
                fig.add_annotation(
                    x=2100 + dx,
                    y=values_comb["2100"],
                    ax=0,
                    ay=-6,
                    arrowhead=2,
                    arrowsize=15,
                    arrowwidth=0.1,
                    arrowcolor="#888",
                    text="",
                    row=j + 1,
                    col=i + 1,
                    # xref=fig.get_subplot(j + 1, i + 1).yaxis.anchor,
                    # yref=fig.get_subplot(j + 1, i + 1).xaxis.anchor,
                    yshift=-3,
                )

            if i + j == 0:
                fig.add_bar(x=[None], y=[None], opacity=0, name="<br><b>Combined:</b>")

    fig.update_layout(
        template="plotly_white",
        height=500,
        width=1100,
        margin={"t": 50, "b": 20, "l": 30},
        legend={"y": 0.5, "x": 1.04, "font_size": 13, "traceorder": "reversed"},
    ).update_yaxes(
        tickformat="p", title="Direct damage costs<br>(share of GDP)", col=1
    ).update_xaxes(
        range=[2020, 2105]
    ).update_yaxes(
        autorange=True
    )

    return fig
