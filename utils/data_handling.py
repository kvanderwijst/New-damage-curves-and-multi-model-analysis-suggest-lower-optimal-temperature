"""
Data handling functions:
 - load data
 - transform data to common format
"""

import numpy as np
import pandas as pd


def load_climrisk(filename):
    data: pd.DataFrame = pd.read_csv(filename)
    data["Discounting"] = "medium"
    return _postprocess(data)


def load_mimosa(filename):
    data: pd.DataFrame = pd.read_csv(filename)
    data = data.drop(columns=["Param hash"]).replace("nodamage", "nodamages")
    if "combined" in filename:
        data["Damage quantile"] = data["Damage quantile"].astype(str) + "_combined"
    if "nodamages" in list(data["Damage quantile"].unique()):
        data.loc[data["Damage quantile"] == "nodamages", "SLR adaptation"] = "nodamages"
    return _postprocess(data)


def load_remind(filename):
    data: pd.DataFrame = pd.read_csv(filename, encoding="unicode_escape", sep=";")
    data.columns = data.columns.str.lstrip("X").str.replace(".", " ", regex=False)
    data["Damage quantile"] = (
        data["Damage quantile"].fillna("nodamages").astype(str).str.lstrip("0p")
    )
    data["SLR quantile"] = (
        data["SLR quantile"].fillna("nodamages").astype(str).str.lstrip("0p")
    )
    data["SLR adaptation"] = data["SLR adaptation"].fillna("nodamages")
    data = data.drop(columns=["2005", "2010", "2015"])
    data["Region"] = data["Region"].replace(
        {
            "ASIA": "R5.2ASIA",
            "LAM": "R5.2LAM",
            "MAF": "R5.2MAF",
            "OECD": "R5.2OECD",
            "REF": "R5.2REF",
        }
    )
    data.loc[
        data["Variable"].str.endswith("Percentage of GDP")
        | data["Variable"].str.endswith("Percentage of baseline GDP"),
        "Unit",
    ] = "Relative (between 0 and 1)"
    data["Variable"] = (
        data["Variable"]
        .replace({"Damage Cost|direct+indirect": "Damage Cost|direct+indirect|%"})
        .str.replace("Percentage of baseline GDP", "Percentage of GDP", regex=False)
    )
    data["Scenario"] = data["Scenario"].replace(
        {
            "experiment-1-1": "experiment_1.1",
            "experiment-2-1": "experiment_2.1",
            "experiment-2-2": "experiment_2.2",
        }
    )

    return _postprocess(data)


def load_witch(
    filename,
):  # COACCH_SLRAd_p05_RCP26, COACCH_SLRAd_p05_opt_dr01, COACCH_bau_dr01
    data: pd.DataFrame = pd.read_excel(filename)
    data["Model"] = "WITCH"
    data.columns = list(data.columns[:5]) + list(data.columns[5:].sort_values())
    data = data.drop(columns=["2005", "2010", "2015"])
    data["Region"] = data["Region"].replace(
        {
            "R5ASIA": "R5.2ASIA",
            "R5LAM": "R5.2LAM",
            "R5MAF": "R5.2MAF",
            "R5OECD": "R5.2OECD",
            "R5REF": "R5.2REF",
        }
    )

    scenario_str = (
        data["Scenario"]
        .str.replace("NODAM", "NODAM_p0", regex=False)
        .str.replace("_bau_", "_NODAM_p0_baseline_", regex=False)
        .str.split("_")
    )

    quant = scenario_str.str[2].str[1:].astype(int)

    data.insert(3, "Damage quantile", quant)
    data.insert(4, "SLR quantile", quant)

    data.insert(5, "SLR adaptation", "with")
    data.loc[scenario_str.str[1] == "SLRNoAd", "SLR adaptation"] = "without"
    data.loc[
        scenario_str.str[1] == "NODAM",
        ["Damage quantile", "SLR quantile", "SLR adaptation"],
    ] = "nodamages"

    data.insert(6, "Target", scenario_str.str[3].str.lower())

    discounting_map = {"dr01": "low", "dr15": "medium", "dr30": "high"}
    discounting = [
        "medium" if len(scen_str) < 5 else discounting_map[scen_str[4]]
        for scen_str in scenario_str
    ]
    data.insert(7, "Discounting", discounting)

    data["Target"] = data["Target"].replace({"opt": "cba"})

    return _postprocess(data)


def _postprocess(data):
    data["Variable"] = data["Variable"].str.replace(
        "Percentage of GDP", "%", regex=False
    )
    data["Damage quantile"] = data["Damage quantile"].replace(
        {5.0: "5", 50.0: "50", 95.0: "95"}
    )
    data["SLR quantile"] = data["SLR quantile"].replace(
        {5.0: "5", 50.0: "50", 95.0: "95"}
    )
    data["Region"] = data["Region"].replace({"R5.2REF": "R5.2EENA"})
    return _sort(_to_long(data))


