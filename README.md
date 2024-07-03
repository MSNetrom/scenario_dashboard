# scenario_dashboard GENeSYS-MOD
The Global Energy System Model (GENeSYS-MOD) - Scenario Dashboard

## Functionality 
This Dashboard aims to visualize model outputs from GENeSYS-MOD in a more efficient way. The following options are currently available: 
- Installed Capacity (Power Sector)
- Total Production (Power Sector)
- Export (Power Sector)
- Transmission & Generation Expansion (Power Sector)

## Installation 
1. Clone the repository
Run the following command in your terminal:
```
git clone https://github.com/danareu/scenario_dashboard.git
```
2. Install the required dependencies <br />
For **conda**; Do: ```conda env create -f environment.yml```, Activate: ```conda activate scenario_dashboard```.
<br/>**Or** - Create a virutal environment and install the dependencies from *requirements.txt*

3. Run main.py <br />
Run main.py and click on the link that is shown in the terminal. E.g.:<br />

```
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'main'
 * Debug mode: on
```

## Dependencies
The scenario_dashboard was written and tested with Python 3.9.
It requires the following Python packages:
- pandas
- dash_bootstrap_components
- dash
- pyyaml
- tkinter
- itertools
- json
- plotly


## Usage
1. After running main.py and following the link, the following window in your preferred browser opens:
![](https://github.com/danareu/scenario_dashboard/assets/122786331/f6404cad-62e5-4af5-bdb0-c9c4bd8269ae)

2. Add a scenario name in the **"Scenario"** field <br />
3. Add the folder path that points towards your solution file by clicking on **"Browse"**. The dashboard accepts .txt or .sol files that have the following data structure:
![txtfile](https://github.com/danareu/scenario_dashboard/assets/122786331/3c5ae3a5-da30-494a-b2ea-82b95ab7c964)
4. Finally, choose your prefered decision variable from the drop down **"Result:"** and click the button **"Save"**.<br />
5. Optional: If you want to compare scenarios, click **"Add"**. A new field opens where the information for the second scenario should be provided. There is no limit on the number of scenarios. However, for visulization purposes, it is recommended to use max. 3 scenarios for comparison.
   
## Screenshots
**Installed Capacities for the Power Sector [GW]**
![instcapa](https://github.com/danareu/scenario_dashboard/assets/122786331/49c78cbb-8c27-4f6d-a2b0-5fe4c6af67b4) | ![instcapac_country](https://github.com/danareu/scenario_dashboard/assets/122786331/3693e282-0d5f-4138-8565-2da6a0853de5)

**Total Production Power Sector [TWh]**
![totalprod_country](https://github.com/danareu/scenario_dashboard/assets/122786331/0b3f9916-682c-4b5c-8988-ffe1e7ff2b75) | ![totalprod](https://github.com/danareu/scenario_dashboard/assets/122786331/2050432f-efe5-4884-bf6f-204a2b716597)

**Export Power 2050 [TWh]**
![export](https://github.com/danareu/scenario_dashboard/assets/122786331/4c2e43fd-9e78-4fec-ad6d-6ae9bcad102f)

**Transmission & Generation Expansion in 2050 [GW]**
Installed Capacities Power Sector & Installed Transmission Capacities for Power
![map](https://github.com/danareu/scenario_dashboard/assets/122786331/8cb8b661-3b8c-4fb9-b28d-b8452b53de62)

**Comparing different scenarios**
![diff](https://github.com/danareu/scenario_dashboard/assets/122786331/44f4e48e-0355-46f3-88fa-a4dfa8db4b87)

