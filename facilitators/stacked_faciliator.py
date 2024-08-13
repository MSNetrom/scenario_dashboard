import plotly.graph_objects as go
from pathlib import Path
from typing import Callable

import data.data_processor as dp
from data import HEADER_MAPPING

from .base_faciliator import FacilitatorBase
from .colors import my_color_generator

class StackedQuantityEvolutionFacilitatorBase2(FacilitatorBase):

    class RelevantData(dp.DataProcessor): pass

    def __init__(self, sol_path: Path = None, type_of_data_to_read: str = None,
                 extra_identifying_columns: list[str] = [],
                 color_generator: Callable[[str], str] = my_color_generator):
        self._sol_path = sol_path
        self._type_of_data_to_read = type_of_data_to_read
        self._extra_identifying_columns = extra_identifying_columns
        self._color_generator = color_generator

    def get_relevant_data(self) -> RelevantData:

        d = dp.DataProcessor(sol_paths={"anonym": self._sol_path}, 
                  type_of_data_to_read=self._type_of_data_to_read)
        
        d.force_numeric(column="Value")

        #d.df = d.df[d.df["Value"] > 0]

        return d
    
    def generate_traces(self, relevant_data: RelevantData) -> list[go.Scatter]:

        traces = []

        #relevant_data.filter_by_identifier(column="Region", identifier=self._region)
        relevant_data.df = relevant_data.df.sort_values(by=self._extra_identifying_columns)

        grouped_df = relevant_data.df.groupby(self._extra_identifying_columns)

        #grouped_df = sorted(grouped_df, key=lambda x: x[1][x[1]["Year"] == 2050]["Value"].sum(), reverse=True)

        # Sort groups based on value in 2050
        #print("Test:", grouped_df)
        #grouped_df = sorted(grouped_df, key=lambda x: x[1][x[1]["Year"] == 2050]["Value"].sum(), reverse=True)

        added_names = set()

        for group, data in grouped_df:

            name = " -> ".join(group[i] for i in range(len(self._extra_identifying_columns))).strip()

            traces.append(go.Scatter(x=data["Year"], y=data["Value"], name=name, fillcolor=self._color_generator(name), 
                                     line_color=self._color_generator(name), stackgroup="one", legendgroup=name, 
                                     showlegend=name not in added_names))
            
            added_names.add(name)

        return traces        
    
    def plot(self, traces: list[go.Scatter]) -> go.Figure:

        fig = go.Figure()

        fig.add_traces(traces)
            
        fig.update_layout(
                        xaxis_title="Year",
                        barmode='stack',
                        font=dict(size=22),
                        legend={'traceorder': 'reversed'}
                        )
                    
        return fig

class StackedQuantityEvolutionFacilitatorBase(FacilitatorBase):

    class RelevantData(dp.DataProcessor): pass

    def __init__(self, sol_path: Path = None, type_of_data_to_read: str = None, 
                 region: str = None, extra_identifying_columns: list[str] = [],
                 color_generator: Callable[[str], str] = my_color_generator):
        self._sol_path = sol_path
        self._type_of_data_to_read = type_of_data_to_read
        self._region = region
        self._extra_identifying_columns = extra_identifying_columns
        self._color_generator = color_generator

    def get_relevant_data(self) -> RelevantData:

        d = dp.DataProcessor(sol_paths={"anonym": self._sol_path}, 
                  type_of_data_to_read=self._type_of_data_to_read)
        
        d.force_numeric(column="Value")

        #d.df = d.df[d.df["Value"] > 0]

        return d
    
    def generate_traces(self, relevant_data: RelevantData) -> list[go.Scatter]:

        traces = []

        relevant_data.filter_by_identifier(column="Region", identifier=self._region)
        relevant_data.df = relevant_data.df.sort_values(by=self._extra_identifying_columns)

        grouped_df = relevant_data.df.groupby(self._extra_identifying_columns + ["Year", "Region"])

        added_names = set()

        for group, data in grouped_df:

            name = " -> ".join(group[i] for i in range(len(self._extra_identifying_columns))).strip()

            traces.append(go.Scatter(x=data["Year"], y=data["Value"], name=name, fillcolor=self._color_generator(name), 
                                     line_color=self._color_generator(name), stackgroup="one", legendgroup=name, 
                                     showlegend=name not in added_names))
            
            added_names.add(name)

        return traces        
    
    def plot(self, traces: list[go.Scatter]) -> go.Figure:

        fig = go.Figure()

        fig.add_traces(traces)
            
        fig.update_layout(
                        xaxis_title="Year",
                        barmode='stack',
                        font=dict(size=22),
                        legend={'traceorder': 'reversed'}
                        )
                    
        return fig


class ProductionByTechnologyForFuelStackedQuantityEvolutionFacilitator(StackedQuantityEvolutionFacilitatorBase):

    def __init__(self, sol_path: Path = None, region: str = None, fuels: list[str] = []):
        self._fuels = fuels
        super().__init__(sol_path=sol_path, type_of_data_to_read="ProductionByTechnologyAnnual", region=region, extra_identifying_columns=["Technology", "Fuel"])

    def get_relevant_data(self) -> StackedQuantityEvolutionFacilitatorBase.RelevantData:
        
        relevant_data = super().get_relevant_data()

        relevant_data.filter_by_list(column="Fuel", identifier_list=self._fuels)
        
        return relevant_data
    
    def plot(self, relevant_data: StackedQuantityEvolutionFacilitatorBase.RelevantData) -> go.Figure:
        
        fig = super().plot(relevant_data)

        fig.update_layout(yaxis_title="Production [TWh]", title="Production of fuel by technology")

        return fig