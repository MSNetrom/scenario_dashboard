from pathlib import Path
import plotly.graph_objects as go
import pandas as pd

from typing import NamedTuple
from abc import ABC, abstractmethod

from ..data.data_processor import GeoLocation, DataProcessor, get_region_location
from ..data.config import HEADER_MAPPING
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

class HourlyFacilitatorBase(FacilitatorBase):

    class RelevantData(DataProcessor): pass

    def __init__(self, sol_path: Path = None, type_of_data_to_read: str = None, year: int = None, region: str = None, extra_identifying_columns: list[str] = []):
        self._sol_path = sol_path
        self._type_of_data_to_read = type_of_data_to_read
        self._year = year
        self._region = region
        self._extra_identifying_columns = extra_identifying_columns

    @staticmethod
    def _get_relevant_data(sol_path: Path, type_of_data_to_read: str, year: int, region: str) -> RelevantData:

        d = DataProcessor(sol_path=sol_path, 
                  type_of_data_to_read=type_of_data_to_read, 
                  columns=HEADER_MAPPING[type_of_data_to_read]["columns"], 
                  read_year_split=True)
        
        d.force_numeric(column="TS")
        d.force_numeric(column="Value")

        return d

    def get_relevant_data(self) -> RelevantData:
        return HourlyFacilitatorBase._get_relevant_data(self._sol_path, self._type_of_data_to_read, self._year, self._region)
    
    def generate_traces(self, relevant_data: RelevantData, text="") -> list[go.Bar]:

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

            traces.append(go.Bar(x=data["TS"], y=data["Value"], name=name, marker_color=consistent_pastel_color_generator(name), showlegend=True))

        return traces

    
    def plot(self, relevant_data: RelevantData) -> go.Figure:

        fig = go.Figure()

        fig.add_traces(self.generate_traces(relevant_data))

        fig.update_layout(barmode='stack', xaxis_title="Hour")

        return fig
    
class HourlyTechActivityRateFacilitator(HourlyFacilitatorBase):

    def __init__(self, sol_path: Path = None, year: int = None, region: str = None):
        super().__init__(sol_path=sol_path, type_of_data_to_read="RateOfActivity", year=year, region=region, extra_identifying_columns=["Technology"])

    
    @staticmethod
    def _get_relevant_data(sol_path: Path, type_of_data_to_read: str, year: int, region: str) -> HourlyFacilitatorBase.RelevantData:
        return HourlyFacilitatorBase._get_relevant_data(sol_path, type_of_data_to_read, year, region)

    
    def get_relevant_data(self) -> HourlyFacilitatorBase.RelevantData:
        
        d = super().get_relevant_data()
        d.df["Value"] *= d.year_split  # Rate of activity is given as if the hourly value is the total value for the year

        return d

    def plot(self, relevant_data: HourlyFacilitatorBase.RelevantData) -> go.Figure:

        fig = super().plot(relevant_data)

        fig.update_layout(yaxis_title="Rate of Activity [TWh]")

        return fig
    
class HourlyTechActivityRateSolutionCompareFacilitator(HourlyTechActivityRateFacilitator):

    #RelevantData = dict[str, DataProcessor]

    def __init__(self, tech: str = None, sol_paths: dict[str, Path] = None, year: int = None, region: str = None):
        self._tech = tech
        self._sol_paths = sol_paths
        self._year = year
        self._region = region
        self._extra_identifying_columns = ["Technology"]

    def get_relevant_data(self) -> dict[str, DataProcessor]:
        return {name: HourlyTechActivityRateFacilitator._get_relevant_data(path, "RateOfActivity", self._year, self._region) for name, path in self._sol_paths.items()}
    
    def plot(self, relevant_data: dict[str, DataProcessor]) -> go.Figure:

        traces = []

        for name, data in relevant_data.items():

            # Do filtering
            data.filter_by_identifier(column="Technology", identifier=self._tech)



            #traces += self.generate_traces(data, text=name)
        


        fig = go.Figure()
        fig.add_traces(traces)
        fig.update_layout(barmode='group', xaxis_title="Hour", yaxis_title="Rate of Activity [TWh]")

        return fig
    
class HourlyTechActivityRateSolutionCompareFacilitator2(HourlyTechActivityRateFacilitator):

    #RelevantData = dict[str, DataProcessor]

    def __init__(self, tech: str = None, sol_paths: dict[str, Path] = None, year: int = None, region: str = None):
        self._tech = tech
        self._sol_paths = sol_paths
        self._year = year
        self._region = region
        self._extra_identifying_columns = ["Technology"]

    def get_relevant_data(self) -> pd.DataFrame:
        data = {name: HourlyTechActivityRateFacilitator(path, self._year, self._region).get_relevant_data() for name, path in self._sol_paths.items()}

        # Generate a new df with extra column indicating the source of the data
        d = pd.concat([data[name].df.assign(Source=name) for name in data.keys()])

        return d


    
    def plot(self, relevant_data: pd.DataFrame) -> go.Figure:

        traces = []

        #for name, data in relevant_data.items():

            # Do filtering
        #    data.filter_by_identifier(column="Technology", identifier=self._tech)



            #traces += self.generate_traces(data, text=name)

        relevant_data = relevant_data[relevant_data["Technology"] == self._tech]

        self.generate_traces(relevant_data)
        
        

        fig = go.Figure()
        fig.add_traces(traces)
        fig.update_layout(barmode='group', xaxis_title="Hour", yaxis_title="Rate of Activity [TWh]")

        return fig
    
