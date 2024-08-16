HEADER_MAPPING = {"TotalCapacityAnnual":
                      {"columns": {"Year": "Numeric", "Technology": "String", "Region": "String", "Value": "Numeric"},
                       "units": "GW"},
                  "RateOfActivity":
                      {"columns": {"Year": "Numeric", "TS": "Numeric", "Technology": "String", "Mode": "Numeric", "Region": "String", "Value": "Numeric"},
                       "units": "TWh"},
                  "ProductionByTechnologyAnnual":
                      {"columns": {"Year": "Numeric", "Technology": "String", "Fuel": "String", "Region": "String", "Value": "Numeric"},
                       "units": "TWh"},
                  "StorageLevelTSStart":
                      {"columns": {"Storage": "String", "Year": "Numeric", "TS": "Numeric", "Region": "String", "Value": "Numeric"},
                       "units": "TWh"},
                  "AccumulatedNewStorageCapacity": {"columns": {"Storage": "String", "Year": "Numeric", "Region": "String", "Value": "Numeric"},
                                                    "units": "TWh"}, 
                  "NewStorageCapacity": {"columns": {"Storage": "String", "Year": "Numeric", "Region": "String", "Value": "Numeric"},
                                                    "units": "TWh"},
                }