from pathlib import Path
import plotly.graph_objects as go
import pandas as pd

from typing import NamedTuple
from abc import ABC, abstractmethod

from .data_raw2 import GeoLocation, DataProcessor, get_region_location
from .config import header_mapping
from .colors import consistent_pastel_color_generator

class FacilitatorBase(ABC):

    class RelevantData:
        pass

    @abstractmethod
    def get_relevant_data(self) -> RelevantData:
        pass

    @abstractmethod
    def plot(self, relevant_data: RelevantData) -> go.Figure:
        pass

class TradeCapacityMapFacilitator(FacilitatorBase):

    class RelevantData(NamedTuple):
        TotalTradeCapacity: DataProcessor
        Locations: dict[str, GeoLocation]


    def __init__(self, sol_path: Path = None, year: int = None):
        self._sol_path = sol_path
        self._year = year

    def get_relevant_data(self) -> RelevantData:

        # Combined
        TotalTradeCapacity = DataProcessor(sol_path=self._sol_path, type_of_data_to_read="TotalTradeCapacity", columns=header_mapping["TotalTradeCapacity"]["columns"])
        TotalTradeCapacity.filter_by_identifier(column="Year", identifier=self._year)
        TotalTradeCapacity.df = TotalTradeCapacity.df.dropna(subset=["Value"])
        TotalTradeCapacity.df = TotalTradeCapacity.df[TotalTradeCapacity.df["Value"] > 0]

        # They seem to have the same data two times, like Region1 -> Region2 and Region2 -> Region1
        TotalTradeCapacity.df = TotalTradeCapacity.df[TotalTradeCapacity.df["Region1"] < TotalTradeCapacity.df["Region2"]]

        # Sum idetical entries
        TotalTradeCapacity.sum_identical_entries(column_to_sum="Value")

        return TradeCapacityMapFacilitator.RelevantData(
            TotalTradeCapacity=TotalTradeCapacity,
            Locations=get_region_location()
        )
    
    @staticmethod
    def plot(relevant_data: RelevantData) -> go.Figure:

        fig = go.Figure()
        lataxis = [35, 70]
        lonaxis = [-9.7, 38]

        # Aggregate all fuels together to 1, if there is more than 1 fuel

        max_capacity = relevant_data.TotalTradeCapacity.df["Value"].max()
        max_line_width = 20

        for _, row in relevant_data.TotalTradeCapacity.df.iterrows():

            
            lat_2, lat_1 = relevant_data.Locations[row['Region2']].latitude, relevant_data.Locations[row['Region1']].latitude
            lon_2, lon_1 = relevant_data.Locations[row['Region2']].longitude, relevant_data.Locations[row['Region1']].longitude

            fig.add_trace(go.Scattergeo(
                locationmode='country names',
                lat=[lat_2, lat_1],
                lon=[lon_2, lon_1],
                mode='lines+markers',
                name = row['Region1'] + " " + row['Region2'],
                legendgroup = row['Region1'] + " " + row['Region2'],  #row["Value"],
                showlegend=False,
                line=dict(width= (row["Value"] / max_capacity) * max_line_width,
                        color='#f4b6c2'),)) 

        for _, row in relevant_data.TotalTradeCapacity.df.iterrows():

            lat_2, lat_1 = relevant_data.Locations[row['Region2']].latitude, relevant_data.Locations[row['Region1']].latitude
            lon_2, lon_1 = relevant_data.Locations[row['Region2']].longitude, relevant_data.Locations[row['Region1']].longitude

            lat_inc = lat_1 - lat_2
            lon_inc = lon_1 - lon_2
            fig.add_trace(go.Scattergeo(
                locationmode='country names',
                lat=[lat_2 + lat_inc * 0.499], #(lat_2-lat_1,lat_2-lat_1),  # Example latitude for New York
                lon=[lon_2 + lon_inc * 0.499], #(lon_2-lon_1,lon_2-lon_1),  # Example longitude for New York
                mode='text',  # Only display text
                text=f'{row["Value"]: .2f} GW',  # Manually added text
                textposition="top center",
                showlegend=False,
                textfont=dict(size=8, color='black'),
            ))

        
        fig.update_layout(title_text=f'Total Trade Capacities [GW]',
                          height=900, width=1620,
                          geo=(go.layout.Geo(
                              lataxis=dict(range=[lataxis[0], lataxis[1]]),
                              lonaxis=dict(range=[lonaxis[0], lonaxis[1]]),
                              showland=True,
                              showlakes=True,
                              lakecolor="#DEF4FC",
                              showcountries=True,
                              countrycolor='white',  # Border color
                              countrywidth=1,  # Border width
                              showcoastlines=False,
                              showocean=True,
                              oceancolor="#DCFBFB",
                              landcolor='rgb(229, 229, 229)')))
        return fig
    
