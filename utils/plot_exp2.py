from plotly.subplots import make_subplots
from .plot import facet_plot, subplot_damages


def general_fig(
    data,
    variable,
    title,
    slr_adapt="with",
    discounting="medium",
    line_dash="Variable",
    facet_row="Damage quantile",
    **kwargs,
):
    if isinstance(variable, str):
        variables = [variable]
    else:
        variables = variable

    if isinstance(discounting, str):
        discountings = [discounting]
    else:
        discountings = discounting
    fig = facet_plot(
        data[
            (data["Variable"].isin(variables))
            & (data["Target"].isin(["cba"]))
            & (data["SLR adaptation"] == slr_adapt)
            & (data["Discounting"].isin(discountings))
        ],
        title,
        facet_row=facet_row,
        line_dash=line_dash,
        height=700,
        **kwargs,
    ).for_each_annotation(
        lambda ann: ann.update(
            text=("<b>Damage quantile: </b>" + ann.text)
            if ann.textangle == 90
            else ann.text
        )
    )
    return fig


def fig_exp2_temperature(data, **kwargs):
    fig = (
        general_fig(
            data,
            "Temperature|Global Mean",
            "Temperature (CBA, medium vs high discounting)",
            line_dash="Discounting",
            line_dash_map={"medium": "solid", "high": "dot", "low": "dash"},
            discounting=["low", "medium", "high"],
            **kwargs,
        )
        .update_yaxes(ticksuffix="°C")
        .for_each_trace(
            lambda trace: trace.update(
                visible="legendonly" if "medium" not in trace.name else None
            )
        )
    )
    return fig


def fig_exp2_emissions(data, **kwargs):
    fig = general_fig(
        data, "Emissions|CO2", "Emissions (CBA, medium discounting)", **kwargs
    )
    return fig


def fig_exp2_costs(data, **kwargs):
    fig = general_fig(
        data,
        ["Policy Cost|%", "Damage Cost|%", "Indirect Cost|%"],
        "Costs (CBA, medium discounting)",
        **kwargs,
    )
    fig.for_each_trace(
        lambda t: t.update(visible="legendonly") if "Indirect" in t.name else t
    )
    return fig


def fig_exp2_damages_bars(data, slr_adapt="without", discounting="medium"):
    selection = data[data["Discounting"] == discounting]
    fig = make_subplots(
        1,
        3,
        column_titles=[f"<b>Damage quantile: {q}</b><br> " for q in [5, 50, 95]],
        # row_titles=[f"<b>{rcp}</b><br> " for rcp in rcps],
    )
    years = ["2030", "2050", "2100"]
    models = ["MIMOSA", "REMIND"]
    variables_lights_map = {
        "MIMOSA": [
            ("Policy Cost|%", -0.3, "Policy"),
            ("Damage Cost|Non-SLR|%", -0.15, "Damages: non-SLR"),
            ("Damage Cost|SLR|%", 0, "Damages: SLR"),
            ("Indirect Cost|%", 0.4, "Indirect"),
        ],
        "REMIND": [
            ("Policy Cost|%", -0.35, "Policy"),
            ("Damage Cost|%", [0.05, -0.15], "Damage"),
            ("Indirect Cost|%", 0.3, "Indirect"),
        ],
    }
    variables_lights_map["WITCH"] = variables_lights_map["MIMOSA"]
    kwargs = {
        "slr_adapt": slr_adapt,
        "years": years,
        "models": models,
        "variables_lights_map": variables_lights_map,
    }
    subplot_damages(selection, fig, 1, 1, "cba", "5", **kwargs)
    subplot_damages(selection, fig, 1, 2, "cba", "50", **kwargs, showlegend=False)
    subplot_damages(selection, fig, 1, 3, "cba", "95", **kwargs, showlegend=False)
    (
        fig.update_layout(
            barmode="relative",
            legend={"traceorder": "normal", "y": 0.5},
            template="plotly_white",
            width=1000,
            height=200 + 300 * 1,
            margin_t=120,
            title=f"<b>Cost decomposition</b> ({slr_adapt} SLR adaptation, region: World)<br> ",
        )
        .update_yaxes(ticksuffix="%")
        .update_yaxes(row=1, matches="y1")
        .update_yaxes(row=2, matches="y4")
        .update_yaxes(col=1, title="GDP loss", title_standoff=0)
        .update_xaxes(matches="x1")
    )

    return fig


def fig_exp2_gdp(data, **kwargs):
    fig = general_fig(data, "GDP|PPP", "GDP (CBA, medium discounting)", **kwargs)
    return fig


def fig_exp2_cprice(data, **kwargs):
    fig = general_fig(
        data, "Price|Carbon", "Carbon price (CBA, medium discounting)", **kwargs
    )
    return fig
