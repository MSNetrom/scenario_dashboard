import pandas as pd
from data.config import colour_codes, header_mapping, key_to_julia
from itertools import cycle
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from data.data_class import read_geojson_file

from .colors import consistent_pastel_color_generator

class PlotObject:

    def __init__(self, key, df_list, scenarios, year=None, sector="Power"):
        self.df_list = df_list
        self.year = year if year is not None else self.df_list[0]['Year'].unique()
        self.key = key_to_julia[key]
        self.sector = sector
        self.scenarios = scenarios
        self.color_to_tech = self.create_col_palette() if key not in ["trade_map", "hydrogen_infrastructure",
                                                                      "export"] else ""

    def create_col_palette(self):
        ## cycle through color palette
        palette = cycle(px.colors.qualitative.Light24)
        technology_list = []
        

        for df in self.df_list:
            technology_list += list(df['Technology'].unique())

        return {t: colour_codes[t] if t in colour_codes.keys() else next(palette) for t in
                pd.Series(technology_list).unique()}

    def stacked_bar_integrated(self, aggregation=True):
        """
        Generate a stacked bar plot integrated with subplots.

        Args:
            aggregation (bool, optional): Whether to aggregate the data. Defaults to True.

        Returns:
            plotly.graph_objs._figure.Figure: The generated figure object.
        """

        # Create subplots
        fig = make_subplots(rows=len(self.year),
                            cols=1,
                            subplot_titles=[f'{self.key}_{int(y)}_{self.sector}' for y in self.year])

        list_technology = []
        # Iterate over dataframes and scenarios
        for df, s in zip(self.df_list, self.scenarios):
            # Apply aggregation if required
            region_col = 'Region'
            if aggregation:
                df = df.groupby(by=['Year', 'Technology', 'Region_agg'], as_index=False).sum(numeric_only=True)
                region_col = 'Region_agg'
            df['Scenario'] = s

            # Iterate over years
            for j, y in enumerate(self.year, start=1):
                # Iterate over unique technologies for each year
                for t in df[df['Year'] == y]['Technology'].unique():
                    # Add trace to subplot
                    fig.add_trace(go.Bar(x=[df[(df['Year'] == y) & (df['Technology'] == t)][region_col],
                                            df[(df['Year'] == y) & (df['Technology'] == t)]['Scenario']],
                                         y=df[(df['Year'] == y) & (df['Technology'] == t)]['Value'],
                                         name=t,
                                         marker_color=self.color_to_tech[t],
                                         legendgroup=t,
                                         showlegend=True if t not in list_technology else False,
                                         ), row=j, col=1)
                    list_technology.append(t)

        # Update layout of the figure
        fig.update_layout(barmode='stack', height=2700, font=dict(size=26))
        fig.update_yaxes(title_text=header_mapping[self.key]["units"])

        return fig

    def stacked_bar_side(self, list_dfs, x="Year", yearly=False):

        # make subplot titles
        region_list = pd.Series([i for df in self.df_list for i in df['Region']]).unique()
        fig = make_subplots(rows=len(region_list),
                            cols=len(self.scenarios),
                            subplot_titles=[f"{r}_{s}" for r in region_list for s in self.scenarios])

        for i, df in enumerate(list_dfs, start=1):
            if yearly:
                df = df[df["Year"] == 2050]
            list_technology = []
            for j, r in enumerate(region_list, start=1):
                # check if region is in data
                if df['Region'].str.contains(r).any():
                    # sum and sort
                    technologies = \
                        df[df['Region'] == r].groupby(by=['Technology'], as_index=False).sum().sort_values(by="Value")[
                            'Technology'].unique()
                    for t in technologies:
                        fig.add_trace(go.Scatter(x=df[(df['Region'] == r) & (df['Technology']== t)][x],
                                                 y=df[(df['Region'] == r) & (df['Technology'] == t)]['Value'],
                                                 name=t,
                                                 mode='lines',
                                                 fillcolor=consistent_pastel_color_generator(t),  #self.color_to_tech[t],
                                                 line_color=consistent_pastel_color_generator(t),  #self.color_to_tech[t],
                                                 legendgroup=t,
                                                 stackgroup=r,
                                                 showlegend=True if t not in list_technology else False,
                                                 ), row=j, col=i)
                        list_technology.append(t)

        fig.update_yaxes(title_text=header_mapping[self.key]["units"])
        fig.update_layout(
                        height=450*len(region_list),
                          barmode='stack',
                          font=dict(size=22)
                          )
        return fig

    def create_dict_tade_geo_fig(self, capacities=[]) -> dict[str, list[go.Figure]]:
        """
        Create dictionary with scenario key word
        Workaround bc multi-plots are too complicated for scatter_geo
        capacities: list of hydrogen capacities
        """
        scenario_to_year = {}
        self.year = [2018, 2050]
        if not capacities:
            for df, s in zip(self.df_list, self.scenarios):
                scenario_to_year[s] = [
                    self.plot_trade_capacity(df=df[df['Year'] == y], year=y, scenario=s, geojson=read_geojson_file(),
                                             pie_chart=True)
                    for y in self.year]
        else:
            for df, s, c in zip(self.df_list, self.scenarios, capacities):
                scenario_to_year[s] = [
                    self.plot_trade_capacity(df=df[df['Year'] == y], year=y, capacities=c, scenario=s,
                                             geojson=read_geojson_file(), pie_chart=True)
                    for y in self.year]

        return scenario_to_year

    def plot_trade_capacity(self, df, year, scenario, geojson, show_marker=False, capacities=None, pie_chart=False) -> go.Figure:
        fig = go.Figure()
        lataxis = [35, 70]
        lonaxis = [-9.7, 38]
        df.reset_index(inplace=True)
        for index, row in df.iterrows():
            # when there is no line back for offshore nodes
            try:
                i = max(row['Value'],
                        df[(df['Region1'] == row['Region2']) & (df['Region2'] == row['Region1'])]['Value'].values[0])
            except IndexError:
                i = row['Value']

            try:
                lat = geojson[row['Region2']]['latitude'], geojson[row['Region1']]['latitude']
                lon = geojson[row['Region2']]['longitude'], geojson[row['Region1']]['longitude']
            except KeyError:
                print(f"{row['Region2'], row['Region1']} Key not found in available data")

            fig.add_trace(go.Scattergeo(
                locationmode='country names',
                lat=[geojson[row['Region2']]['latitude'], geojson[row['Region1']]['latitude']],
                lon=[geojson[row['Region2']]['longitude'], geojson[row['Region1']]['longitude']],
                mode='lines+markers',
                name=f'{i: .2f} GW',
                text=f'{i: .2f} GW',
                legendgroup=row["Value"],
                showlegend=True if (index == 0) | (index == (df.shape[0] - 1)) else False,
                line=dict(width=1 if show_marker else i,
                          color='grey'),  # if (capacities is None and pie_chart is False) else "rgb(0,191,191)"),
                marker=dict(size=5 if (capacities is None and pie_chart is False) else 1,
                            color="black",
                            line_color='black',
                            line_width=0.5,
                            sizemode='area')))

            if show_marker:
                fig.add_trace(go.Scattergeo(
                    locationmode='country names',
                    lat=[(geojson[row['Region2']]['latitude'] + geojson[row['Region1']]['latitude']) / 2],
                    lon=[(geojson[row['Region2']]['longitude'] + geojson[row['Region1']]['longitude']) / 2],
                    mode='text',
                    name=f'<b>{i: .2f}</b>',
                    showlegend=False,
                    textfont=dict(color='black', size=9),
                    # textposition='middle center',
                    text=f'{i: .1f}', ))
        if capacities is not None:
            # plot pie charts with capacities
            if pie_chart:
                list_traces = make_pie_chart_capacities(capacities, geojson, lataxis, lonaxis, year)
                for i in list_traces:
                    fig.add_trace(i)
            else:
                for index, row in capacities.iterrows():
                    fig.add_trace(go.Scattergeo(
                        locationmode='country names',
                        lat=[geojson[row['Region']]['latitude']],
                        lon=[geojson[row['Region']]['longitude']],
                        mode='markers',
                        name=f'{row["Region"]}, {row["Value"]: .2f} GW',
                        # text=f'{i: .2f} GW',
                        legendgroup=row["Value"],
                        showlegend=True if (index == 0) | (index == capacities.shape[0] - 1) else False,
                        marker=dict(size=row['Value'] / 3,
                                    color=colour_codes['Hydrogen'] if row['Value'] > 0 else "rgb(229,229,229)",
                                    line_width=0.5,
                                    sizemode='area')))

        fig.update_layout(title_text=f'Total Trade Capacities [GW] for {scenario} in {year}',
                          height=2000,
                          geo=(go.layout.Geo(
                              lataxis=dict(range=[lataxis[0], lataxis[1]]),
                              lonaxis=dict(range=[lonaxis[0], lonaxis[1]]),
                              showland=True,
                              countrycolor='white',
                              # oceancolor="rgb(0,35,74)",
                              # showframe=False,
                              showlakes=True,
                              # lakecolor="rgb(0,35,74)",
                              # coastlinecolor='rgb(0,35,74)',
                              showcoastlines=False,
                              landcolor='rgb(229, 229, 229)')))
        return fig