class StorageDischargeHourlyRateFacilitator(HourlyTechActivityRateFacilitator):

    """
    Plots hourlay rate of techs, but turns storages into two techs, by adding "_Charge" and "_Discharge" to the name
    """

    def __init__(self, sol_path: Path = None, year: int = None, region: str = None):
        super().__init__(sol_path=sol_path, year=year, region=region)

    def get_relevant_data(self) -> HourlyFacilitatorBase.RelevantData:

        d = super().get_relevant_data()
        #d.force_numeric(column="Mode")

        #print(d.df[d.df["Technology"].str.startswith("D_") & (d.df["Mode"] == 1)].head(100))
        
        # Change value to negative for those who starts with "D_", let column "Mode" with value "2" represent discharge
        d.df.loc[d.df["Technology"].str.startswith("D_") & (d.df["Mode"] == 2), "Value"] *= -1

        # Add "Charge" and "Discharge" to the storage technologie names "D_"
        d.df.loc[d.df["Technology"].str.startswith("D_") & (d.df["Mode"] == 1), "Technology"] += "_Charge"
        d.df.loc[d.df["Technology"].str.startswith("D_") & (d.df["Mode"] == 2), "Technology"] += "_Discharge"

        return d

        

class TradeCapacityMapFacilitator(FacilitatorBase):

    class RelevantData(NamedTuple):
        TotalTradeCapacity: DataProcessor
        Locations: dict[str, GeoLocation]


    def __init__(self, sol_path: Path = None, year: int = None):
        self._sol_path = sol_path
        self._year = year

    def get_relevant_data(self) -> RelevantData:

        # Combined
        TotalTradeCapacity = DataProcessor(sol_path=self._sol_path, type_of_data_to_read="TotalTradeCapacity", columns=HEADER_MAPPING["TotalTradeCapacity"]["columns"])
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
                  columns=HEADER_MAPPING["TotalCapacityAnnual"]["columns"])
        
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

    def __init__(self, sol_path: Path = None, type_of_data_to_read: str = None, region: str = None, extra_identifying_columns: list[str] = []):
        self._sol_path = sol_path
        self._type_of_data_to_read = type_of_data_to_read
        self._region = region
        self._extra_identifying_columns = extra_identifying_columns

    def get_relevant_data(self) -> RelevantData:

        d = DataProcessor(sol_path=self._sol_path, 
                  type_of_data_to_read=self._type_of_data_to_read, 
                  columns=HEADER_MAPPING[self._type_of_data_to_read]["columns"])
        
        d.force_numeric(column="Value")

        #d.df = d.df[d.df["Value"] > 0]

        return d
    
    def plot(self, relevant_data: RelevantData) -> go.Figure:

        relevant_data.filter_by_identifier(column="Region", identifier=self._region)

        fig = go.Figure()

        # relevant_data.df.sort_values(by=['Year', 'Value'], ascending= [True, False], inplace=True)

        grouped_df = relevant_data.df.groupby(self._extra_identifying_columns + ["Year", "Region"])

        added_names = set()

        for group, data in grouped_df:


            name = " -> ".join(group[i] for i in range(len(self._extra_identifying_columns))).strip()

            fig.add_trace(go.Scatter(x=data["Year"], y=data["Value"], name=name, fillcolor=consistent_pastel_color_generator(name), 
                                     line_color=consistent_pastel_color_generator(name), stackgroup="one", legendgroup=name, 
                                     showlegend=name not in added_names))
            
            added_names.add(name)

        #print(relevant_data.df.head(10))

        """for entry in relevant_data.df[self._column_to_plot].unique():
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
                            ))"""
            
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

        #relevant_data.filter_by_list(column="Fuel", by_filter=self._fuels)
        
        fig = super().plot(relevant_data)

        fig.update_layout(yaxis_title="Production [TWh]", title="Production of fuel by technology")

        return fig
    

class AnnualUseStackedQuantityEvolutionFacilitator(StackedQuantityEvolutionFacilitatorBase):

    def __init__(self, sol_path: Path = None, region: str = None):
        super().__init__(sol_path=sol_path, type_of_data_to_read="UseAnnual", region=region, extra_identifying_columns=["Fuel"])

    def plot(self, relevant_data: StackedQuantityEvolutionFacilitatorBase.RelevantData) -> go.Figure:

        fig = super().plot(relevant_data)

        fig.update_layout(yaxis_title="Use [TWh]", title="Use of fuels")

        return fig
    

class SurplusEnergyStackedQuantityEvolutionFacilitator(FacilitatorBase):

    class RelevantData(NamedTuple):
        prod_annual: DataProcessor
        use_annual: DataProcessor

    def __init__(self, sol_path: Path = None, region: str = None):
        
        self.prod_annual = StackedQuantityEvolutionFacilitatorBase(sol_path=sol_path, type_of_data_to_read="ProductionByTechnologyAnnual", region=region, extra_identifying_columns=["Technology", "Fuel"])
        self.use_annual = StackedQuantityEvolutionFacilitatorBase(sol_path=sol_path, type_of_data_to_read="UseByTechnologyAnnual", region=region, extra_identifying_columns=["Technology", "Fuel"])