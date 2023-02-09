"""
CBA plot: emissions on top row, damage+mitigation costs on bottom row
"""

import pandas as pd

from plotly.subplots import make_subplots

from .. import colorutils, plot


def fig_cba_emissions_costs(
    data, slr_adapt="with", years=None, maxyear="2100", show_info_box=True
):

    if years is None:
        years = ["2030", "2050", "2100"]

    selection_fig3 = data[
        (data["Region"] == "World")
        & (data["Target"] == "cba")
        & (data["Discounting"] == "medium")
        & (data["SLR adaptation"] == slr_adapt)
        & (data["Year"] <= maxyear)
    ]

    damage_quantiles = ["5", "50", "95"]

    horizontal_spacing = 0.06

    column_titles = [f"<b>Damage quantile: {q}</b><br> <br> " for q in damage_quantiles]
    column_titles[0] += "<b>a.</b> Global CO<sub>2</sub> emissions (CBA path)" + (
        " " * 4
    )

    fig3 = make_subplots(
        2,
        3,
        horizontal_spacing=horizontal_spacing,
        vertical_spacing=0.18,
        column_titles=column_titles,
        subplot_titles=[
            None,
            None,
            None,
            "<b>b.</b> Cost decomposition{}<br> ".format(" " * 28),
            None,
            None,
        ],
    )
    source_data = []

    # 1. Emissions

    # 2. Add temperature labels
    extra_label_space = 0.06
    fig3.for_each_xaxis(
        lambda x: x.update(domain=[x.domain[0], x.domain[1] - extra_label_space]), row=1
    )
    ay_values = {
        "p5": {"MIMOSA": 9, "WITCH": 9, "REMIND": -9},
        "p50": {"MIMOSA": -6, "WITCH": -16, "REMIND": 12},
        "p95": {"MIMOSA": -13, "WITCH": -17, "REMIND": 13},
    }

    for i, damage_quantile in enumerate(damage_quantiles):

        subselection = selection_fig3[
            selection_fig3["Damage quantile"] == damage_quantile
        ]
        _source = emissions_and_temp_subplot(
            fig3,
            subselection,
            ay_values=ay_values[f"p{damage_quantile}"],
            col=i + 1,
            row=1,
            colormap=colorutils.model_to_color,
            maxyear=maxyear,
            show_info_box=show_info_box,
        )
        source_data += [_source]

    # 3. Add damages

    variables_lights_map = {
        "MIMOSA": [
            ("Policy Cost|%", [-0.25, -1, ".", 0.25], "Policy"),
            ("Damage Cost|Non-SLR|%", -0.15, "Damages: non-SLR"),
            ("Damage Cost|SLR|%", 0, "Damages: SLR"),
            ("Indirect Cost|%", 0.4, "Indirect"),
        ],
        "WITCH": [
            ("Policy Cost|%", [-0.15, -1, ".", 0.25], "Policy"),
            ("Damage Cost|Non-SLR|%", 0, "Damages: non-SLR"),
            ("Damage Cost|SLR|%", 0.2, "Damages: SLR"),
            ("Indirect Cost|%", 0.5, "Indirect"),
        ],
        "REMIND": [
            ("Policy Cost|%", [-0.35, -1, ".", 0.25], "Policy"),
            # ("Damage Cost|%", [0.05, -0.15, "/"], "Damage"),
            ("Damage Cost|Non-SLR|%", -0.2, "Damages: non-SLR"),
            ("Damage Cost|SLR|%", 0, "Damages: SLR"),
            ("Indirect Cost|%", 0.3, "Indirect"),
        ],
    }
    kwargs = {
        "slr_adapt": slr_adapt,
        "years": years,
        "models": ["MIMOSA", "WITCH", "REMIND"],
        "variables_lights_map": variables_lights_map,
    }
    for i, damage_quantile in enumerate(damage_quantiles):
        _source = plot.subplot_damages(
            selection_fig3,
            fig3,
            2,
            i + 1,
            "cba",
            damage_quantile,
            **kwargs,
            showlegend=i == 0,
            var_legend_title="<b>Cost type:</b>",
        )
        source_data += [_source]

    # Add explanation annotation for combined damages REMIND
    # if show_info_box:
    #     fig3.add_annotation(
    #         xref="paper",
    #         yref="y6",
    #         x=fig3.layout["xaxis6"].domain[1],
    #         y=2.8,
    #         xshift=-3,
    #         yshift=0,
    #         ax=13,
    #         ay=0,
    #         xanchor="left",
    #         text="Combined SLR and<br>non-SLR damages<br>for REMIND",
    #         **colorutils.explanation_annotation_style,
    #     )

    fig3.update_layout(
        width=900,
        height=630,
        barmode="relative",
        template="plotly_white",
        legend={"y": 0.5, "font_size": 13},
        margin={"t": 80, "b": 20, "l": 44},
    ).update_yaxes(row=1, matches="y1", dtick=10, range=[-9.11, 53.69]).update_yaxes(
        row=1,
        col=1,
        title={"text": "CO<sub>2</sub> emissions (Gt CO<sub>2</sub>)", "standoff": 0},
    ).update_yaxes(
        row=2, matches="y4", ticksuffix="%", autorange=True
    ).update_yaxes(
        row=2, col=1, title={"text": "Costs (share of GDP)", "standoff": 0}
    ).update_yaxes(
        zerolinecolor="#888", zerolinewidth=2
    )

    return fig3, pd.concat(source_data)


