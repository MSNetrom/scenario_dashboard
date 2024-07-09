import plotly.graph_objects as go
import pandas as pd

from .colors import consistent_pastel_color_generator

class PlotCreator:

    def __init__(self, df: pd.DataFrame):
        self._df = df.copy()

    #def sum_aggregate_column

    def plot_stacked_quantity_evolution(self, region: str, stacked_column: str = "Technology") -> go.Figure:

        # Use Year along x-axis, Quantity along y-axis, and Technology as stacked bars
        fig = go.Figure()

        # Loop years
        #for j, y in enumerate(self.year, start=1):
                # Iterate over unique technologies for each year
        #for t in self.df[self.df['Year'] == y]['Technology'].unique():

        #for y in self._df['Year'].unique():
        self._df.sort_values(by=['Year', 'Value'], ascending= [True, False], inplace=True)
        for t in self._df['Technology'].unique():
            # Add trace to subplot
            #print(self._df[(self._df['Year'] == y) & (self._df['Technology'] == t) & (self._df["Region"] == region)]['Year'])
            #print(self._df[(self._df['Year'] == y) & (self._df['Technology'] == t) & (self._df["Region"] == region)]['Value'])
            fig.add_trace(go.Scatter(x=self._df[(self._df['Technology'] == t) & (self._df["Region"] == region)]['Year'],
                                y=self._df[(self._df['Technology'] == t) & (self._df["Region"] == region)]['Value'],
                                mode = 'lines',
                                name=t,
                                #fill='tonexty',
                                fillcolor=consistent_pastel_color_generator(t),  #self.color_to_tech[t],
                                line_color=consistent_pastel_color_generator(t),
                                stackgroup="one",
                                legendgroup=t,
                                showlegend=True,
                            ))
            
        fig.update_layout(
                        title=f"Quantity evolution in {region}",
                        xaxis_title="Year",
                        yaxis_title="Quantity [TWh]",
                        barmode='stack',
                        font=dict(size=22)
                        )
                    
        return fig

