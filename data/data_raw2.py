from pathlib import Path
import pandas as pd
import json
from typing import NamedTuple, Any

def get_technology_sector() -> dict[str, list[str]]:

    df_input = pd.read_csv(
                    "config/Tag_Technology_to_Sector.csv",
                    delimiter=";")
    
    # For each sector create a list of technologies
    technology_sector = {}
    for sector in df_input["Sector"].unique():
        technology_sector[sector] = df_input[df_input["Sector"] == sector]["Technology"].to_list()

    return technology_sector

class GeoLocation(NamedTuple):
    latitude: str
    longitude: str
    name: str

def get_region_location() -> dict[str, GeoLocation]:

    with open(Path(__file__).parent.parent / "config" / "geolocation.json", 'r') as fp:
        geo_location_raw = dict(json.load(fp))

    return {region: GeoLocation(latitude=data['latitude'], longitude=data['longitude'], name=data['name']) for region, data in geo_location_raw.items()}

class DataProcessor:

    def __init__(self, sol_path: Path, type_of_data_to_read: str, columns: list[str]):
        self._sol_path = sol_path
        self._type_of_data_to_read = type_of_data_to_read
        self._columns = columns
        
        
        # Read data
        with open(self._sol_path, "r") as f:
            lines = f.read().splitlines()
            data_list = []
            for i, l in enumerate(lines, start=-1):
                if l.startswith(f"{self._type_of_data_to_read}["):
                    m = l.split('[', 1)[1].split(']')[0].split(",")
                    m.append(l.split(" ")[-1])
                    data_list.append(m)
                    if not lines[i + 1].startswith(self._type_of_data_to_read):
                        break

        self.df = pd.DataFrame(data_list, columns=self._columns)

        if "Value" in self.df.columns:
            self.df['Value'] = pd.to_numeric(self.df['Value'], errors='coerce')
        
        if "Year" in self.df.columns:
            self.df['Year'] = pd.to_numeric(self.df['Year'], errors='raise')

        # Convert from PetaJoules to TerraWhatHours
        if type_of_data_to_read in ["ProductionByTechnologyAnnual", "Export", "UseAnnual", "RateOfActivity", "ProductionByTechnology"]:
            self.df['Value'] = pd.to_numeric(self.df['Value']) / 3.6
        else:
            print("No unit conversion applied!")

    def filter_by_list(self, column: str, by_filter: list[str]):
        self.df = self.df[self.df[column].isin(by_filter)]

    def aggregate_by_sum(self, column_to_sum: str, groups_memberships: dict[str, str]):
        self.df.replace(groups_memberships, inplace=True)
        self.df = self.df.groupby([col for col in self.df.columns if col != column_to_sum], as_index=False).sum(numeric_only=True)

    def sum_identical_entries(self, column_to_sum: str):
        self.df = self.df.groupby([col for col in self.df.columns if col != column_to_sum], as_index=False).sum(numeric_only=True)

    def aggreagate_all_by_sum(self, column_to_aggregate: str, aggregated_entry_name: str, column_to_sum: str):
        self.df[column_to_aggregate] = aggregated_entry_name
        self.df = self.df.groupby([col for col in self.df.columns if col != column_to_sum], as_index=False).sum(numeric_only=True)

    def show_example_rows(self, n: int = 10):
        print(self.df.head(n))

    def force_numeric(self, column: str):
        self.df[column] = pd.to_numeric(self.df[column], errors='raise')

    def filter_by_identifier(self, column: str, identifier: str | int | Any):
        self.df = self.df[self.df[column] == identifier]

    def filter_by_containing_string(self, column: str, identifier: str):
        self.df = self.df[self.df[column].str.contains(identifier)]