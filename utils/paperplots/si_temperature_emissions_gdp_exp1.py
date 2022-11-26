"""
SI plot: temperature path, emissions and GDP for RCP6.0 and 2.6
with background shade for the range 5-95th damage quantile.
"""

from plotly.subplots import make_subplots
from .si_mitigcosts_cprice_rcp26 import add_ranges_and_median_lines


def fig_SI_temp_emissions_gdp(data):

    selection = data[
        (data["Region"] == "World")
        & (data["SLR adaptation"] != "without")
    ].astype({"Year": float})

    damage_quantiles = {
        "REMIND": ["5", "50", "95"],
        "WITCH": ["50", "5", "95"],
        "MIMOSA": ["50", "5", "95"],
    }

    variables = [
        ("Temperature|Global Mean", "a. Temperature", 1),
        ("Emissions|CO2", "b. Global CO<sub>2</sub> emissions", 1e-3),
        ("GDP|PPP", "c. Global GDP (PPP)", 1),
    ]

    column_titles = [f"<b>{name}</b>" for _, name, _ in variables]

    targets = [("RCP 6.0", "rcp60"), ("RCP 2.6", "rcp26")]

    fig = make_subplots(
        len(targets),
        3,
        column_titles=column_titles,
        row_titles=[f"<b>{target[0]}</b><br> " for target in targets],
    )

    for i, target in enumerate(targets):
        row = i + 1
        subselection = selection[selection["Target"] == target[1]]
        add_ranges_and_median_lines(
            fig, variables, subselection, damage_quantiles, row=row, showlegend=i == 0
        )

    fig.update_layout(
        template="plotly_white",
        legend={"y": 0.5, "font_size": 13, "traceorder": "reversed"},
        margin={"t": 40, "b": 20, "l": 44},
        width=1100,
        height=100 + 150 * len(targets),
    ).update_yaxes(col=1, ticksuffix="°C", matches="y1").update_yaxes(
        col=2, title="Gt CO<sub>2</sub>/yr", matches="y2"
    ).update_yaxes(
        col=3, title="billion US$2010/yr", matches="y3"
    ).update_yaxes(
        title_standoff=0
    )

    return fig
