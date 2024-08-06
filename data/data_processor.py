from __future__ import annotations

from pathlib import Path
import pandas as pd
import json
from typing import NamedTuple, Any

from .config import HEADER_MAPPING

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

def read_sol_keys(sol_path: Path) -> set[str]:

    with open(sol_path, "r") as f:
        lines = f.read().splitlines()
        keys = set()
        for l in lines[1:]:
            keys.add(l.split("[", 1)[0])

    return keys


def find_keys_containing_string(sol_path: Path, string: str) -> set[str]:

    with open(sol_path, "r") as f:
        lines = f.read().splitlines()
        keys = set()
        for l in lines[1:]:
            if string in l:
                keys.add(l.split("[", 1)[0])

    return keys

class DataProcessor:

    def __init__(self, sol_path: Path, type_of_data_to_read: str, columns: list[str], read_year_split: bool = False):

        self.df = self._read_file(sol_path, type_of_data_to_read, columns)

        if "Value" in self.df.columns:
            self.df['Value'] = pd.to_numeric(self.df['Value'], errors='coerce')

        for col in ["Year", "Mode"]:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='raise')


        # Get year_split, 1 / number of timesteps per year, Just use RateofActivity for this
        self._year_split = None
        if read_year_split:
            df_with_timestamp = self.df if "TS" in self.df.columns else self._read_file(sol_path, "RateOfActivity", HEADER_MAPPING["RateOfActivity"]["columns"])
            self._year_split = 1 / len(df_with_timestamp["TS"].unique())

        # Convert from PetaJoules to TerraWhatHours
        if type_of_data_to_read in ["ProductionByTechnologyAnnual", "Export", "UseAnnual", "RateOfActivity", "ProductionByTechnology"]:
            print("Converting from PetaJoules to TerraWattHours")
            self.df['Value'] = pd.to_numeric(self.df['Value']) / 3.6
        else:
            print("No unit conversion applied!")

    def _read_file(self, sol_path: Path, type_of_data_to_read: str, columns: list[str]) -> pd.DataFrame:

        # Read data
        with open(sol_path, "r") as f:
            lines = f.read().splitlines()
            data_list = []
            for i, l in enumerate(lines, start=-1):
                if l.startswith(f"{type_of_data_to_read}["):
                    m = l.split('[', 1)[1].split(']')[0].split(",")
                    m.append(l.split(" ")[-1])

                    data_list.append(m)
                    if not lines[i + 1].startswith(type_of_data_to_read):
                        break

        self.df = pd.DataFrame(data_list, columns=columns)

        return self.df

    def concat(self, this_identifier: str, others: dict[str, DataProcessor]) -> DataProcessor:
        self.df["Source"] = this_identifier
        for identifier, other in others.items():
            other.df["Source"] = identifier
            self.df = pd.concat([self.df, other.df], ignore_index=True)

        return self
    
    @property
    def year_split(self):
        if self._year_split is None:
            raise ValueError("year_split has not been calculated, set read_year_split=True in the constructor")
        return self._year_split

    def filter_by_list(self, column: str, by_filter: list[Any]):
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

    def filter_by_containing_string_in_list(self, column: str, identifier_list: list[str]):
        self.df = self.df[self.df[column].str.contains("|".join(identifier_list))]

def concat(data_processors: dict[str, DataProcessor]) -> DataProcessor:
    # Concat and add source
    source, data_processor = data_processors.popitem()
    data_processor.concat(source, data_processors)

    return data_processor