from pathlib import Path
import pandas as pd

from data import DataProcessor, header_mapping, PlotCreator, get_technology_sector
from data import aggregation as tech_aggregation

#d = DataProcessor(directory=Path(__file__).parent / "Solution_day40.sol", 
#                  type_of_data_to_read="ProductionByTechnologyAnnual", 
#                  columns=header_mapping["ProductionByTechnologyAnnual"]["columns"])

d = DataProcessor(sol_path=Path(__file__).parent / "Solution_day40.sol", 
                  type_of_data_to_read="TotalCapacityAnnual", 
                  columns=header_mapping["TotalCapacityAnnual"]["columns"])

#d.show_example_rows()

d.force_numeric(column="Value")
#d.filter_by_string(column="Fuel", identifier="Heat_Low_Industrial")
#d.filter_by_string(column="Region", identifier="DE")
#d.filter_by_string(column="Tec

d.filter_by_containing_string(column="Technology", identifier="D_")
#d.aggreagate_all_by_sum(column_to_aggregate="Region", aggregated_entry_name="All_Region", column_to_sum="Value")
#power_techs = get_technology_sector()["Power"]
#d.filter_by_list(column="Technology", by_filter=power_techs)
#d.aggregate_by_sum(column_to_sum="Value", groups_memberships=tech_aggregation)
#d.filter_by_string(column="Fuel", identifier="Power")


#d.df = d.df[d.df["Value"] > 0]



"""data = {
    'Year': [2018, 2025, 2030, 2035, 2040, 2045, 2050, 2018, 2025, 2030, 2035, 2040, 2045, 2050],
    'Technology': ['RES_Grass'] * 7 + ['RES_Fast'] * 7,
    'Fuel': ['Biomass'] * 7 + ['Biomass'] * 7,
    'Region': ['AT'] * 14,
    'Value': [12.223781, 12.893669, 12.235504, 11.774789, 11.314073, 10.991573, 10.669072,
              13.223781, 13.893669, 11.235504, 10.774789, 10.314073, 9.991573, 9.669072]
}

df = pd.DataFrame(data)"""

d.show_example_rows()

#print(df)
fig = PlotCreator(d.df).plot_stacked_quantity_evolution(region="DE")

fig.update_layout(
    width=1400,
    height=800,
    title="Storage Capacity All Contries",
    yaxis_title="Capacity [GW]",
    xaxis_title="Year",
)
fig.write_image("storage_capacity_germany.pdf")

fig.show()

#print(d.df.head(10))