def _sort(data):
    return data.sort_values(
        [
            "Model",
            "Target",
            "Damage quantile",
            "SLR quantile",
            "SLR adaptation",
            "Discounting",
            "Scenario",
            "Variable",
            "Region",
            "Year",
        ]
    )


def _to_long(data):
    return (
        data.set_index(
            [
                "Model",
                "Scenario",
                "Region",
                "Damage quantile",
                "SLR quantile",
                "SLR adaptation",
                "Target",
                "Discounting",
                "Variable",
                "Unit",
            ]
        )
        .rename_axis("Year", axis=1)
        .stack()
        .to_frame("Value")
        .reset_index()
    )


################################
##
## Indirect cost calculation
##
################################


def indirect_costs_mimosa_witch(data, model="MIMOSA"):

    calc_policy_indirect_costs = (
        model == "MIMOSA"
    )  # WITCH cannot provide indirect policy costs

    selection = data[data["Model"] == model]

    # 1. Net GDP for each scenario
    gdp = selection[selection["Variable"] == "GDP|PPP"]

    basic_columns = {"Model", "Region", "Target", "Year"}
    if model == "MIMOSA":
        basic_columns = basic_columns.union({"Scenario"})
    extended_columns = basic_columns.union(
        {"Damage quantile", "SLR quantile", "SLR adaptation", "Discounting",}
    )

    baseline_columns = basic_columns - {"Scenario", "Target"}
    if model == "WITCH":
        basic_columns = basic_columns.union({"Discounting"})
        baseline_columns = baseline_columns.union({"Discounting"})

    # 2. Extra variables
    merge_columns = {
        "gdp_nodamages": (
            gdp[
                (gdp["Target"] != "baseline") & (gdp["Damage quantile"] == "nodamages")
            ],
            basic_columns,
        ),
        "gdp_baseline": (
            gdp[
                (gdp["Target"] == "baseline") & (gdp["Damage quantile"] == "nodamages")
            ],
            baseline_columns,
        ),
        "direct_policy_costs": (
            selection[(selection["Variable"] == "Policy Cost|%")],
            extended_columns,
        ),
        "direct_damage_costs": (
            selection[(selection["Variable"] == "Damage Cost|%")],
            extended_columns,
        ),
    }

    for column_name, (merge_values, merge_on) in merge_columns.items():
        gdp = gdp.merge(
            merge_values[list(merge_on.union({"Value"}))],
            on=list(merge_on),
            how="left",
            suffixes=("", f"_{column_name}"),
        )

    gdp["Damage Cost|indirect|%"] = (gdp["Value_gdp_nodamages"] - gdp["Value"]) / gdp[
        "Value_gdp_baseline"
    ] - gdp["Value_direct_damage_costs"]
    gdp["Indirect Cost|%"] = (
        (gdp["Value_gdp_baseline"] - gdp["Value"]) / gdp["Value_gdp_baseline"]
        - gdp["Value_direct_policy_costs"]
        - gdp["Value_direct_damage_costs"]
    )
    gdp["Damage Cost|direct+indirect|%"] = (
        gdp["Value_direct_damage_costs"] + gdp["Damage Cost|indirect|%"]
    )

    if calc_policy_indirect_costs:
        gdp["Policy Cost|indirect|%"] = (
            gdp["Value_gdp_baseline"] - gdp["Value_gdp_nodamages"]
        ) / gdp["Value_gdp_baseline"] - gdp["Value_direct_policy_costs"]
        gdp["Policy Cost|direct+indirect|%"] = (
            gdp["Value_direct_policy_costs"] + gdp["Policy Cost|indirect|%"]
        )

    combined = pd.DataFrame()
    for column_name in [
        "Damage Cost|indirect|%",
        "Indirect Cost|%",
        "Damage Cost|direct+indirect|%",
    ] + (
        ["Policy Cost|indirect|%", "Policy Cost|direct+indirect|%"]
        if calc_policy_indirect_costs
        else []
    ):
        temp = (
            gdp[list(extended_columns.union({"Variable", "Unit", column_name}))]
            .copy()
            .rename(columns={column_name: "Value"})
        )
        temp["Variable"] = column_name
        temp["Unit"] = "Relative (between 0 and 1)"
        combined = pd.concat([combined, temp], sort=False)

    # Remove NaN-rows
    combined = combined[~combined["Value"].isna()]

    if model == "WITCH":
        combined["Scenario"] = ""

    return pd.concat([data, combined], sort=False)


