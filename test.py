from pathlib import Path
import pandas as pd

from data import DataProcessor, header_mapping, PlotCreator, get_technology_sector
from data import aggregation as tech_aggregation

#d = DataProcessor(directory=Path(__file__).parent / "Solution_day40.sol", 
#                  type_of_data_to_read="ProductionByTechnologyAnnual", 
#                  columns=header_mapping["ProductionByTechnologyAnnual"]["columns"])

d = DataProcessor(directory=Path(__file__).parent / "Solution_day40.sol", 
                  type_of_data_to_read="TotalCapacityAnnual", 
                  columns=header_mapping["TotalCapacityAnnual"]["columns"])

#d.show_example_rows()

d.force_numeric(column="Value")
#d.filter_by_string(column="Fuel", identifier="Heat_Low_Industrial")
#d.filter_by_string(column="Region", identifier="DE")
#d.filter_by_string(column="Tec

d.filter_by_containing_string(column="Technology", identifier="D_")
#power_techs = get_technology_sector()["Power"]
#d.filter_by_list(column="Technology", by_filter=power_techs)
#d.aggregate_by_sum(column_to_sum="Value", groups_memberships=tech_aggregation)
#d.filter_by_string(column="Fuel", identifier="Power")


d.df = d.df[d.df["Value"] > 0]

d.show_example_rows()

"""data = {
    'Year': [2018, 2025, 2030, 2035, 2040, 2045, 2050, 2018, 2025, 2030, 2035, 2040, 2045, 2050],
    'Technology': ['RES_Grass'] * 7 + ['RES_Fast'] * 7,
    'Fuel': ['Biomass'] * 7 + ['Biomass'] * 7,
    'Region': ['AT'] * 14,
    'Value': [12.223781, 12.893669, 12.235504, 11.774789, 11.314073, 10.991573, 10.669072,
              13.223781, 13.893669, 11.235504, 10.774789, 10.314073, 9.991573, 9.669072]
}

df = pd.DataFrame(data)"""

#print(df)
fig = PlotCreator(d.df).plot_stacked_quantity_evolution(region="DE")

fig.update_layout(
    title="Storage Capacity",
)

fig.show()

#print(d.df.head(10))

