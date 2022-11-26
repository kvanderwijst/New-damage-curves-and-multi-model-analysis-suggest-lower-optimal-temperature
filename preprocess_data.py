########################################################################
##
## Preprocess all raw data
##
## This produces the CSV file "preprocessed_scenario_data.csv"
## Running this script is not required if this file already exists
##
########################################################################


import pandas as pd

from utils.data_handling import (
    load_mimosa,
    load_remind,
    load_witch,
    indirect_costs_remind,
    indirect_costs_mimosa_witch,
    mimosa_combined_to_separate_model,
    remind_global_carbon_price,
)

# MIMOSA
data_mimosa_baseline = load_mimosa("Data/rawdata/MIMOSA/MIMOSA_baseline.csv")
data_mimosa_exp1 = load_mimosa("Data/rawdata/MIMOSA/MIMOSA_exp1.csv")
data_mimosa_exp1 = data_mimosa_exp1[
    data_mimosa_exp1["Scenario"] != "experiment_1.1_without_mitig"
]
data_mimosa_exp1_combined = load_mimosa("Data/rawdata/MIMOSA/MIMOSA_exp1_combined.csv")
data_mimosa_exp1_combined = data_mimosa_exp1_combined[
    data_mimosa_exp1_combined["Scenario"] != "experiment_1.1_without_mitig"
]
data_mimosa_exp2 = load_mimosa(f"Data/rawdata/MIMOSA/MIMOSA_exp2_2150.csv")

# REMIND
data_remind_exp1_rcp26 = load_remind("Data/rawdata/REMIND/REMIND_rcp26_08252022.csv")
data_remind_exp1_rcp60 = load_remind("Data/rawdata/REMIND/REMIND_rcp60_08252022.csv")
data_remind_exp1_rcp60_highdr = load_remind(
    "Data/rawdata/REMIND/REMIND_rcp60_highdr_09062022.csv"
)
data_remind_exp2 = load_remind("Data/rawdata/REMIND/REMIND_cba_08262022.csv")

# WITCH
data_witch_exp1 = pd.concat(
    [
        load_witch("Data/rawdata/WITCH/template_COACCH_part1_21-07-16_22-18-22.xlsx"),
        load_witch("Data/rawdata/WITCH/missing_run_rcp26_p95_slrnoad.xlsx"),
    ]
)
data_witch_exp2 = pd.concat(
    [
        load_witch("Data/rawdata/WITCH/template_COACCH_dr0p1.xlsx").replace(
            {"medium": "low"}
        ),
        load_witch("Data/rawdata/WITCH/template_COACCH_dr1p5.xlsx"),
        load_witch("Data/rawdata/WITCH/template_COACCH_dr3p0.xlsx").replace(
            {"medium": "high"}
        ),
    ]
)
data_witch_exp2 = pd.concat(
    [
        data_witch_exp2,  # For medium discounting, CBA p5 is equal to tax0 run p5 dmg
        data_witch_exp2[
            (data_witch_exp2["Discounting"] == "medium")
            & (data_witch_exp2["Damage quantile"] == "5")
        ].replace({"tax0": "cba"}),
    ]
)
data_witch_exp2 = data_witch_exp2[~data_witch_exp2["Target"].isin(["rcp60", "rcp26"])]
data_witch_exp2 = data_witch_exp2[
    ~data_witch_exp2["Scenario"].str.contains("_emission_pulse|_bau_")
]
data_witch_bau = load_witch(
    "Data/rawdata/WITCH/template_COACCH_part1_21-11-16_15-46-00.xlsx"
)
data_witch_bau = data_witch_bau[
    data_witch_bau["Scenario"].str.contains("_bau_|_baudam_")
]


data_all = pd.concat(
    [
        data_mimosa_baseline,
        data_mimosa_exp1,
        data_mimosa_exp1_combined,
        data_mimosa_exp2,
        data_remind_exp1_rcp26,
        data_remind_exp1_rcp60,
        data_remind_exp1_rcp60_highdr,
        data_remind_exp2,
        data_witch_exp1,
        data_witch_exp2,
        data_witch_bau,
    ]
)

data_all = mimosa_combined_to_separate_model(
    indirect_costs_mimosa_witch(data_all, "MIMOSA")
)
data_all = indirect_costs_remind(data_all)
data_all = indirect_costs_mimosa_witch(data_all, "WITCH")
data_all = remind_global_carbon_price(data_all)

data_all["Discounting"] = pd.Categorical(
    data_all["Discounting"], ["low", "medium", "high"], ordered=True
)

for column in ["Damage quantile", "SLR quantile"]:
    data_all[column] = data_all[column].replace(
        {"5.0": "5", "50.0": "50", "95.0": "95",}
    )


data_wide = data_all.set_index([c for c in data_all.columns if c != "Value"])[
    "Value"
].unstack("Year")
data_wide = data_wide[~data_wide.isna().all(axis=1)].reset_index()

data_wide.to_csv("Data/preprocessed_scenario_data.csv", index=False)