def indirect_costs_remind(data):
    selection = data[
        (data["Model"] == "REMIND")
        & data["Variable"].isin(["Damage Cost|%", "Damage Cost|direct+indirect|%"])
    ]

    selection = selection.set_index(list(selection.columns[:-1]))

    selection_unstacked = selection["Value"].unstack("Variable")

    indirect_costs = (
        selection_unstacked["Damage Cost|direct+indirect|%"]
        - selection_unstacked["Damage Cost|%"]
    )
    indirect_costs = indirect_costs.to_frame("Value").reset_index()
    indirect_costs.insert(8, "Variable", "Indirect Cost|%")

    # Indirect costs are the same as indirect damage costs for REMIND
    indirect_damage_costs = indirect_costs.copy()
    indirect_damage_costs["Variable"] = "Damage Cost|indirect|%"

    return pd.concat([data, indirect_costs, indirect_damage_costs])


# def indirect_costs_witch(data):
#     selection = data[data["Model"] == "WITCH"]

#     # 1. Net GDP for each scenario
#     gdp = selection[selection["Variable"] == "GDP|PPP"]

#     basic_columns = {"Model", "Region", "Target", "Year"}
#     extended_columns = basic_columns.union(
#         {"Damage quantile", "SLR quantile", "SLR adaptation", "Discounting",}
#     )

#     # 2. Extra variables
#     merge_columns = {
#         "gdp_nodamages": (gdp[gdp["Damage quantile"] == "nodamages"], basic_columns),
#         "direct_policy_costs": (
#             selection[(selection["Variable"] == "Policy Cost|%")],
#             extended_columns,
#         ),
#         "direct_damage_costs": (
#             selection[(selection["Variable"] == "Damage Cost|%")],
#             extended_columns,
#         ),
#     }

#     for column_name, (merge_values, merge_on) in merge_columns.items():
#         gdp = gdp.merge(
#             merge_values[merge_on.union({"Value"})],
#             on=list(merge_on),
#             how="left",
#             suffixes=("", f"_{column_name}"),
#         )

#     gdp["Damage Cost|indirect|%"] = (gdp["Value_gdp_nodamages"] - gdp["Value"]) / gdp[
#         "Value_gdp_nodamages"
#     ] - gdp["Value_direct_damage_costs"]
#     # gdp["Indirect Cost|%"] = (
#     #     (gdp["Value_gdp_baseline"] - gdp["Value"]) / gdp["Value_gdp_baseline"]
#     #     - gdp["Value_direct_policy_costs"]
#     #     - gdp["Value_direct_damage_costs"]
#     # )
#     gdp["Indirect Cost|%"] = gdp["Damage Cost|indirect|%"]
#     gdp["Damage Cost|direct+indirect|%"] = (
#         gdp["Value_direct_damage_costs"] + gdp["Damage Cost|indirect|%"]
#     )

#     combined = pd.DataFrame()
#     for column_name in [
#         "Damage Cost|indirect|%",
#         "Indirect Cost|%",
#         "Damage Cost|direct+indirect|%",
#     ]:
#         temp = (
#             gdp[extended_columns.union({"Variable", "Unit", column_name})]
#             .copy()
#             .rename(columns={column_name: "Value"})
#         )
#         temp["Variable"] = column_name
#         temp["Unit"] = "Relative (between 0 and 1)"
#         combined = pd.concat([combined, temp], sort=False)

#     # Remove NaN-rows
#     combined = combined[~combined["Value"].isna()]

#     # Add scenario column back
#     combined["Scenario"] = "experiment_1"  # TODO

#     return pd.concat([data, combined], sort=False)


def mimosa_combined_to_separate_model(data):
    mask = data["Damage quantile"].astype(str).str.contains("_combined") & (
        data["Model"] == "MIMOSA"
    )
    data.loc[mask, "Model"] = data.loc[mask, "Model"] + "_combined"
    data.loc[mask, "Damage quantile"] = (
        data.loc[mask, "Damage quantile"].astype(str).str.rstrip("_combined")
    )
    return data


################################
##
## Global carbon price
##
################################


def remind_global_carbon_price(data):
    selection = data[
        (data["Model"] == "REMIND") & (data["Variable"] == "Price|Carbon")
    ].astype({"Value": float})

    # First check if World region is not available
    if len(selection[selection["Region"] == "World"]) > 0:
        print(
            "Warning: global carbon prices are already (partly) provided. Stopping calculation of global carbon prices."
        )
        return data

    index_cols = ["Target", "Damage quantile", "Discounting", "SLR adaptation", "Year"]
    grouped = selection.groupby(index_cols)

    # Then check if carbon prices are indeed roughly similar between each region
    std = grouped["Value"].std().max()
    if std > 1:
        print("Careful, there are significant regional differences in carbon prices.")

    # Finally calculate average world carbon price
    mean_cprices = grouped.agg(
        dict(
            {
                col: "first"
                for col in selection.columns
                if col not in index_cols + ["Value"]
            },
            Value="mean",
        )
    ).reset_index()
    mean_cprices["Region"] = "World"

    return pd.concat([data, mean_cprices], sort=False)
