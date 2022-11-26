"""
CBA plot: scatter plot with optimal temperature in 2100, with SLR adaptation as symbols
"""

import plotly.express as px
import numpy as np

from .. import colorutils


def fig_cba_temperature_sensitivity(
    data, models=["MIMOSA", "REMIND", "WITCH"], with_peak=False
):

    selection_all_years = (
        data[
            (data["Target"] == "cba")
            & (data["Variable"] == "Temperature|Global Mean")
            & (data["Year"] <= "2100")
            & (data["Damage quantile"] != "nodamages")
            & (data["Model"].isin(models))
        ]
        .sort_values(["Discounting", "Model", "SLR adaptation"])
        .copy()
    )

    selection_all_years["Discounting"] = selection_all_years["Discounting"].replace(
        {"low": "0.1%", "medium": "1.5%", "high": "3%"}
    )

    selection = selection_all_years[selection_all_years["Year"] == "2100"]
    groups = ["Model", "Damage quantile", "SLR adaptation", "Discounting"]
    selection_peak = (
        selection_all_years.sort_values(groups)
        .groupby(groups)["Value"]
        .max()
        .reset_index()
    )

    symbols = {"with": "circle", "without": "diamond"}

    def _create_fig(df):
        ylabel = (
            "Temperature<br>(rel. to pre-industrial)"
            if with_peak
            else "Temperature in 2100<br>(rel. to pre-industrial)"
        )
        return (
            px.scatter(
                df,
                facet_col="Damage quantile",
                y="Value",
                symbol_map=symbols,
                x="Discounting",
                color="Model",
                color_discrete_map=colorutils.model_to_color,
                symbol="SLR adaptation",
                template="plotly_white",
            )
            .update_yaxes(dtick=0.5, ticksuffix="°C", title=ylabel, col=1,)
            .update_xaxes(
                showgrid=False,
                zeroline=False,
                tickvals=[0, 1, 2],
                ticktext=["0.1%", "1.5%", "3%"],
                title="Discounting (PRTP)",
            )
        )

    fig_cba_temps = _create_fig(selection)

    if with_peak:
        for trace in _create_fig(selection_peak).data:
            fig_cba_temps.add_trace(
                trace.update(marker_symbol=trace.marker.symbol + "-open", opacity=0.5)
            )

    def _shift(name, dx=0.15):
        if "MIMOSA" in name:
            return -dx
        if "WITCH" in name:
            return dx
        return 0.0

    fig_cba_temps.for_each_trace(
        lambda t: t.update(
            x=np.array([{"0.1%": 0, "1.5%": 1, "3%": 2,}[x] for x in t.x])
            + _shift(t.name)
        )
    )

    # Add new legend:
    fig_cba_temps.update_traces(showlegend=False, marker_size=8).update_layout(
        legend_title=""
    )

    fig_cba_temps.add_scatter(x=[None], y=[None], opacity=0, name="<b>Model:</b>")
    for model in models:
        fig_cba_temps.add_scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker={"color": colorutils.model_to_color[model], "size": 8},
            name=model,
        )

    fig_cba_temps.add_scatter(
        x=[None], y=[None], opacity=0, name="<br><b>SLR adaption:</b>"
    )
    for slr_adapt in ["with", "without"]:
        fig_cba_temps.add_scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker={"color": "#666", "size": 8, "symbol": symbols[slr_adapt]},
            name=slr_adapt.capitalize(),
        )

    if with_peak:
        fig_cba_temps.add_scatter(
            x=[None], y=[None], opacity=0, name="<br><b>Variable:</b>"
        )
        for symbol, name in [
            ("circle", "Temperature in 2100"),
            ("circle-open", "Peak temperature"),
        ]:
            fig_cba_temps.add_scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker={"color": "#666", "size": 8, "symbol": symbol},
                name=name,
            )

    ymin = 0.9

    for col in [1, 2, 3]:
        fig_cba_temps.add_hline(
            y=2, row=1, col=col, line={"color": "#AAA"},
        )
    # fig_cba_temps.for_each_yaxis(
    #     lambda axis: fig_cba_temps.add_shape(
    #         type="rect",
    #         layer="below",
    #         x0=0,
    #         x1=1,
    #         xref=f"{axis.anchor} domain",
    #         yref=axis.anchor.replace("x", "y"),
    #         y0=ymin,
    #         y1=2,
    #         fillcolor="rgba(150,150,200, 0.075)",
    #         line_width=0,
    #     )
    # )

    for x in [0, 2]:
        fig_cba_temps.for_each_xaxis(
            lambda axis: fig_cba_temps.add_shape(
                type="rect",
                layer="below",
                y0=0,
                y1=1,
                yref=f"{axis.anchor} domain",
                xref=axis.anchor.replace("y", "x"),
                x0=-0.5 + x,
                x1=0.5 + x,
                fillcolor="rgba(150,150,200, 0.075)",
                line_width=0,
            )
        )

    (
        fig_cba_temps.update_layout(
            width=900, legend={"y": 0.5, "font_size": 13}, font_size=13, height=368
        )
        .update_xaxes(range=[-0.4, 2.4])
        .update_yaxes(range=[ymin, 3.65])
        .for_each_annotation(
            lambda ann: ann.update(
                text=("<b>Damage quantile: {}</b><br> ".format(ann.text.split("=")[1]))
                if "Damage quantile" in ann.text
                else ann.text,
                font_size=15,
            )
        )
    )
    if with_peak:
        fig_cba_temps.update_layout(height=390)
    return fig_cba_temps