def make_pie_chart_capacities(capacities: list, geojson: dict, lataxis: list, lonaxis: list, year: int) -> list:
    """
    Create pie chart traces based on capacities data.

    Parameters:
    - capacities (List[Dict[str, Any]]): A list of dictionaries containing capacities data.
    - geojson (Dict[str, Any]): A dictionary containing geojson data.
    - lataxis (List[float]): A list containing latitude axis limits.
    - lonaxis (List[float]): A list containing longitude axis limits.
    - year (int): The year for which the data is to be plotted.

    Returns:
    - list_traces (List[Any]): A list of pie chart traces.
    """
    list_traces = []

    # Iterate over unique regions
    for r in capacities["Region"].unique():
        x_domain = (geojson[r]['longitude'] - lonaxis[0]) / (lonaxis[1] - lonaxis[0])
        y_domain = (geojson[r]['latitude'] - lataxis[0]) / (lataxis[1] - lataxis[0])

        # Extract colors for the pie chart
        colors = [consistent_pastel_color_generator(tech, factor=0.3) for tech in capacities[(capacities['Region'] == r) & (capacities["Year"] == year)]["Technology"]]
            
        # Check if there is data for the year
        if capacities[(capacities['Region'] == r) & (capacities["Year"] == year)]['Value'].sum() > 0:
            pie_trace = go.Pie(
                labels=capacities[(capacities['Region'] == r) & (capacities["Year"] == year)]['Technology'],
                values=capacities[(capacities['Region'] == r) & (capacities["Year"] == year)]['Value'],
                marker={"colors": colors},
                textinfo='none',
                domain=dict(x=[max(0, x_domain - 0.025), x_domain + 0.025],
                            y=[max(0, y_domain - 0.025), y_domain + 0.025]),
                title=r
            )
            list_traces.append(pie_trace)
    return list_traces
