from pathlib import Path

from data import DataRaw, PlotObject
fuel = "Power"


data_rw = DataRaw(directory=Path(__file__).parent / "Solution_day40.sol", key="trade_map", sector="Power")
data_rw.filter_column(column="Fuel", by_filter=[fuel])
data_rw.replace_offshore()

df = DataRaw(directory=Path(__file__).parent / "Solution_day40.sol",
             key="capacities")
df.replace_offshore()
df.filter_sector()
df.aggregate_technologies()
#df.filter_by_column_string_contains(column="Technology", identifier="D_Heat_HLDH")

figure_dict = PlotObject(key="trade_map", year=[2018, 2030, 2040, 2050], sector="Power", df_list=[data_rw.df], scenarios=["Test"]).create_dict_tade_geo_fig(capacities=[df.df])


# Create a list of scenarios
scenarios = list(figure_dict.keys())

# Add each scenario's figures to the subplot
for name, figure in figure_dict.items():
    for f in figure:
        f.update_layout(height=1080, width=1520)
        f.show()