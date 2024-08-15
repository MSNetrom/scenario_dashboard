import plotly.graph_objects as go
from pathlib import Path
from typing import Callable

import data.data_processor as dp

from .base_faciliator import FacilitatorBase
from .colors import my_color_generator

class StackedQuantityEvolutionFacilitatorBase(FacilitatorBase):

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

        return d
    
    def generate_traces(self, relevant_data: RelevantData) -> list[go.Scatter]:

        traces = []

        relevant_data.df = relevant_data.df.sort_values(by=self._extra_identifying_columns)

        grouped_df = relevant_data.df.groupby(self._extra_identifying_columns)

        added_names = set()

        for group, data in grouped_df:

            name = " -> ".join(group[i] for i in range(len(self._extra_identifying_columns))).strip()

            traces.append(go.Scatter(x=data["Year"], y=data["Value"], name=name, fillcolor=self._color_generator(name), 
                                     line_color=self._color_generator(name), stackgroup="one", legendgroup=name, 
                                     showlegend=name not in added_names))
            
            added_names.add(name)

        return traces        
    
    def generate_figure(self, traces: list[go.Scatter]) -> go.Figure:

        fig = go.Figure()

        fig.add_traces(traces)
            
        fig.update_layout(
                        xaxis_title="Year",
                        barmode='stack',
                        font=dict(size=22),
                        legend={'traceorder': 'reversed'}
                        )
                    
        return fig