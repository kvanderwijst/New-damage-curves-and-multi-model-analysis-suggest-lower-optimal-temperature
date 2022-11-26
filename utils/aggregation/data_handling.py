"""
Aggregation: data handling
 - Import data
 - Transform to long form

"""

import pandas as pd


def import_data(filename, make_these_variables_absolute=None):

    data = pd.read_csv(filename).drop(columns="Unit")
    to_index = (
        lambda varname: data[data["Variable"] == varname]
        .set_index("Region")
        .drop(columns=["Variable"])
    )

    if make_these_variables_absolute is not None:
        for variable in make_these_variables_absolute:
            value_absolute = (to_index(variable) * to_index("GDP_gross")).reset_index()
            value_absolute.insert(0, "Variable", f"{variable}_absolute")
            data = pd.concat([data, value_absolute], ignore_index=True)

    return _to_long(data)


def _to_long(data):
    data_long = (
        data.set_index(["Variable", "Region"])
        .rename_axis("Year", axis=1)
        .stack()
        .to_frame("Value")
        .reset_index()
    )
    return data_long

