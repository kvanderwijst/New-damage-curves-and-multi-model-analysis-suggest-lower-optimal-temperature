from plotly.subplots import make_subplots

from ..plot import subplot_damages


def fig_SI_with_vs_without_slr_adapt(data,):
    regions = ["R5.2ASIA", "R5.2EENA", "R5.2LAM", "R5.2MAF", "R5.2OECD"]
    fig = make_subplots(
        2,
        len(regions),
        column_titles=[
            "<b>R5-{}</b>".format(region[len("R5.2") :]) for region in regions
        ],
    )
    targets = ["rcp60", "rcp26"]
    selection = data[
        data["Variable"].str.startswith("Damage")
        & data["Target"].isin(targets)
        & (data["Discounting"] == "medium")
        & data["Model"].isin(["MIMOSA", "REMIND", "WITCH"])
    ].copy()
    selection["Discounting"] = list(selection["Discounting"])
    selection_average = (
        selection.groupby(
            [
                "Region",
                "Damage quantile",
                "SLR quantile",
                "SLR adaptation",
                "Target",
                "Discounting",
                "Variable",
                "Year",
            ]
        )
        .mean()
        .reset_index()
    )
    selection_average["Model"] = [
        "average_with_slr_adapt" if slr_adapt == "with" else "average_without_slr_adapt"
        for slr_adapt in selection_average["SLR adaptation"]
    ]
    selection_average["Scenario"] = ""
    _var_map = [
        ("Damage Cost|Non-SLR|%", -0.15, "Non-SLR"),
        ("Damage Cost|SLR|%", 0, "SLR"),
        ("Damage Cost|indirect|%", 0.4, "Indirect"),
    ]
    variables_lights_map = {
        "average_with_slr_adapt": _var_map,
        "average_without_slr_adapt": _var_map,
    }
    colormap = {
        "average_with_slr_adapt": "#00b9f1",
        "average_without_slr_adapt": "#30a2a6",
    }

    for i, target in enumerate(targets):
        for j, region in enumerate(regions):
            subplot_damages(
                selection_average,
                fig,
                i + 1,
                j + 1,
                years=["2100"],
                target=target,
                region=region,
                slr_adapt=None,
                models=list(variables_lights_map.keys()),
                showlegend=i + j == 0,
                custom_model_to_color=colormap,
                variables_lights_map=variables_lights_map,
            )

    fig.for_each_trace(
        lambda x: x.update(
            name=_map_replace(
                x.name,
                {
                    "Model:": "SLR adaptation:",
                    "average_with_slr_adapt": "With optimal adaptation",
                    "average_without_slr_adapt": "Without adaptation",
                },
            )
        )
    ).update_xaxes(showticklabels=False)

    (
        fig.update_layout(
            barmode="relative",
            legend={"traceorder": "normal", "y": 0.5},
            template="plotly_white",
            width=1180,
            height=100 + 250 * 2,
            margin_t=80,
            title="<b>c.</b> Effect of optimal vs no adaptation against SLR damages",
        )
        .update_yaxes(ticksuffix="%", matches="y")
        .update_yaxes(col=1, title="GDP loss", title_standoff=0)
        .update_xaxes(matches="x1")
    )

    return fig


def _map_replace(string, replace_dict):
    for str_from, str_to in replace_dict.items():
        string = string.replace(str_from, str_to)
    return string
