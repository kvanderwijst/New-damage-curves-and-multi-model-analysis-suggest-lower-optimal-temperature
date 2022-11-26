import itertools
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

from .plot import facet_plot, subplot_damages
from .colorutils import explanation_annotation_style


def general_fig(
    data, variable, title, slr_adapt="with", ignore_mimosa_combined=True,
):
    fig = facet_plot(
        data[
            (data["Variable"].isin([variable]))
            & (~data["Model"].str.contains("_combined") | (not ignore_mimosa_combined))
            & (data["Target"].isin(["rcp26", "rcp60"]))
            & (data["SLR adaptation"].isin([slr_adapt, "nodamages"]))
        ],
        title,
    )
    return fig


################
##
## Emissions
##
################


def fig_emissions(data, **kwargs):
    fig = general_fig(data, "Emissions|CO2", "Emissions", **kwargs)

    fig.for_each_trace(
        lambda t: t.update(visible="legendonly") if "nodamages" in t.name else t
    )
    return fig


################
##
## Damage costs
##
################


def fig_exp1_damages_fct(data, rcp, slr_adapt="with"):
    return facet_plot(
        data[
            (
                data["Variable"].isin(
                    [
                        "Damage Cost|%",
                        # "Damage Cost|SLR|%",
                        # "Damage Cost|Non-SLR|%",
                        "Damage Cost|direct+indirect|%",
                        # "Indirect Cost|%",
                    ]
                )
            )
            & (data["Damage quantile"] != "nodamages")
            & (data["Target"].isin([rcp]))
            & (data["SLR adaptation"].isin([slr_adapt, "?"]))
        ],
        "Damage costs ({})".format(rcp),
        facet_row="Damage quantile",
        line_dash="Variable",
        height=700,
    ).for_each_annotation(
        lambda ann: ann.update(
            text=("<b>Damage quantile: </b>" + ann.text)
            if ann.textangle == 90
            else ann.text
        )
    )


def fig_exp1_damages_bars(
    data,
    slr_adapt="without",
    rcps=["RCP 6.0", "RCP 2.6"],
    models=["WITCH", "MIMOSA", "MIMOSA_combined", "REMIND"],
    years=["2030", "2050", "2100"],
    with_scale=False,
):
    fig = make_subplots(
        len(rcps),
        3,
        column_titles=[f"<b>Damage quantile: {q}</b><br> " for q in [5, 50, 95]],
        row_titles=[f"<b>{rcp}</b><br> " for rcp in rcps],
        vertical_spacing=0.07,
    )
    kwargs = {
        "slr_adapt": slr_adapt,
        "years": years,
        "models": models,
    }
    for i, rcp in enumerate(rcps):
        rcp_target = rcp.replace(" ", "").lower().replace(".", "")
        subplot_damages(
            data, fig, i + 1, 1, rcp_target, "5", **kwargs, showlegend=i == 0
        )
        subplot_damages(
            data, fig, i + 1, 2, rcp_target, "50", **kwargs, showlegend=False
        )
        subplot_damages(
            data, fig, i + 1, 3, rcp_target, "95", **kwargs, showlegend=False
        )
    (
        fig.update_layout(
            barmode="relative",
            legend={"traceorder": "normal", "y": 0.5},
            template="plotly_white",
            width=1180,
            height=200 + 300 * len(rcps),
            margin_t=120,
            title=f"<b>Damage cost decomposition</b> ({slr_adapt} SLR adaptation, region: World)<br> ",
        )
        .update_yaxes(ticksuffix="%")
        .update_yaxes(row=1, matches="y1")
        .update_yaxes(row=2, matches="y4")
        .update_yaxes(col=1, title="GDP loss")  # , title_standoff=0)
        .update_xaxes(matches="x1")
    )
    if with_scale:
        low_range = [-0.759, 6.985]
        x0, dx = -0.03, 0.01

        line_style = {
            "type": "line",
            "xref": "paper",
            "line": {"width": 1, "color": "#BBB"},
        }
        for row in [1, 2]:
            yref = f"y{(row-1)*3+1}"
            for y_val in low_range:
                fig.add_shape(
                    yref=yref, x0=x0, x1=x0 + dx, y0=y_val, y1=y_val, **line_style
                )
            fig.add_shape(
                yref=yref, x0=x0, x1=x0, y0=low_range[0], y1=low_range[1], **line_style
            )
            middle = np.mean(low_range)
            fig.add_shape(
                yref=yref, x0=x0 - dx, x1=x0, y0=middle, y1=middle, **line_style
            )
        fig.add_shape(  # TODO: calculate the y-values relative to paper automatically for this
            yref="paper", x0=x0 - dx, x1=x0 - dx, y0=0.232, y1=0.627, **line_style
        )
    # if with_gap:
    #     fig.update_xaxes(range=[0.0, len(years) * (len(models) + 2) - 1])

    # fig.add_annotation(
    #     xref="paper",
    #     yref="y6",
    #     x=fig.layout["xaxis6"].domain[1],
    #     y=1,
    #     xshift=-3,
    #     yshift=0,
    #     ax=13,
    #     ay=0,
    #     xanchor="left",
    #     text="Combined SLR and<br>non-SLR damages<br>for REMIND",
    #     **explanation_annotation_style,
    # )

    return fig


