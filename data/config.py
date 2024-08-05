aggregation = {
    'P_Nuclear': 'Nuclear',
    'P_Coal_Hardcoal': 'Hardcoal',
    'P_Coal_Lignite': 'Lignite',
    'P_Oil': 'Oil',
    'P_Gas_OCGT': 'Gas',
    'P_Gas_CCGT': 'Gas',
    'P_Gas_CCS': 'Gas',
    'P_Gas_Engines': 'Gas',
    'RES_Hydro_Large': 'Hydro Reservoir',
    'RES_Hydro_Small': 'Hydro Run-of-River',
    'RES_Wind_Offshore_Deep': 'Wind Offshore',
    'RES_Wind_Offshore_Transitional': 'Wind Offshore',
    'RES_Wind_Offshore_Shallow': 'Wind Offshore',
    'RES_Wind_Onshore_Opt': 'Wind Onshore',
    'RES_Wind_Onshore_Avg': 'Wind Onshore',
    'RES_Wind_Onshore_Inf': 'Wind Onshore',
    'RES_PV_Utility_Opt': 'PV',
    'RES_PV_Utility_Avg': 'PV',
    'RES_PV_Rooftop_Residential': 'PV',
    'Res_PV_Utility_Tracking': 'PV',
    'RES_PV_Utility_Inf': 'PV',
    'RES_PV_Rooftop_Commercial': 'PV',
    'P_Biomass': 'Biomass',
    'P_Biomass_CCS': 'Biomass',
    'D_PHS': "Pumped Hydro",
    'D_Battery_Li-Ion': 'Battery Li-Ion',
    'D_PHS_Residual': "Pumped Hydro",
}

colour_codes = {
    'Nuclear': 'rgb(112,112,112)',
    'Hardcoal': 'rgb(229,229,229)',
    'Gas': 'rgb(224,91,9)',
    'Pumped Hydro': '#51dbcc',
    'Oil': 'black',
    'Biomass': 'rgb(186,167,65)',
    'Hydro Reservoir': 'rgb(7,154,136)',
    'Hydro Run-of-River': 'rgb(8,173,151)',
    'PV': 'rgb(249,208,2, 1)',
    'Wind Onshore': 'rgb(35,94,188)',
    'Wind Offshore': 'rgb(104,149,221)',
    'Hydrogen': 'rgb(191,0,191)',
    'X_Electrolysis': 'magenta',
    'solar_rooftop': 'rgb(255,239,96)',
    'solar_tracking': 'rgb(255,246,191)',
    'Transport': 'rgb(37,160,139)',
    'Industry': 'rgb(234,197,99)',
    'Buildings': 'rgb(240,243,190)',
    'Demand': 'rgb(223,222,220)',  # rgb(166,193,214),
    'DK': 'rgb(42,157,142)',
    'UK': 'rgb(230,111,81)',
    'Power': 'rgb(38,70,83)',
    'NO1': 'rgb(37,160,139)',
    'NO3': 'rgb(234,197,99)',
    'NO4': 'rgb(240,243,190)',
    'NO5': 'rgb(199,197,193)',
    'NO2': 'rgb(230,111,81)'

}

agg_countries = {
    'NO': ['NO1', 'NO2', 'NO3', 'NO4', 'NO5', 'OFF_NO'],
}

order_legend = ['Gas', 'Nuclear', 'Oil', 'Biomass', 'Hydro Reservoir', 'Hydro Run-of-River', 'Pumped Hydro', 'Wind Onshore', 'Wind Offshore', 'PV']

header_mapping = {"TotalCapacityAnnual":
                      {"columns": ["Year", "Technology", "Region", "Value"],
                       "units": "GW"},
                  "ProductionByTechnology":
                      {"columns": ["Year", "TS","Technology", "Fuel", "Region", "Value"],
                       "units": "TWh"},
                  "RateOfActivity":
                      {"columns": ["Year", "TS", "Technology", "Mode", "Region", "Value"],
                       "units": "TWh"},
                  "ProductionByTechnologyAnnual":
                      {"columns": ["Year", "Technology", "Fuel", "Region", "Value"],
                       "units": "TWh"},
                  "StorageLevelTSStart":
                      {"columns": ["Technology", "Year", "TS", "Region", "Value"],
                       "units": "TWh"},
                  "UseAnnual":
                      {"columns": ["Year", "Fuel", "Region", "Value"],
                       "units": "TWh"},
                  "TotalDiscountedCostByTechnology":
                      ["Year", "Technology", "Region", "Value"],
                  "TotalTradeCapacity":
                      {"columns": ["Year", "Fuel", "Region1", "Region2", "Value"],
                       "units": "GW"},
                  "Export":
                      {"columns": ["Year", "TS", "Fuel", "Region1", "Region2", "Value"]},
                  "UseByTechnologyAnnual": 
                        {"columns": ["Year", "Technology", "Fuel", "Region", "Value"],
                         "units": "TWh"}, 
                    }

# UseByTechnologyAnnual[2018,A_Rooftop_Commercial,Area_Rooftop_Commercial,AT]

key_to_julia = {'capacities': 'TotalCapacityAnnual',
                'trade_map': 'TotalTradeCapacity',
                'demand': 'UseAnnual',
                'storage_level': 'StorageLevelTSStart',
                'operation': 'ProductionByTechnology',
                'export': "Export",
                'discountedcosts': 'TotalDiscountedCostByTechnology',
                'hydrogen_infrastructure': "Export"}

hydrogen_technologies =["X_Electrolysis"]