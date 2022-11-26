"""
Code to transform MIMOSA output to COACCH task 4.3 template
"""

import pandas as pd


class SelectData:
    def __init__(self, template_name, variable, unit, factor=1):
        self.template_name = template_name
        self.variable = variable
        self.unit = unit
        self.factor = factor

    def to_template(self, data):
        selection = self._select(data).round(5).reset_index()
        selection.insert(1, "Variable", self.template_name)
        selection.insert(2, "Unit", self.unit)
        selection.insert(3, "2010", "")
        selection.insert(4, "2015", "")
        return selection

    def _select(self, data):
        selection = data[data["Variable"] == self.variable].drop(columns=["Variable"])
        selection["Value"] *= self.factor
        return self._to_wide(selection)

    @staticmethod
    def _to_wide(selection):
        return selection.set_index(["Region", "Year"])["Value"].unstack()


class DivideSelectData(SelectData):
    def __init__(
        self, template_name, variable, unit, factor=1, divide_by_variable="GDP_gross"
    ):
        super().__init__(template_name, variable, unit, factor)
        self.divide_by_variable = divide_by_variable

    def _select(self, data):
        selection_main = super()._select(data)
        selection_divide_by = data[data["Variable"] == self.divide_by_variable].drop(
            columns=["Variable"]
        )
        return selection_main / self._to_wide(selection_divide_by)


def to_template(data_aggregated):
    template_variables = [
        SelectData("Emissions|CO2", "regional_emissions", "Mt CO2/yr", 1000),
        DivideSelectData(
            "Damage Cost|Percentage of GDP",
            "damage_costs_absolute",
            "Relative (between 0 and 1)",
        ),
        DivideSelectData(
            "Damage Cost|SLR|Percentage of GDP",
            "SLR_damages_absolute",
            "Relative (between 0 and 1)",
        ),
        DivideSelectData(
            "Damage Cost|Non-SLR|Percentage of GDP",
            "resid_damages_absolute",
            "Relative (between 0 and 1)",
        ),
        DivideSelectData(
            "Policy Cost|Percentage of GDP",
            "abatement_costs",
            "Relative (between 0 and 1)",
        ),
        SelectData("GDP|PPP", "GDP_net", "billion US$2010/yr", 1000),
        SelectData("Price|Carbon", "carbonprice", "US$2010/t CO2", 1000),
        SelectData(
            "Temperature|Global Mean", "temperature", "°C (rel to pre-industrial)"
        ),
        SelectData("Utility", "utility", "No unit"),
    ]

    combined_data = pd.concat(
        [
            template_variable.to_template(data_aggregated)
            for template_variable in template_variables
        ],
        ignore_index=True,
    )

    combined_data["Region"] = combined_data["Region"].replace("Global", "World")
    return combined_data


def to_template_climrisk(data_aggregated):
    template_variables = [
        SelectData(
            "Damage Cost|Percentage of GDP",
            "damages_relative",
            "Relative (between 0 and 1)",
        ),
        SelectData(
            "Temperature|Global Mean", "temperature", "°C (rel to pre-industrial)"
        ),
    ]

    combined_data = pd.concat(
        [
            template_variable.to_template(data_aggregated)
            for template_variable in template_variables
        ],
        ignore_index=True,
    )

    combined_data["Region"] = combined_data["Region"].replace("Global", "World")
    return combined_data
