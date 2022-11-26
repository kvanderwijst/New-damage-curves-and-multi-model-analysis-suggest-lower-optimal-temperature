"""
SI plot: Regional damages in bar plot: 
bar figure with regions as facet_col, RCP as facet_row.
For either RCP 2.6 or RCP 6.0, and with or without SLR adaptation
"""

from plotly.subplots import make_subplots

from ..plot import subplot_damages


def fig_SI_regional_damages(
    data,
    rcp="RCP 6.0",
    slr_adapt="without",
    models=["WITCH", "MIMOSA", "REMIND"],
    years=["2030", "2050", "2100"],
    damage_quantiles=["5", "50", "95"],
    title_suffix="",
):
    regions = ["R5.2ASIA", "R5.2EENA", "R5.2LAM", "R5.2MAF", "R5.2OECD"]
    rcp_target = rcp.replace(" ", "").lower().replace(".", "")
    fig = make_subplots(
        len(damage_quantiles),
        len(regions),
        column_titles=[
            "<b>R5-{}</b>".format(region[len("R5.2") :]) for region in regions
        ],
        row_titles=[f"<b>Damage quantile: {q}</b><br> " for q in damage_quantiles],
        vertical_spacing=0.07,
    )
    kwargs = {
        "slr_adapt": slr_adapt,
        "years": years,
        "models": models,
        "target": rcp_target,
    }
    for i, q in enumerate(damage_quantiles):
        for j, region in enumerate(regions):
            subplot_damages(
                data,
                fig,
                i + 1,
                j + 1,
                damage_quantile=q,
                region=region,
                **kwargs,
                showlegend=i + j == 0,
            )
    (
        fig.update_layout(
            barmode="relative",
            legend={"traceorder": "normal", "y": 0.5},
            template="plotly_white",
            width=1180,
            height=100 + 250 * len(damage_quantiles),
            margin_t=80,
            title=f"<b>{title_suffix}Damage cost decomposition: {rcp}</b> ({slr_adapt} SLR adaptation)",
        )
        .update_yaxes(ticksuffix="%")  # , nticks=15)
        .update_yaxes(col=1, title="GDP loss", title_standoff=0)
        .update_xaxes(matches="x1")
    )
    for i in range(len(damage_quantiles)):
        fig.update_yaxes(row=i + 1, matches=f"y{i*len(regions)+1}")

    return fig
