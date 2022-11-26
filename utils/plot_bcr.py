from typing import Optional
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from .plot import facet_plot, subplot_damages

from .colorutils import colors_PBL, lighten_hex, model_to_color


def fig_bcr(
    avoided_damages: pd.DataFrame,
    costs: pd.DataFrame,
    temperatures: Optional[pd.DataFrame],
    benefit_cost_ratios: pd.DataFrame,
    damage_quantile="50",
):

    if temperatures is None:
        with_temperature = False
        cols = 2
        col_costs_benefits, letter_costs_benefits = 1, "a"
        col_bcr, letter_bcr = 2, "b"
        column_widths = [0.6, 0.4]
    else:
        with_temperature = True
        cols = 3
        col_costs_benefits, letter_costs_benefits = 2, "b"
        col_bcr, letter_bcr = 3, "c"
        column_widths = None

    fig = make_subplots(
        1,
        cols,
        subplot_titles=(
            ["<b>a.</b> Temperature until 2150<br> "] if with_temperature else []
        )
        + [
            f"<b>{letter_costs_benefits}.</b> Resulting benefits and costs<br>over time",
            f"<b>{letter_bcr}.</b> Benefit Cost Ratios<br> ",
        ],
        horizontal_spacing=0.1,
        column_widths=column_widths,
    )

    if with_temperature:
        create_temperature_fig(
            fig,
            temperatures[
                (temperatures["Discounting"] == "medium")
                & (temperatures["Damage quantile"] == damage_quantile)
            ],
            row=1,
            col=1,
        )

    create_benefits_costs_over_time_fig(
        fig,
        avoided_damages[
            (avoided_damages["Discounting"] == "medium")
            & (avoided_damages["Damage quantile"] == damage_quantile)
        ],
        costs[
            (costs["Discounting"] == "medium")
            & (costs["Damage quantile"] == damage_quantile)
        ],
        row=1,
        col=col_costs_benefits,
    )

    create_bcr_bars_fig(
        fig,
        benefit_cost_ratios[benefit_cost_ratios["Damage quantile"] == damage_quantile],
        row=1,
        col=col_bcr,
    )

    fig.update_layout(
        template="plotly_white",
        width=900,
        height=350,
        margin={"t": 70, "r": 30, "b": 30, "l": 30},
        legend={
            "tracegroupgap": 0,
            "bgcolor": "#FFF",
            # "x": 0.03,
            "font_size": 13,
            "y": 0.5,
        },
    ).update_yaxes(zerolinecolor="#000", zerolinewidth=1, title_standoff=0)

    return fig


###############


def create_temperature_fig(fig: go.Figure, temperatures, row=1, col=1):
    targets, dashes = ["Baseline", "CBA"], ["solid", "dot"]
    for i, (target, dash) in enumerate(zip(targets, dashes)):
        for model, color in model_to_color.items():
            selection = temperatures[
                (temperatures["Model"] == model)
                & (temperatures["Target"] == target.lower())
            ]
            fig.add_scatter(
                x=selection["Year"].astype(float),
                y=selection["Value"],
                line={"color": color, "width": 3, "dash": dash},
                showlegend=False,
                name=f"{model}: {target}",
                legendgroup=model,
                mode="lines",
                row=row,
                col=col,
            )
    _fake_legend(fig, targets, dashes=dashes, row=row, col=col)
    fig.update_yaxes(row=row, col=col, ticksuffix="°C", title="Global warming")


def create_benefits_costs_over_time_fig(
    fig: go.Figure, avoided_damages, costs, row=1, col=2
):
    names, dfs, dashes = (
        ["Avoided damages", "Costs"],
        [avoided_damages, costs],
        ["solid", "dot"],
    )
    for name, df, dash in zip(names, dfs, dashes):
        for model, color in model_to_color.items():
            selection = df[df["Model"] == model]
            fig.add_scatter(
                x=selection["Year"].astype(float),
                y=selection["Value"],
                line={"color": color, "width": 3, "dash": dash},
                showlegend=False,
                name=model,
                legendgroup=model,
                mode="lines",
                row=row,
                col=col,
            )
    _fake_legend(fig, names, dashes=dashes, row=row, col=col)
    fig.update_yaxes(
        row=row, col=col, tickformat=".0%", title="Benefits and costs as % of GDP",
    )


def create_bcr_bars_fig(fig: go.Figure, bcr, row=1, col=3):
    for model, selection in bcr.sort_values("Model").groupby("Model"):
        color = model_to_color[model]
        fig.add_bar(
            x=selection["PRTP"],
            y=selection["Value"],
            marker_color=color,
            name=model,
            legendgroup=model,
            text=[f"{bcr:.1f}" for bcr in selection["Value"]],
            textposition='outside',
            textfont_color='#BBB',
            cliponaxis=False,
            row=row,
            col=col,
        )

    (
        fig.update_layout(barmode="group")
        .update_yaxes(row=row, col=col, ticksuffix=":1", title="BCR")
        .add_hline(y=1, col=col, row=row)
    )


###############