def emissions_and_temp_subplot(
    fig,
    subselection,
    ay_values,
    col,
    row,
    colormap=None,
    group_column="Model",
    maxyear="2100",
    show_info_box=True,
):
    if colormap is None:
        colormap = {}
    # 1. Emissions
    subselection_emissions = subselection[subselection["Variable"] == "Emissions|CO2"]
    for model, rows in subselection_emissions.groupby(group_column):
        fig.add_scatter(
            x=rows["Year"].astype(float),
            y=rows["Value"] / 1e3,
            line_color=colormap.get(model, "#555555"),
            name=model,
            showlegend=False,
            mode="lines",
            row=row,
            col=col,
        )

    subselection_temp = (
        subselection[
            (
                subselection["Variable"].isin(
                    ["Emissions|CO2", "Temperature|Global Mean"]
                )
            )
            & (subselection["Year"] == maxyear)
        ]
        .set_index([group_column, "Variable"])["Value"]
        .unstack("Variable")
        .reset_index()
    )
    for j, (_, datarow) in enumerate(
        subselection_temp.sort_values("Temperature|Global Mean").iterrows()
    ):
        color = colormap.get(datarow[group_column], "#555555")
        bgcolor = colorutils.lighten_hex(color, extra_lightness=-0.1)

        xaxis = fig.get_subplot(row, col).xaxis
        annotation_x = xaxis.domain[1]
        annotation_y = datarow["Emissions|CO2"] / 1e3
        fig.add_annotation(
            xref="paper",
            yref=xaxis.anchor,
            y=annotation_y,
            text=" {:.1f}°C ".format(datarow["Temperature|Global Mean"]),
            x=annotation_x,
            ax=12,
            ay=ay_values.get(datarow[group_column], 0),
            xanchor="left",
            arrowhead=6,
            arrowcolor=bgcolor,
            arrowwidth=2,
            bgcolor=bgcolor,
            bordercolor=bgcolor,
            font_size=13,
            font_color="white",
        )
        if datarow[group_column] == "REMIND" and col == 1 and show_info_box:
            fig.add_annotation(
                xref="paper",
                yref=xaxis.anchor,
                x=annotation_x,
                y=annotation_y,
                xshift=35,
                yshift=-37,
                ax=-25,
                ay=20,
                yanchor="top",
                text=f"Temp. in {maxyear} <br>using each<br>IAM's internal<br>climate model",
                **colorutils.explanation_annotation_style,
            )

    return subselection_emissions
