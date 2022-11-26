"""
SI plot: global mitigation costs and global carbon prices per model for RCP2.6,
with background shade for the range 5-95th damage quantile.
"""

import numpy as np
from plotly.subplots import make_subplots

from .. import colorutils


def fig_SI_mitigcosts_cprice_rcp26(data, rcp="rcp26", fig=None):

    selection = data[
        (data["Region"] == "World")
        & (data["Target"] == rcp)
        & (data["SLR adaptation"] != "without")
    ].astype({"Year": float})

    damage_quantiles = {
        "WITCH": ["50", "5", "95"],
        "REMIND": ["nodamages", "5", "50", "95"],
        "MIMOSA": ["50", "5", "95"],
    }

    variables = [
        ("Policy Cost|%", "a. Mitigation costs", 1),
        # ("Damage Cost|%", "b. Damage costs", 1),
        ("Price|Carbon", "b. Carbon price", 1),
    ]

    column_titles = [f"<b>{name}</b>" for _, name, _ in variables]

    if fig is None:
        fig = make_subplots(1, len(variables), column_titles=column_titles)

    add_ranges_and_median_lines(
        fig, variables, selection, damage_quantiles, make_2020_zero=True
    )

    fig.update_layout(
        template="plotly_white",
        legend={"y": 0.5, "font_size": 13, "traceorder": "reversed"},
        margin={"t": 40, "b": 20, "l": 44},
        width=1100,
        height=350,
    ).update_yaxes(col=1, title="GDP loss", tickformat="p").update_yaxes(
        col=2, title="US$ / tCO<sub>2</sub>"
    ).update_yaxes(
        title_standoff=0
    )

    return fig


def add_ranges_and_median_lines(
    fig,
    variables,
    data_selection,
    damage_quantiles,
    row=1,
    showlegend=True,
    make_2020_zero=False,
):

    # Empty legend for background range
    fig.add_scatter(
        x=[None],
        y=[None],
        fill="toself",
        fillcolor="#000",
        opacity=0.2,
        name="<br>Range for 5-95th<br>damage quantile<br>",
        mode="lines",
        showlegend=showlegend,
        line={"width": 0, "color": "rgba(0,0,0,0)"},
    )

    for i, (variable, _, factor) in enumerate(variables):
        # For each variable, calculate the medium value (first element in damage_quantiles),
        # and full range (min-max of all damage_quantiles)

        for model, damage_quants in damage_quantiles.items():
            subselection = data_selection[
                (data_selection["Variable"] == variable)
                & (data_selection["Model"] == model)
                & (data_selection["Year"] <= 2100)
            ].copy()
            if make_2020_zero:
                subselection.loc[subselection["Year"] == 2020, "Value"] = 0.0
            subselection["Value"] *= factor
            color = colorutils.model_to_color[model]

            # 1. Background range
            values_range = subselection[
                subselection["Damage quantile"].isin(damage_quants)
            ]
            values_min = values_range.groupby("Year").min()
            values_max = values_range.groupby("Year").max()
            fig.add_scatter(
                x=np.concatenate([values_min.index, values_max.index[::-1]]),
                y=np.concatenate([values_min["Value"], values_max["Value"][::-1]]),
                fill="toself",
                fillcolor=color,
                opacity=0.2,
                line={"width": 0, "color": "rgba(0,0,0,0)"},
                showlegend=False,
                row=1,
                col=i + 1,
            )

            # 2. Medium line
            values = subselection[subselection["Damage quantile"] == damage_quants[0]]
            fig.add_scatter(
                x=values["Year"],
                y=values["Value"],
                name=model,
                showlegend=i == 0 and showlegend,
                mode="lines",
                line_color=color,
                row=row,
                col=i + 1,
            )

    return fig

