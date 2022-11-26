"""
Functions to transform between RGB, HEX and HLS and to lighten/darken a color
"""
import colorsys
import numpy as np

# Bugfix for Plotly default export size
import plotly.io as pio

pio.kaleido.scope.default_width = None
pio.kaleido.scope.default_height = None

colors_PBL = [
    "#00AEEF",
    "#808D1D",
    "#B6036C",
    "#FAAD1E",
    "#3F1464",
    "#7CCFF2",
    "#F198C1",
    "#42B649",
    "#EE2A23",
    "#004019",
    "#F47321",
    "#511607",
    "#BA8912",
    "#78CBBF",
    "#FFF229",
    "#0071BB",
]

model_to_color = {
    "MIMOSA": colors_PBL[0],
    "WITCH": colors_PBL[1],
    "REMIND": colors_PBL[3],
}
model_to_color["MIMOSA_combined"] = colors_PBL[2]

explanation_annotation_style = dict(
    arrowhead=6,
    arrowcolor="#CCC",
    bgcolor="#FFF",
    arrowwidth=2,
    bordercolor="#CCC",
    font={"size": 12, "color": "#444"},
)


def hex_to_rgb(hex_str, normalise=False):
    hex_str = hex_str.lstrip("#")
    rgb = [int(hex_str[i : i + 2], 16) for i in (0, 2, 4)]
    if normalise:
        return [x / 255.0 for x in rgb]
    else:
        return rgb


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(rgb)


def hex_to_hls(hex_str):
    return colorsys.rgb_to_hls(*hex_to_rgb(hex_str, True))


def hls_to_hex(hls):
    return rgb_to_hex([int(np.round(x * 255)) for x in colorsys.hls_to_rgb(*hls)])


def lighten_hex(hex_str, extra_lightness=0.1, extra_saturation=0.0):
    hls = list(hex_to_hls(hex_str))
    hls[1] += extra_lightness
    hls[2] += extra_saturation
    return hls_to_hex(hls)
