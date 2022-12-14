# New damage curves and multi-model analysis suggest lower optimal temperature

This repository contains the data required to reproduce all findings of the paper "New damage curves and multi-model analysis suggest lower optimal temperature" (van der Wijst et al.).

Specifically:
* The scenario data (in preprocessed format combining scenario data from the three models MIMOSA, REMIND and WITCH): `Data/preprocessed_scenario_data.csv`
  * (This file can be recreated by running `preprocess_data.py`. It combines data from the three scenarios and calculates indirect damage/mitigation costs, see Methods from paper.)
* Output data:
  * Calculated Benefit-Cost Ratios: `Data/output_benefit_cost_ratios.csv`
  * Calculated benefits and costs over time: `Data/output_costs_and_benefits_over_time`
  * (These files can be recreated using `Benefit Cost Ratios.ipynb`)
* All figures in the folder `Figures` (which can be recreated using `Paper figures.ipynb` and `Benefit Cost Ratios.ipynb`)

## Requirements
To run the scripts in this repository, the following packages are needed:
* `pandas`
* `plotly`
* Either `cairosvg` or Inkscape to convert the SVG maps (Figure 1) to PNG files. If Inkscape is used, the command `inkscape` should be available from the command prompt.
