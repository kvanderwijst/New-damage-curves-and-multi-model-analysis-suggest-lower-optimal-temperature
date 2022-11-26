"""
Plot utils:
 - facet plot
"""

import plotly.express as px

from .colorutils import lighten_hex, model_to_color


def facet_plot(
    data,
    title="",
    color="Model",
    line_dash="Damage quantile",
    facet_col="Region",
    facet_row="Target",
    height=500,
    line_dash_map=None,
    **kwargs,
):
    if line_dash_map is None:
        line_dash_map = (
            {"5": "dot", "50": "solid", "95": "dash", "nodamages": "dashdot"}
            if line_dash == "Damage quantile"
            else None
        )

    fig = px.line(
        data,
        x="Year",
        y="Value",
        color=color,
        line_dash=line_dash,
        facet_col=facet_col,
        facet_row=facet_row,
        width=1100,
        render_mode="svg",
        line_dash_map=line_dash_map,
        color_discrete_map=(model_to_color if color == "Model" else None),
        template="plotly_white",
        **kwargs,
    )

    var_names = data["Variable"].sort_values().unique()
    var_name = ",<br>".join(var_names)
    if "%" in var_name:
        fig.update_yaxes(tickformat="%")
    fig.update_yaxes(col=1, title={"text": var_name, "standoff": 0})
    if facet_row == "Variable":
        for i, name in enumerate(var_names):
            fig.update_yaxes(col=1, row=i + 1, title_text=name)

    (
        fig.update_xaxes(title="")
        .for_each_annotation(
            lambda ann: ann.update(text="<b>{}</b>".format(ann.text.split("=")[1]))
        )
        .update_layout(
            legend_y=0.5,
            height=height,
            margin={"t": 70, "r": 30, "b": 30, "l": 50},
            title=f"<b>{title}</b>",
        )
    )

    return fig


def lighten_list_to_pattern_color(lighten, model_color):
    if isinstance(lighten, list):  # Use pattern
        lighten_bg = lighten[0]
        fgcolor = (
            lighten_hex(model_color, extra_lightness=lighten[1])
            if lighten[1] > -1
            else "#000000"
        )
        pattern = {
            "shape": lighten[2] if len(lighten) > 2 else "/",
            "fgcolor": fgcolor,
            "fgopacity": 1,
            "solidity": lighten[3] if len(lighten) > 3 else 0.5,
        }
    else:
        lighten_bg = lighten
        pattern = None
    color = lighten_hex(model_color, extra_lightness=lighten_bg)
    return color, pattern


## Damage bars
def subplot_damages(
    data,
    fig,
    row=1,
    col=1,
    target="rcp26",
    damage_quantile="50",
    region="World",
    slr_adapt="without",
    years=["2030", "2050", "2070", "2100"],
    showlegend=True,
    models=["MIMOSA", "WITCH", "REMIND"],
    variables_lights_map=None,
    discounting="medium",
    custom_model_to_color=None,
    var_legend_title="<b>Damage type:</b>",
):
    if custom_model_to_color is None:
        custom_model_to_color = model_to_color

    selection = data[
        (data["Target"] == target)
        & (data["Damage quantile"] == damage_quantile)
        & (data["Region"] == region)
        & (data["Discounting"] == discounting)
    ]
    if slr_adapt is not None:
        selection = selection[selection["SLR adaptation"] == slr_adapt]

    if variables_lights_map is None:
        variables_lights_map = {
            "MIMOSA": [
                ("Damage Cost|Non-SLR|%", -0.15, "Non-SLR"),
                ("Damage Cost|SLR|%", 0, "SLR"),
                ("Damage Cost|indirect|%", 0.4, "Indirect"),
            ],
            "REMIND": [
                ("Damage Cost|Non-SLR|%", -0.15, "Non-SLR"),
                ("Damage Cost|SLR|%", 0, "SLR"),
                ("Damage Cost|indirect|%", 0.3, "Indirect"),
            ],
            "MIMOSA_combined": [
                ("Damage Cost|%", [0.05, -0.15, "/"], "SLR + Non-SLR"),
                ("Damage Cost|indirect|%", 0.4, "Indirect"),
            ],
        }
        variables_lights_map["WITCH"] = variables_lights_map["MIMOSA"]

    legend_shades_of_gray = variables_lights_map[list(variables_lights_map.keys())[0]]

    xticks = {}
    xgap = 0.85 * len(models) / 3
    for i, year in enumerate(years):

        xticks[year] = (i + 0.5) * (len(models) + xgap) - 0.5

        for j, model in enumerate(models):
            model_color = custom_model_to_color[model]
            sub_selection = selection[
                (selection["Year"] == year) & (selection["Model"] == model)
            ]

            xpos = i * (len(models) + xgap) + j + 0.5 * xgap

            if model not in variables_lights_map:
                raise NotImplementedError
            variables_lights = variables_lights_map[model]

            for variable, lighten, nicename in variables_lights:
                color, pattern = lighten_list_to_pattern_color(lighten, model_color)

                values = sub_selection[sub_selection["Variable"] == variable]
                if len(values) > 1:
                    raise Exception(
                        f"Too many ({len(values)}) values for {year}, {model}, {variable}"
                    )
                if len(values) == 0:
                    continue
                value = values["Value"].iloc[0] * 100
                fig.add_bar(
                    x=[xpos],
                    y=[value],
                    marker={"color": color, "pattern": pattern},
                    legendgroup=variable,
                    name=nicename,
                    showlegend=False,
                    row=row,
                    col=col,
                )

    if showlegend:
        fig.add_bar(
            x=[None], y=[None], name=f"<b>Model:</b>", opacity=0, row=row, col=col,
        )
        for model in models:
            color = custom_model_to_color[model]
            fig.add_bar(
                x=[None],
                y=[None],
                name=model,
                marker_color=color,
                legendgroup="Models",
                row=row,
                col=col,
            )
        fig.add_bar(
            x=[None],
            y=[None],
            name=f"<br>{var_legend_title}",
            opacity=0,
            row=row,
            col=col,
        )
        for variable, lighten, nicename in legend_shades_of_gray[::-1]:
            legend_color = "#7F7F7F"
            color, pattern = lighten_list_to_pattern_color(lighten, legend_color)
            if pattern is not None:
                color = "#BBB"
            fig.add_bar(
                x=[None],
                y=[None],
                name=nicename,
                marker={"color": color, "pattern": pattern},
                legendgroup=variable,
                row=row,
                col=col,
            )

    fig.update_xaxes(
        tickvals=list(xticks.values()), ticktext=list(xticks.keys()), row=row, col=col
    )
    fig.update_layout(legend={"traceorder": "normal", "font_size": 13})


###############
#
# Utils
#
###############


def first_letter_upper(string):
    if len(string) <= 1:
        return string.upper()
    return string[0].upper() + string[1:]
