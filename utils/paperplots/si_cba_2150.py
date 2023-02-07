"""
SI plot: temperature, damages and policy costs until 2150 for the CBA runs
"""

from plotly.subplots import make_subplots
from .si_mitigcosts_cprice_rcp26 import add_ranges_and_median_lines


def fig_SI_cba_2150(data):

    selection = data[
        (data["Region"] == "World")
        & (data["Target"] == "cba")
        & (data["SLR adaptation"] == "with")
        & (data["Discounting"] == "medium")
    ].astype({"Year": float})

    damage_quantiles = {
        "REMIND": ["5", "50", "95"],
        "WITCH": ["50", "5", "95"],
        "MIMOSA": ["50", "5", "95"],
    }

    variables = [
        ("Temperature|Global Mean", "a. Temperature", 1),
        ("Damage Cost|%", "b. Damage costs", 1),
        ("Policy Cost|%", "c. Policy costs", 1),
    ]

    column_titles = [f"<b>{name}</b>" for _, name, _ in variables]

    damage_quantiles = ["5", "50", "95"]

    fig = make_subplots(
        len(damage_quantiles),
        len(variables),
        column_titles=column_titles,
        row_titles=[
            f"<b>Damage quantile: {damage_q}</b><br> " for damage_q in damage_quantiles
        ],
    )

    for i, damage_q in enumerate(damage_quantiles):
        row = i + 1
        add_ranges_and_median_lines(
            fig,
            variables,
            selection,
            {m: [damage_q, damage_q, damage_q] for m in ["REMIND", "WITCH", "MIMOSA"]},
            end_year=2150,
            row=row,
            showlegend=i == 0,
            showrangelegend=False,
        )

    fig.update_layout(
        template="plotly_white",
        legend={"y": 0.5, "font_size": 13, "traceorder": "reversed"},
        margin={"t": 40, "b": 20, "l": 44},
        width=1100,
        height=100 + 150 * len(damage_quantiles),
    ).update_yaxes(col=1, ticksuffix="°C", matches="y1", range=[0.9, 4.1]).update_yaxes(
        col=2, tickformat="p", title="% of GDP", matches="y2", range=[-0.0075, 0.05],
    ).update_yaxes(
        col=3, tickformat="p", title="% of GDP", matches="y3", range=[-0.0075, 0.05]
    ).update_yaxes(
        title_standoff=0
    )

    return fig
