"""
Creates a map with bar charts on top
"""

import os
import subprocess
import json
import numpy as np
import pandas as pd

idx = pd.IndexSlice
import plotly.express as px
from xml.etree import ElementTree
from IPython.display import SVG, display
import cairosvg

# Bugfix for Plotly default export size
import plotly.io as pio

pio.kaleido.scope.default_width = None
pio.kaleido.scope.default_height = None

from .plot import first_letter_upper


# Import GeoJSON
with open("utils/macroregions.json") as fh:
    macroregions = json.load(fh)

colors = {
    # "Violet": ["#B6026D", "#F6E3EB"],
    "Violet": ["#9d015d", "#FFF"],
    "Donkerblauw": ["#0070BA", "#E3EAF6"],
    "Mosgroen": ["#808E1E", "#ADB46E", "#E0E3C6"],
    "Hemelblauw": ["#00ADEE", "#41C8F4", "#C7EBFC"],
    "Hemelblauw2": ["#0087BB", "#00B9F1", "#AAE1FA"],
    "Rood": ["#EF2924", "#FDE9DD"],
    "Donkergeel": ["#C98918", "#FCAD1F", "#FEF5E5"],
}

# Create figure
def create_map(
    selection,
    outputfile="figure.svg",
    width=1180,
    height=520,
    title=None,
    coloraxis_tickformat="%",
    custom_ymax=None,
):
    margin_t = 35
    if title is not None:
        height += 50
        margin_t += 50

    fig = px.choropleth(
        selection[selection["Model"] == "Combined"],
        locations="Region",
        geojson=macroregions,
        color="Damage Cost|direct+indirect|%",
        color_continuous_scale=colors["Violet"][::-1],
    )

    fig.update_geos(
        projection_type="natural earth",
        visible=False,
        showframe=True,
        framecolor="#AAA",
        showland=True,
        landcolor="#F5F5F5",
    )
    # fig.update_geos(projection_type="orthographic")

    fig.add_scatter(x=[None], y=[None], showlegend=False)
    hide_kwargs = {"showgrid": False, "zeroline": False, "visible": False}
    fig.update_xaxes(**hide_kwargs).update_yaxes(**hide_kwargs)

    subplot_height = 0.3
    subplot_width = 0.1
    fromleft = 0.05
    for i, (xmin, ymin, region, region_coords) in enumerate(
        [
            (fromleft, 0, "LAM", [[0.37, 0.44]]),
            (0.5 - 0.5 * subplot_width, 0, "MAF", [[0.55, 0.48]]),
            (1 - subplot_width - fromleft, 0, "ASIA", [[0.7, 0.67]]),
            (
                fromleft,
                1 - subplot_height,
                "OECD",
                [[0.31, 0.75], [0.51, 0.81]],
            ),  # , [0.76, 0.37]
            (1 - subplot_width - fromleft, 1 - subplot_height, "EENA", [[0.7, 0.86]]),
        ]
    ):
        j = i + 2
        indexed_selection = selection[selection["Region"] == f"R5.2{region}"].set_index(
            "Model"
        )

        bar_kwargs = {"xaxis": f"x{j}", "yaxis": f"y{j}", "showlegend": i == 0}
        for name, values, color in zip(
            ("Non-SLR", "SLR", "indirect"),
            ([15.314, 12.69, 15.37], [1.405, 1.734, np.nan], [4.6347, 5.67, 2.711]),
            colors["Hemelblauw2"],
        ):
            models = ["MIMOSA", "WITCH", "REMIND"]
            values = indexed_selection.loc[models, f"Damage Cost|{name}|%"].values
            patterns = [
                "/" if combined else ""
                for combined in indexed_selection.loc[models, "Combined"]
            ]
            fig.add_bar(
                x=models,
                y=values,
                name=first_letter_upper(name),
                marker={
                    "color": color,
                    "pattern": {
                        "shape": patterns,
                        "fgcolor": colors["Hemelblauw2"][1],
                        "fgopacity": 1,
                        "solidity": 0.5,
                    },
                },
                **bar_kwargs,
            )

        # Combined color: #8C9D74
        fig.layout[f"xaxis{j}"] = {
            "domain": [xmin, xmin + subplot_width],
            "anchor": f"y{j}",
        }
        fig.layout[f"yaxis{j}"] = {
            "domain": [ymin, ymin + subplot_height],
            "anchor": f"x{j}",
        }

        # Add arrow to position on map
        arrow_color = "#AAA"
        for regionx, regiony in region_coords:
            fig.add_shape(
                type="line",
                xref="paper",
                yref="paper",
                x0=regionx,
                y0=regiony,
                line_color=arrow_color,
                x1=xmin + 0.5 * subplot_width,
                y1=ymin + 0.5 * subplot_height,
            )
            circle_dx = 0.002
            circle_dy = circle_dx * width / height
            fig.add_shape(
                type="circle",
                x0=regionx - circle_dx,
                x1=regionx + circle_dx,
                y0=regiony - circle_dy,
                y1=regiony + circle_dy,
                xref="paper",
                yref="paper",
                line_color=arrow_color,
                fillcolor=arrow_color,
            )

        dx = 0.027
        fig.add_shape(
            type="rect",
            xref="paper",
            yref="paper",
            x0=xmin - dx,
            x1=xmin + subplot_width + dx,
            y0=ymin - 0.1,
            y1=ymin + subplot_height + 0.05,
            fillcolor="white",
            line={"width": 1, "color": "#999"},
        )

        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=xmin + 0.5 * subplot_width,
            y=ymin + subplot_height,
            xanchor="center",
            yanchor="bottom",
            text=f"<b>R5-{region}</b>",
            font_size=13,
            showarrow=False,
        )

    fig.update_layout(
        width=width,
        height=height,
        margin={"b": 50, "t": margin_t, "r": 20, "l": 0},
        barmode="relative",
        legend={
            "y": 0.47,
            "x": 0.92,
            "title": {"text": "<b>Damage type:</b>", "font_size": 14},
            "traceorder": "reversed",
            "font_size": 14,
        },
        title=title,
        template="plotly_white",
    )
    fig.update_coloraxes(
        colorbar={
            "title": {"text": "Average<br>total<br>damages"},
            "tickformat": coloraxis_tickformat,
        },
        cmin=0,
        cmax=selection["Damage Cost|direct+indirect|%"].max()
        if custom_ymax is None
        else custom_ymax,
    )
    ymin = min(
        0,
        selection["Damage Cost|direct+indirect|%"].min(),
        selection.drop(columns=["Region", "Model", "Combined"]).min().min(),
    )
    ymax = (
        max(
            selection["Damage Cost|direct+indirect|%"].max(),
            selection.drop(columns=["Region", "Model", "Combined"]).max().max(),
        )
        if custom_ymax is None
        else custom_ymax
    )
    yrange = [ymin - 0.1 * (ymax - ymin), ymax + 0.1 * (ymax - ymin)]
    fig.update_yaxes(tickformat=coloraxis_tickformat, range=yrange)

    fig.write_image(outputfile)
    move_layers(outputfile)
    show_svg(outputfile)


