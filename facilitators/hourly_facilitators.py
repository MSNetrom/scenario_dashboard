import plotly.graph_objects as go
from pathlib import Path

import data.data_processor as dp
from data import HEADER_MAPPING

from .base_faciliator import FacilitatorBase
from .colors import consistent_pastel_color_generator

class HourlyFacilitatorBase(FacilitatorBase):

    def __init__(self, sol_path: Path = None, type_of_data_to_read: str = None, year: int = None, region: str = None, extra_identifying_columns: list[str] = []):
        self._sol_path = sol_path
        self._type_of_data_to_read = type_of_data_to_read
        self._year = year
        self._region = region
        self._extra_identifying_columns = extra_identifying_columns

    @staticmethod
    def _get_relevant_data(sol_path: Path, type_of_data_to_read: str) -> dp.DataProcessor:

        d = dp.DataProcessor(sol_path=sol_path, 
                  type_of_data_to_read=type_of_data_to_read, 
                  columns=HEADER_MAPPING[type_of_data_to_read]["columns"], 
                  read_year_split=True)
        
        d.force_numeric(column="TS")
        d.force_numeric(column="Value")

        return d

    def get_relevant_data(self) -> dp.DataProcessor:
        return HourlyFacilitatorBase._get_relevant_data(self._sol_path, self._type_of_data_to_read, self._year, self._region)
    
    def generate_traces(self, relevant_data: dp.DataProcessor) -> list[go.Bar]:

        traces = []

        relevant_data.filter_by_identifier(column="Region", identifier=self._region)
        relevant_data.filter_by_identifier(column="Year", identifier=self._year)

        # Data of same year and same region, and same identifying columns should be one group plotted with same colors in the bars
        grouped_df = relevant_data.df.groupby(self._extra_identifying_columns + ["Year", "Region"])

        # Create a bar for each group
        for group, data in grouped_df:

            data = data.sort_values(by="TS")
            data["TS"] = data["TS"].astype(str)

            name = " ".join(group[i] for i in range(len(self._extra_identifying_columns)))

            traces.append(go.Bar(x=[data["TS"], *[data[column] for column in self._extra_identifying_columns]], y=data["Value"], 
                                 name=name, marker_color=consistent_pastel_color_generator(name), showlegend=True))

        return traces
    

class HourlyTechActivityRateFacilitator(HourlyFacilitatorBase):

    def __init__(self, sol_path: Path = None, year: int = None, region: str = None):
        super().__init__(sol_path=sol_path, type_of_data_to_read="RateOfActivity", year=year, region=region, extra_identifying_columns=["Technology"])

    
    @staticmethod
    def _get_relevant_data(sol_path: Path, type_of_data_to_read: str) -> dp.DataProcessor:
        d = HourlyFacilitatorBase._get_relevant_data(sol_path, type_of_data_to_read)
        d.df["Value"] *= d.year_split
        return d

    
    def get_relevant_data(self) -> HourlyFacilitatorBase.RelevantData:
        return HourlyTechActivityRateFacilitator._get_relevant_data(self._sol_path, self._type_of_data_to_read)
    
    def plot(self, traces):

        fig = super().plot(traces)
        fig.update_layout(yaxis_title="Rate of Activity [TWh]")
        return fig
    
class HourlyTechActivityRateSolutionCompareFacilitator(HourlyTechActivityRateFacilitator):

    def __init__(self, tech: str = None, sol_paths: dict[str, Path] = None, year: int = None, region: str = None):
        self._tech = tech
        self._sol_paths = sol_paths
        self._year = year
        self._region = region
        self._extra_identifying_columns = ["Source"]

    def get_relevant_data(self) -> dp.DataProcessor:
        return dp.concat({name: HourlyTechActivityRateFacilitator(path, self._year, self._region).get_relevant_data() for name, path in self._sol_paths.items()})
    
    def generate_traces(self, relevant_data: dp.DataProcessor) -> list[go.Bar]:
        relevant_data.filter_by_identifier(column="Technology", identifier=self._tech)
        return super().generate_traces(relevant_data)
    
    def plot(self, traces) -> go.Figure:
        
        fig = go.Figure()
        fig.add_traces(traces)
        fig.update_layout(barmode='group', xaxis_title="Hour", yaxis_title="Rate of Activity [TWh]")

        return fig