def fig_exp1_damages_bars_policybrief(
    data,
    slr_adapt="without",
    rcps=["RCP 6.0", "RCP 2.6"],
    models=["WITCH", "MIMOSA", "REMIND"],
    years=["2030", "2050", "2100"],
    damage_quantile="50",
):
    fig = make_subplots(
        1,
        len(rcps),
        column_titles=[f"<b>{rcp}</b><br> " for rcp in rcps],
        vertical_spacing=0.07,
    )
    kwargs = {
        "slr_adapt": slr_adapt,
        "years": years,
        "models": models,
    }
    for i, rcp in enumerate(rcps):
        rcp_target = rcp.replace(" ", "").lower().replace(".", "")
        subplot_damages(
            data,
            fig,
            1,
            i + 1,
            rcp_target,
            damage_quantile,
            **kwargs,
            showlegend=i == 0,
        )
    (
        fig.update_layout(
            barmode="relative",
            legend={"traceorder": "normal", "y": 0.5},
            template="plotly_white",
            width=980,
            height=450,
            margin_t=120,
            title=f"<b>Damage cost decomposition</b> ({slr_adapt} SLR adaptation, region: World)<br> ",
        )
        .update_yaxes(ticksuffix="%")
        .update_yaxes(row=1, matches="y1")
        .update_yaxes(row=2, matches="y4")
        .update_yaxes(col=1, title="World GDP loss (%)", title_standoff=0)
        .update_xaxes(matches="x1")
    )
    # if with_gap:
    #     fig.update_xaxes(range=[0.0, len(years) * (len(models) + 2) - 1])

    return fig


################
##
## Policy costs
##
################


def fig_exp1_policycosts(data, **kwargs):
    fig_exp1_policycosts = general_fig(data, "Policy Cost|%", "Policy costs", **kwargs)
    return fig_exp1_policycosts


################
##
## GDP
##
################


def fig_exp1_gdp(data, **kwargs):

    gdp_ref = {
        "rcp26": [
            101081.500,
            142462.800,
            184463.700,
            228517.700,
            276536.000,
            330871.500,
            390057.800,
            454381.400,
            524725.400,
        ],
        "rcp60": [
            101244.500,
            143069.700,
            185954.600,
            231300.200,
            280515.400,
            336848.500,
            398498.200,
            465846.500,
            539332.400,
        ],
    }
    gdp_ref_index = list(range(2020, 2101, 10))

    fig_exp1_gdp = general_fig(data, "GDP|PPP", "GDP", **kwargs)
    fig_exp1_gdp.for_each_trace(
        lambda t: t.update(visible="legendonly") if "nodamages" in t.name else t
    )

    for i, ref_values in enumerate(gdp_ref.values()):
        fig_exp1_gdp.add_scatter(
            x=gdp_ref_index,
            y=ref_values,
            col=6,
            row=1 - i + 1,
            marker_color="#000",
            mode="markers",
            name="Reference (MESSAGE SSP2)",
            showlegend=i == 0,
            legendgroup="ref",
        )
    return fig_exp1_gdp


################
##
## Carbon price
##
################


def fig_exp1_cprice(data, **kwargs):
    fig = general_fig(data, "Price|Carbon", "Carbon price", **kwargs)
    fig.for_each_trace(
        lambda t: t.update(visible="legendonly") if "nodamages" in t.name else t
    )
    return fig