def _fake_legend(
    fig,
    labels,
    dashes=None,
    colors=None,
    row=1,
    col=1,
    y0=0.9,
    x0=0.05,
    dx=0.10,
    dy=0.085,
):
    dashes = ["solid"] * len(labels) if dashes is None else dashes
    colors = ["#444"] * len(labels) if colors is None else colors
    # Add fake legend
    xref = "{} domain".format(fig.get_subplot(row, col).yaxis.anchor)
    yref = "{} domain".format(fig.get_subplot(row, col).xaxis.anchor)

    for i, (label, dash, color) in enumerate(zip(labels, dashes, colors)):
        y = y0 - i * dy
        fig.add_shape(
            type="line",
            x0=x0,
            x1=x0 + dx,
            y0=y,
            y1=y,
            line={"color": color, "width": 3, "dash": dash},
            xref=xref,
            yref=yref,
        ).add_annotation(
            text=f" {label}",
            showarrow=False,
            xref=xref,
            yref=yref,
            x=x0 + dx,
            y=y,
            xanchor="left",
            yanchor="middle",
            font_size=14,
        )


# def fig_bcr(
#     costs_and_benefits_over_time: pd.DataFrame,
#     benefit_cost_ratios: pd.DataFrame,
#     endyear=2150,
#     show_prtp_range=False,
#     damage_p="p50",
# ):

#     fig = make_subplots(
#         1,
#         2,
#         subplot_titles=(
#             "<b>a.</b> Benefit and costs over time (CBA path)<br> ",
#             "<b>b.</b> Benefit Cost Ratio<br> ",
#         ),
#         column_widths=[0.7, 0.3],
#     )

#     ### a. Costs and benefits over time

#     # Only select chosen endyear and {damage_p} damage quantile
#     selection_over_time = costs_and_benefits_over_time[
#         (costs_and_benefits_over_time["endyear"] == endyear)
#         & (costs_and_benefits_over_time["damage_p"] == damage_p)
#     ].copy()
#     selection_over_time["Year"] = selection_over_time["Year"].astype(float)

#     common_prtp_range_kwargs = {
#         "legendgroup": "prtp_range",
#         "fill": "toself",
#         "line": {"color": "rgba(0,0,0)", "width": 0},
#         "opacity": 0.2,
#     }

#     for i, (variable, subselection) in enumerate(
#         selection_over_time.groupby("variable")
#     ):
#         subselection_by_prtp = {
#             prtp: rows for prtp, rows in subselection.groupby("prtp")
#         }

#         if i == 0:
#             color = colors_PBL[2]
#         elif i == 1:
#             color = colors_PBL[0]
#         else:
#             color = colors_PBL[2 + i]

#         if show_prtp_range:
#             fig.add_scatter(
#                 x=list(subselection_by_prtp[0.001]["Year"])
#                 + list(subselection_by_prtp[0.03]["Year"])[::-1],
#                 y=list(subselection_by_prtp[0.001]["Value"])
#                 + list(subselection_by_prtp[0.03]["Value"])[::-1],
#                 showlegend=False,
#                 fillcolor=color,
#                 **common_prtp_range_kwargs,
#             )

#         fig.add_scatter(
#             x=subselection_by_prtp[0.015]["Year"],
#             y=subselection_by_prtp[0.015]["Value"],
#             name=variable,
#             legendgroup=variable,
#             line={"color": color, "width": 3},
#         )

#     if show_prtp_range:
#         # Add legend item for PRTP range
#         fig.add_scatter(
#             x=[None],
#             y=[None],
#             mode="lines",
#             fillcolor="#000",
#             **common_prtp_range_kwargs,
#             name="PRTP range",
#         )

#     fig.update_yaxes(
#         col=1,
#         tickformat=".0%",
#         title="Benefits and costs as % of GDP",
#         title_standoff=0,
#     ).update_xaxes(dtick=10, col=1)

#     ### b. Benefit Cost Ratios

#     selection_bcr = benefit_cost_ratios[
#         (benefit_cost_ratios["endyear"] == str(endyear))
#         & (benefit_cost_ratios["damage_p"] == damage_p)
#     ]

#     for i, (prtp, subselection_bcr) in enumerate(selection_bcr.groupby("PRTP")):
#         row = subselection_bcr.iloc[0]
#         bcr = row["Benefit Cost Ratio"]

#         color = lighten_hex(colors_PBL[1], extra_lightness=0.1 * i ** 2)
#         fig.add_bar(
#             x=[f"<b>{prtp}</b>"],
#             y=[bcr],
#             marker_color=color,
#             showlegend=False,
#             text=f"<b>{bcr:.1f}:1</b>",
#             textposition="outside",
#             row=1,
#             col=2,
#         )

#     fig.add_annotation(
#         xref="paper",
#         yref="paper",
#         x=fig.get_subplot(1, 2).xaxis.domain[0],
#         y=0,
#         yshift=-19,
#         xanchor="right",
#         text="<b>PRTP:</b>",
#         showarrow=False,
#     )

#     fig.add_hline(y=1, col=2).update_yaxes(
#         col=2, range=[-0.124, 2.6], tickvals=[0, 0.5, 1, 1.5, 2]
#     )

#     fig.update_layout(
#         template="plotly_white",
#         width=900,
#         height=350,
#         margin={"t": 70, "r": 30, "b": 30, "l": 50},
#         legend={
#             "tracegroupgap": 5,
#             "bgcolor": "#FFF",
#             "x": 0.03,
#             "font_size": 13,
#             "y": 0.95,
#         },
#     )

#     return fig
