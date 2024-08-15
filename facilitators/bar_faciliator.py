import plotly.graph_objects as go
from pathlib import Path

import data.data_processor as dp
from data import HEADER_MAPPING

from .base_faciliator import FacilitatorBase
from .colors import consistent_pastel_color_generator

class BarFacilitator(FacilitatorBase):

    def __init__(self, sol_paths: dict[str, Path], type_of_data_to_read: str = None, x_grouping_columns: list[str] = [], legend_grouping_columns: list[str] = []):
        self._sol_paths = sol_paths
        self._type_of_data_to_read = type_of_data_to_read
        self._x_grouping_columns = x_grouping_columns
        self._legend_grouping_columns = legend_grouping_columns

    @staticmethod
    def _get_relevant_data(sol_paths: Path, type_of_data_to_read: str) -> dp.DataProcessor:

        d = dp.DataProcessor(sol_paths=sol_paths, 
                  type_of_data_to_read=type_of_data_to_read,
                  read_year_split=True)

        return d

    def get_relevant_data(self) -> dp.DataProcessor:
        return BarFacilitator._get_relevant_data(self._sol_paths, self._type_of_data_to_read)
    
    def generate_traces(self, relevant_data: dp.DataProcessor) -> list[go.Bar]:

        traces = []

        grouped_df = relevant_data.df.groupby(self._legend_grouping_columns)

        # Create a bar for each group
        for group, data in grouped_df:

            data = data.sort_values(by=self._x_grouping_columns)
            
            for column in self._x_grouping_columns:
                data[column] = data[column].astype(str)


            name = " ".join(str(group[i]) for i in range(len(self._legend_grouping_columns)))

            ready_data = []
            if len(self._x_grouping_columns) == 1:
                ready_data = data[self._x_grouping_columns[0]].tolist()
            else:
                ready_data = [data[column] for column in self._x_grouping_columns]


            traces.append(go.Bar(x=ready_data, y=data["Value"], 
                                 name=name, marker_color=consistent_pastel_color_generator(name), showlegend=True))

        return traces
    
    def generate_figure(self, traces: list[go.Bar]) -> go.Figure:

        fig = go.Figure()

        fig.add_traces(traces)
            
        fig.update_layout(
            barmode='stack'
        )

        return fig