#############
#
# Utils
#
#############

ElementTree.register_namespace("", "http://www.w3.org/2000/svg")


def move_layers(filename, output_filename=None):

    et = ElementTree.parse(filename)

    end_layers = []
    root = et.getroot()
    for element in et.getroot():
        if "class" in element.attrib:
            classname = element.attrib["class"]
            if classname in ["cartesianlayer", "bglayer"]:
                end_layers.append(element)
                root.remove(element)
    for layer in end_layers:
        root.append(layer)

    if output_filename is None:
        output_filename = filename
    et.write(output_filename)


def show_svg(filename):
    display(SVG(filename=filename))
    # display(SVG(filename=filename))


def inkscape_png(svg_filename, png_filename=None, dpi=200, print_output=False):
    if png_filename is None:
        png_filename = svg_filename.rstrip(".svg") + ".png"
    output = subprocess.check_output(
        'inkscape --export-filename="{}" -d {} "{}"'.format(
            os.path.join(os.getcwd(), png_filename),
            dpi,
            os.path.join(os.getcwd(), svg_filename),
        ),
        shell=True,
    )
    if print_output:
        print(output)


def cairo_png(svg_filename, png_filename=None, scale=3):
    if png_filename is None:
        png_filename = svg_filename.rstrip(".svg") + ".png"
    cairosvg.svg2png(url=svg_filename, write_to=png_filename, scale=scale)


def svg_to_png(svg_filename, png_filename=None, use_inkscape=True, **kwargs):
    if use_inkscape:
        inkscape_png(svg_filename, png_filename, **kwargs)
    else:
        cairo_png(svg_filename, **kwargs)