class StackedQuantityEvolutionFacilitator(FacilitatorBase):

    class RelevantData(DataProcessor): pass

    def __init__(self, sol_path: Path = None, region: str = None):
        self._sol_path = sol_path
        self._region = region

    def get_relevant_data(self) -> RelevantData:

        d = DataProcessor(sol_path=self._sol_path, 
                  type_of_data_to_read="TotalCapacityAnnual", 
                  columns=header_mapping["TotalCapacityAnnual"]["columns"])
        
        d.force_numeric(column="Value")

        return d
    
    def plot(self, relevant_data: RelevantData) -> go.Figure:

        relevant_data.filter_by_identifier(column="Region", identifier=self._region)

        fig = go.Figure()

        relevant_data.df.sort_values(by=['Year', 'Value'], ascending= [True, False], inplace=True)
        for t in relevant_data.df['Technology'].unique():
            # Add trace to subplot
            fig.add_trace(go.Scatter(x=relevant_data.df[relevant_data.df['Technology'] == t]['Year'],
                                y=relevant_data.df[relevant_data.df['Technology'] == t]['Value'],
                                mode='lines',
                                name=t,
                                #fill='tonexty',
                                fillcolor=consistent_pastel_color_generator(t),  #self.color_to_tech[t],
                                line_color=consistent_pastel_color_generator(t),
                                stackgroup="one",
                                legendgroup=t,
                                showlegend=True,
                            ))
            
        fig.update_layout(
                        xaxis_title="Year",
                        barmode='stack',
                        font=dict(size=22)
                        )
                    
        return fig
    
    
class StackedQuantityEvolutionFacilitatorBase(FacilitatorBase):

    class RelevantData(DataProcessor): pass

    def __init__(self, sol_path: Path = None, type_of_data_to_read: str = None, region: str = None, column_to_plot: str = None):
        self._sol_path = sol_path
        self._type_of_data_to_read = type_of_data_to_read
        self._region = region
        self._column_to_plot = column_to_plot

    def get_relevant_data(self) -> RelevantData:

        d = DataProcessor(sol_path=self._sol_path, 
                  type_of_data_to_read=self._type_of_data_to_read, 
                  columns=header_mapping[self._type_of_data_to_read]["columns"])
        
        d.force_numeric(column="Value")

        return d
    
    def plot(self, relevant_data: RelevantData) -> go.Figure:

        relevant_data.filter_by_identifier(column="Region", identifier=self._region)

        fig = go.Figure()

        relevant_data.df.sort_values(by=['Year', 'Value'], ascending= [True, False], inplace=True)
        for entry in relevant_data.df[self._column_to_plot].unique():
            # Add trace to subplot
            fig.add_trace(go.Scatter(x=relevant_data.df[relevant_data.df[self._column_to_plot] == entry]['Year'],
                                y=relevant_data.df[relevant_data.df[self._column_to_plot] == entry]['Value'],
                                mode='lines',
                                name=entry,
                                #fill='tonexty',
                                fillcolor=consistent_pastel_color_generator(entry),  #self.color_to_tech[t],
                                line_color=consistent_pastel_color_generator(entry),
                                stackgroup="one",
                                legendgroup=entry,
                                showlegend=True,
                            ))
            
        fig.update_layout(
                        xaxis_title="Year",
                        barmode='stack',
                        font=dict(size=22)
                        )
                    
        return fig
