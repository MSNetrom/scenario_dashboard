import plotly.graph_objects as go
from pathlib import Path

import data.data_processor as dp
from data import HEADER_MAPPING

from .base_faciliator import FacilitatorBase
from .colors import consistent_pastel_color_generator

class StackedQuantityEvolutionFacilitatorBase(FacilitatorBase):

    class RelevantData(dp.DataProcessor): pass

    def __init__(self, sol_path: Path = None, type_of_data_to_read: str = None, region: str = None, extra_identifying_columns: list[str] = []):
        self._sol_path = sol_path
        self._type_of_data_to_read = type_of_data_to_read
        self._region = region
        self._extra_identifying_columns = extra_identifying_columns

    def get_relevant_data(self) -> RelevantData:

        d = dp.DataProcessor(sol_path=self._sol_path, 
                  type_of_data_to_read=self._type_of_data_to_read, 
                  columns=HEADER_MAPPING[self._type_of_data_to_read]["columns"])
        
        d.force_numeric(column="Value")

        d.df = d.df[d.df["Value"] > 0]

        return d
    
    def generate_traces(self, relevant_data: RelevantData) -> list[go.Scatter]:

        traces = []

        relevant_data.filter_by_identifier(column="Region", identifier=self._region)

        grouped_df = relevant_data.df.groupby(self._extra_identifying_columns + ["Year", "Region"])

        added_names = set()

        for group, data in grouped_df:

            name = " -> ".join(group[i] for i in range(len(self._extra_identifying_columns))).strip()

            traces.append(go.Scatter(x=data["Year"], y=data["Value"], name=name, fillcolor=consistent_pastel_color_generator(name), 
                                     line_color=consistent_pastel_color_generator(name), stackgroup="one", legendgroup=name, 
                                     showlegend=name not in added_names))
            
            added_names.add(name)

        return traces        
    
    def plot(self, traces: list[go.Scatter]) -> go.Figure:

        fig = go.Figure()

        fig.add_traces(traces)
            
        fig.update_layout(
                        xaxis_title="Year",
                        barmode='stack',
                        font=dict(size=22)
                        )
                    
        return fig


class ProductionByTechnologyForFuelStackedQuantityEvolutionFacilitator(StackedQuantityEvolutionFacilitatorBase):

    def __init__(self, sol_path: Path = None, region: str = None, fuels: list[str] = []):
        self._fuels = fuels
        super().__init__(sol_path=sol_path, type_of_data_to_read="ProductionByTechnologyAnnual", region=region, extra_identifying_columns=["Technology", "Fuel"])

    def get_relevant_data(self) -> StackedQuantityEvolutionFacilitatorBase.RelevantData:
        
        relevant_data = super().get_relevant_data()

        relevant_data.filter_by_list(column="Fuel", by_filter=self._fuels)
        
        return relevant_data
    
    def plot(self, relevant_data: StackedQuantityEvolutionFacilitatorBase.RelevantData) -> go.Figure:
        
        fig = super().plot(relevant_data)

        fig.update_layout(yaxis_title="Production [TWh]", title="Production of fuel by technology")

        return fig