"""
File: population_simulation.py
Author: Shai Sussman
Date: 26 May 2023
Description: This script initates the dashboard
"""

import requests
from dash import Dash, html, dcc, Input, Output
from dash_extensions.javascript import  assign
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_leaflet.express as dlx
import plotly.express as px
import plotly.graph_objects as go
import dash_leaflet as dl
import pandas as pd
import numpy as np
import json
import geopandas as gpd
import datetime
import requests
from dash_extensions.javascript import Namespace
ns = Namespace("someNamespace", "someSubNamespace")
from assets.graph import graph
import os

# Get the directory containing the current script
script_directory = os.path.dirname(os.path.realpath(__file__))

# Set the working directory to the script directory
os.chdir(script_directory)

# Globals and CONSTANT
contextual_width_global = 1200
contextual_height_global = 275
map_height = '600px'
lower_fig_height = 450

PATH_TO_POUP = 'assets/popup.js'

# Load settings file:
response = requests.get('https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/assets/settings.json')
# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Load the JSON data from the response content
    settings = json.loads(response.content)
else:
    print(f"Error: {response.status_code}")
    
graph.status = settings['status']
graph.status_graph_color = settings['status_graph_color']
graph.contextual_width_global = contextual_width_global
graph.contextual_height_global = contextual_height_global
income_dict = settings['income_dict']

# Map Layers
# Statistical Stats
stat_json = json.loads(gpd.read_file('https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/statistical_tract_4326.geojson').to_json())
# Buildings in the simulation
sim_bldgs_gdf = gpd.read_file('https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/buildings_for_dashboard_4326.geojson')
sim_blgds_json = json.loads(sim_bldgs_gdf.to_json())

# Convert filed to datetime
sim_bldgs_gdf['start_date'] = pd.to_datetime(sim_bldgs_gdf['start_date'])
sim_bldgs_gdf['end_date'] = pd.to_datetime(sim_bldgs_gdf['end_date'])


# Agents track Data
agents_track_status = pd.read_csv('https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/agents_track_status.csv')

agents_stat_summary_by_year = pd.read_csv('https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/yearly_stats_for_dashboard.csv')

graph.total_pop = int(np.round(agents_stat_summary_by_year.loc[agents_stat_summary_by_year.index[-1], 'total_pop'], 0))
graph.matrix_rows_cols = int(np.sqrt(graph.total_pop)) + 1
graph.agents_stat_summary_by_year = agents_stat_summary_by_year

graph.year_ranges = agents_stat_summary_by_year['year']

colorDict = settings['colorDict']


attribution = '© OpenStreetMap contributors, © CARTO'
cartoUrl = 'http://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'

# Renters owners graph
renters_owners_fig = graph.renters_owners('2015 Q1', '2015 Q1', graph.contextual_width_global, graph.contextual_height_global)


q_date_for_dot_matrix = '2015 Q1'

dotMAtrixFig = graph.dot_matrix(q_date_for_dot_matrix)

selected_date = pd.to_datetime('2015-01-01')

blgds_for_selected_dates = sim_bldgs_gdf[(sim_bldgs_gdf['start_date']< selected_date ) & (sim_bldgs_gdf['end_date']> selected_date )].copy().reset_index(drop=True)

# Construction

bldgs_constr = blgds_for_selected_dates[blgds_for_selected_dates['status']=='Construction'].reset_index()

construction_typo_v = bldgs_constr['project_ty'].value_counts().to_frame().reset_index()
construction_typo_v.rename(columns={'index':'project_ty','project_ty':'count'},inplace=True)

selected_date_180d_before = selected_date - datetime.timedelta(days=180) # Why go back 180 days??? Need comment
bldgs2 = sim_bldgs_gdf[(sim_bldgs_gdf['start_date']< selected_date_180d_before ) & (sim_bldgs_gdf['end_date']> selected_date_180d_before )].copy().reset_index(drop=True)

bldgs_constr = bldgs2[bldgs2['status']=='Construction'].reset_index()

construction_typo_d = bldgs_constr['project_ty'].value_counts().to_frame().reset_index()
construction_typo_d.rename(columns={'index':'project_ty','project_ty':'count'},inplace=True)
construction_typo_graph = graph.current_construction(construction_typo_v, construction_typo_d)

# Sunburst

year_makrs = [year for year in np.arange(2015,2031,0.5)]
years_with_q2_makrs = []
for year in year_makrs:
    constructed_date = pd.to_datetime(f'{int(year)}-07-01')
    if year % 1 == 0:
        constructed_date = pd.to_datetime(f'{int(year)}-01-01')
    years_with_q2_makrs.append(constructed_date)
    
selected_bldgs_copy = blgds_for_selected_dates.copy()
agents_synced_buildings_to_date = pd.merge(agents_track_status,selected_bldgs_copy[['project_nu','status','start_date']],left_on=['ProjNumber','bld_status'], right_on=['project_nu','status'])
agents_synced_buildings_to_date_stay_new = agents_synced_buildings_to_date[agents_synced_buildings_to_date['status_x']!='Leave'].drop_duplicates().reset_index(drop=True)

age_grown1 = selected_date.year-years_with_q2_makrs[0].year
agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='stay','age'] = agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='stay','age'] + age_grown1
agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='New Comers','age'] = agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='New Comers'].apply(lambda p: p['age'] + (selected_date.year - p['start_date'].year),axis=1)

agents_synced_buildings_to_date_stay_new['age_group'] = pd.cut(agents_synced_buildings_to_date_stay_new['age'], [0,44,64,84,130],right=True, labels=["18-44", "45-64", "65-84", "85+"],ordered=True)
agents_stay_age_income =agents_synced_buildings_to_date_stay_new[['status_x','age_group','income_cat']].reset_index(drop=True).rename(columns={'status_x':'Stay or leave','age_group':'Age group','income_cat':'Income category'})
population_sunburst_graph_init = graph.demographic_sunburst(2019,agents_stay_age_income,colorDict)

# Bubble Figure

selected_bldgs_copy = blgds_for_selected_dates.copy()

agents_synced_buildings_to_date = pd.merge(agents_track_status,selected_bldgs_copy[['project_nu','status','start_date']],left_on=['ProjNumber','bld_status'], right_on=['project_nu','status'])
agents_synced_buildings_to_date_stay_new = agents_synced_buildings_to_date[agents_synced_buildings_to_date['status_x']!='Leave'].drop_duplicates().reset_index(drop=True)

#age the agents
age_grown1 = selected_date.year-years_with_q2_makrs[0].year
agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='stay','age'] = agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='stay','age'] + age_grown1
agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='New Comers','age'] = agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='New Comers'].apply(lambda p: p['age'] + (selected_date.year - p['start_date'].year),axis=1)

#set categories to agents ages
agents_synced_buildings_to_date_stay_new['age_group'] = pd.cut(agents_synced_buildings_to_date_stay_new['age'], [0,44,64,84,130],right=True, labels=["18-44", "45-64", "65-84", "85+"],ordered=True)
agents_stay_age_income =agents_synced_buildings_to_date_stay_new[['status_x','age_group','income_cat']].reset_index(drop=True).rename(columns={'status_x':'Stay or leave','age_group':'Age group','income_cat':'Income category'})
agents_stay_age_income['units'] = 1
agents_stay_age_income_count = agents_stay_age_income.groupby(['Stay or leave','Age group','Income category']).agg({'units':'count'}).reset_index()
new_comers_age_income_count = agents_stay_age_income_count[agents_stay_age_income_count['Stay or leave']=='New Comers'].reset_index(drop=True)
stay_age_income_count = agents_stay_age_income_count[agents_stay_age_income_count['Stay or leave']=='stay'].reset_index(drop=True)
total = new_comers_age_income_count['units'].sum()+ stay_age_income_count['units'].sum()
new_comers_age_income_count['ratio'] = new_comers_age_income_count['units']/1100
stay_age_income_count['ratio'] = stay_age_income_count['units']/1100

selected_bldgs_copy = blgds_for_selected_dates.copy()

agents_synced_buildings_ref_date = pd.merge(agents_track_status,selected_bldgs_copy[['project_nu','status','start_date']],left_on=['ProjNumber','bld_status'], right_on=['project_nu','status'])
agents_synced_buildings_ref_date_stay_new = agents_synced_buildings_ref_date[agents_synced_buildings_ref_date['status_x']!='Leave'].drop_duplicates().reset_index(drop=True)

#age the agents
age_grown1 = selected_date.year-years_with_q2_makrs[0].year
agents_synced_buildings_ref_date_stay_new.loc[agents_synced_buildings_ref_date_stay_new['status_x']=='stay','age'] = agents_synced_buildings_ref_date_stay_new.loc[agents_synced_buildings_ref_date_stay_new['status_x']=='stay','age'] + age_grown1
agents_synced_buildings_ref_date_stay_new.loc[agents_synced_buildings_ref_date_stay_new['status_x']=='New Comers','age'] = agents_synced_buildings_ref_date_stay_new.loc[agents_synced_buildings_ref_date_stay_new['status_x']=='New Comers'].apply(lambda p: p['age'] + (selected_date.year - p['start_date'].year),axis=1)

#set categories to agents ages
agents_synced_buildings_ref_date_stay_new['age_group'] = pd.cut(agents_synced_buildings_ref_date_stay_new['age'], [0,44,64,84,130],right=True, labels=["18-44", "45-64", "65-84", "85+"],ordered=True)
agents_stay_age_income_ref =agents_synced_buildings_ref_date_stay_new[['status_x','age_group','income_cat']].reset_index(drop=True).rename(columns={'status_x':'Stay or leave','age_group':'Age group','income_cat':'Income category'})
agents_stay_age_income_ref['units'] = 1
agents_stay_age_income_ref = agents_stay_age_income_ref.groupby(['Stay or leave','Age group','Income category']).agg({'units':'count'}).reset_index()
new_comers_age_income_count_ref = agents_stay_age_income_ref[agents_stay_age_income_ref['Stay or leave']=='New Comers'].reset_index(drop=True)
stay_age_income_count_ref = agents_stay_age_income_ref[agents_stay_age_income_ref['Stay or leave']=='stay'].reset_index(drop=True)
total_ref = new_comers_age_income_count_ref['units'].sum()+ stay_age_income_count_ref['units'].sum()
new_comers_age_income_count_ref['ratio'] = new_comers_age_income_count_ref['units']/1100
stay_age_income_count_ref['ratio'] = stay_age_income_count_ref['units']/1100
bubble_age_income = graph.bubble_age_income_stay_time(stay_age_income_count_ref,new_comers_age_income_count_ref,stay_age_income_count,new_comers_age_income_count,'2015 Q1','2015 Q1')

# BUILD STATUS COUNT GRAPH

# Select building that their status starts before the selected date and ends after the selected date (overlapping status during that date)
selected_bldgs_copy = blgds_for_selected_dates.copy()

# For Building status count chart
bldg_status = selected_bldgs_copy['status'].value_counts().to_frame().reset_index()
# bldg_status.rename(columns={'status':'count'},inplace=True)
# bldg_status.rename(columns={'index':'status'},inplace=True)

# In case only one or two status exist, populate the other status with 0
if len(bldg_status)<3:
  if len(bldg_status[bldg_status['status'].isin(['Building before'])])==0:
    bldg_status = pd.concat([bldg_status,pd.DataFrame({'status':['Building before'],'count':[0]})])
  if len(bldg_status[bldg_status['status'].isin(['Construction'])])==0:
    bldg_status = pd.concat([bldg_status,pd.DataFrame({'status':['Construction'],'count':[0]})])
  if len(bldg_status[bldg_status['status'].isin(['Building after'])])==0:
    bldg_status = pd.concat([bldg_status,pd.DataFrame({'status':['Building after'],'count':[0]})])
bldg_status.reset_index(drop = True, inplace=True)

# Build status count graph
bldg_status_count = graph.get_status(bldg_status)

# TODO consider switching to Maplibre 100%

# Build dash leaflet 2D map object
classes = settings['status']
colorscale = settings['map_2d_color']
style = dict(weight=2, opacity=1, color='grey', fillOpacity=0.7)

# Build a color legend for the map object
colorbar = dlx.categorical_colorbar(categories=classes, colorscale=colorscale, width=300, height=30, position="bottomright")

# Line style for statistical areas
line_style = dict(weight=2, opacity=1, color='blue', fillOpacity=0,dashArray="10 10")

style_handle = assign("""
function(feature, context){
    const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value the determines the color
    for (let i = 0; i < classes.length; ++i) {
        if (value == classes[i]) {
            style.fillColor = colorscale[i];  // set the fill color according to the class
        }
    }
    return style;
}""")


mapObj = dl.Map([dl.TileLayer(url=cartoUrl, maxZoom=20, attribution=attribution),dl.GeoJSON(data=stat_json, options={'style':line_style},),
                 dl.GeoJSON(data = sim_blgds_json,options = {'style':style_handle, 'onEachFeature':ns("bindPopup")}, id='simulatedBldgs',hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp="status")),colorbar],center=[32.0272,34.7444], zoom=16, style={'width': '100%', 'height': map_height})



dashboard_page =  html.Div([
  html.Div([
    # Div Row 1 and 2 (Map, Time series, status graphs)
    html.Div([
      html.Div([
        # 2D/3D Map card (column 1/ row 1 and row 2)
        dbc.Card(
          children=[  
            dbc.CardHeader(["Map of the study area ",html.Span(id='3d_map_date')]),
            dbc.CardBody([
              html.Div(mapObj,id='map_2d',style={'display':'block','textAlign':'center'}),
              html.Div([],id='map_3d')
            ])
          ]
        )],style={'width': '34%', 'display': 'inline-block','textAlign':'center'}),
      # Div (Column 2 and 3/row 1 and 2)
      html.Div([
        # Time series card (column 2 and column 3/ row 1)
        dbc.Card(
          children=[
            dbc.CardHeader("Time series graph with context"),
            dbc.CardBody(
              html.Div([
                dcc.Graph(id='time_seiries_graph',figure=renters_owners_fig,style={'textAlign':'center'})
              ])
            )
          ]
        ),
        html.Div([
          # Current construction typologies (column 2 row 2)
          dbc.Card(
            children=[
              dbc.CardHeader("Current construction typologies"),
              dbc.CardBody([
                dcc.Graph(id='typo_count', figure=construction_typo_graph,style={'textAlign':'center'}),
              ])
            ]
          )
        ],style={'width': '50%', 'display': 'inline-block','textAlign':'center'}),
        html.Div([
          # Building status count (column 3 row 2)
          dbc.Card(
            children=[
              dbc.CardHeader("Building status count"),
              dbc.CardBody([dcc.Graph(id='status_count',figure=bldg_status_count,style={'textAlign':'center'})])
            ]
          )
        ],style={'width': '50%', 'display': 'inline-block'})
      ], style={'width': '66%', 'float': 'right', 'display': 'inline-block','textAlign':'center'})
    ],style={'padding':'1px'}), # seperator between uppwer and lower!
    #-------------------------------- Lower Div --------------------------------------
    # Div Row 3 (2 variables, suburst, dot mbatrix)
    html.Div([
      #---------------------- 2 Variables graph -------------------------------
      html.Div([
        html.Div([
          # 2 Variable graph card (Row 3, Column 1)
          dbc.Card(
            children=[
              dbc.CardHeader("2 Variables bubble graph"),
              dbc.CardBody( dcc.Graph(id='bubble_graph',figure=bubble_age_income,style={'width': '100%','marginLeft':'auto','marginRight':'auto','textAlign':'center'}))
            ]
          )
        ])
      ],style={'width': '34%', 'display': 'inline-block','marginLeft':'auto','marginRight':'auto','textAlign':'center'}),
      html.Div([
      # sunburst graph card (Row 3, Column 2)
        dbc.Card(
          children=[
            dbc.CardHeader("Population sunburst"),
            dbc.CardBody(dcc.Graph(id='population_sunburst_fig',figure= population_sunburst_graph_init,style={'width': '100%','marginLeft':'auto','marginRight':'auto','textAlign':'center'}))
          ]
        )
      ],style={'width': '33%', 'display': 'inline-block','marginLeft':'auto','marginRight':'auto','textAlign':'center'}),
      html.Div([
        # Dot matrix graph card (Row 3, Column 3)
        dbc.Card(
          children=[
            dbc.CardHeader("Population dot matrix"),
            dbc.CardBody(dcc.Graph(id='dot_matrix_fig',figure=dotMAtrixFig,style={'width': '100%','marginLeft':'auto','marginRight':'auto','textAlign':'center'}))
          ]
        )
      ],style={'width': '33%', 'display': 'inline-block','marginLeft':'auto','marginRight':'auto','textAlign':'center'})
    ],style={'padding':'1px'}),
    #---------------------- Controllers -------------------------------
    # Div Row 4 (Controller)
    html.Div([dbc.Card(
      children=[
        dbc.CardHeader("Controller"),
        dbc.CardBody([
          html.Div(
            daq.BooleanSwitch(on=False, label="3D", labelPosition="top",id='3d_map_switch'),
            style={'width':'10%', 'display': 'inline-block'}
          ),
          html.Div([dcc.Dropdown( id='select_context',options=[
              {'label': 'Owners Renters Count', 'value': 'Owners Renters Count'},
              {'label': 'Chnage Apartment Size', 'value': 'Chnage Apartment Size'},
              {'label': 'Change in Age Distribution', 'value': 'Change in Age Distribution'},
              {'label': 'Change in Income Distribution', 'value': 'Change in Income Distribution'},
              {'label': 'Change in Income Category', 'value': 'Change in Income Category'},
            ], value='Owners Renters Count')] ,style={'width':'25%', 'display': 'inline-block'}),
          html.Div([dcc.RangeSlider(id='years-slider',
             min=2015,
             max=2030,
             value=[2015,2015],
             marks={str(year):str(year) for year in np.arange(2015,2030,1)},
                                                    step=0.5
                                                    )],style={'width':'65%', 'display': 'inline-block'})
        ]),
      ])],style={'textAlign':'center'})
  ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '5px 5px'})
])
external_stylesheets = [dbc.themes.BOOTSTRAP, "https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/assets/style.css"]
app = Dash(__name__,suppress_callback_exceptions=True,prevent_initial_callbacks=True, external_stylesheets=external_stylesheets)


app.title = "Population Dashboard"

#run_with_ngrok(app)

app.layout = html.Div([

    dashboard_page
])

@app.callback(
    Output('simulatedBldgs', 'data'),
    Output('status_count','figure'),
    Output('dot_matrix_fig','figure'),
    Output('time_seiries_graph','figure'),
    Output('typo_count','figure'),
    Output('population_sunburst_fig','figure'),
    Output('bubble_graph','figure'),
    Output('map_2d','style'),
    Output('map_3d','children'),
    Output('3d_map_date','children'),
    Input('years-slider', 'value'),
    Input('select_context','value'),
    Input('3d_map_switch','on')
)
def update_output_div(input_value, input_select_context, d3_map_switch):
    #sim_bldgs_gdf
    ref_year = int(input_value[0]) # Reference year to compare
    selected_year = int(input_value[1]) # selected year
    date_return = f'Q3 {selected_year}' # Q before Date
    q_date_for_dot_matrix = f'{selected_year} Q3' # Q After date
    selected_date = pd.to_datetime(f'{selected_year}-07-01') # selected date by user by default middle of year (Q3)
    map_libre_date = int(f'{selected_year}0701') # date to be use when selecting html file

    # Set date variables to Q1 instead of Q3
    if input_value[1] % 1 == 0:
        selected_date = pd.to_datetime(f'{selected_year}-01-01')
        date_return = f'Q1 {selected_year}'
        q_date_for_dot_matrix = f'{selected_year} Q1'
        map_libre_date = int(f'{selected_year}0101')
        
    #reference date
    reference_date = pd.to_datetime(f'{ref_year}-07-01')
    ref_q_date = f'Q3 {ref_year}'
    ref_q_date_e = f'{ref_year} Q3'
    if input_value[0] % 1 == 0:
          reference_date = pd.to_datetime(f'{ref_year}-01-01')
          ref_q_date = f'Q1 {ref_year}'
          ref_q_date_e = f'{ref_year} Q1'

    
    blgds_for_selected_dates  = sim_bldgs_gdf[(sim_bldgs_gdf['start_date']< selected_date ) & (sim_bldgs_gdf['end_date']> selected_date )].copy().reset_index(drop=True)
    blgds_for_selected_dates_copy = blgds_for_selected_dates.copy()

    # For JSON object
    bldgsUsedForJson = blgds_for_selected_dates.copy()
    bldgsUsedForJson['start_date'] = bldgsUsedForJson['start_date'].astype(str)
    bldgsUsedForJson['end_date'] = bldgsUsedForJson['end_date'].astype(str)

    if d3_map_switch:
      bldgsJson=None
      #display 2D/3D Map
      map_2d_display = {'display':'none'}
      rand_id = random_int = np.random.randint(0,10) #to refresh 3d
      map3d = html.Iframe(id=f'ifame-cell-{rand_id}', height=map_height, width="100%",
                                                  src=f"https://shai2u.github.io/demographic_estimation_dashboard_article/BatYam_maplibre/{map_libre_date}.html")

    else:
      bldgsJson = json.loads(bldgsUsedForJson.to_json())
      #display 2D/3D Map
      map_2d_display = {'display':'block'}
      map3d = ''

    #construction
    bldg_status = blgds_for_selected_dates['status'].value_counts().to_frame().reset_index()
    
    # Fill valaues if missing
    if len(bldg_status)<3:
      if len(bldg_status[bldg_status['status'].isin(['Building before'])])==0:
        bldg_status = pd.concat([bldg_status,pd.DataFrame({'status':['Building before'],'count':[0]})])
      if len(bldg_status[bldg_status['status'].isin(['Construction'])])==0:
        bldg_status = pd.concat([bldg_status,pd.DataFrame({'status':['Construction'],'count':[0]})])
      if len(bldg_status[bldg_status['status'].isin(['Building after'])])==0:
        bldg_status = pd.concat([bldg_status,pd.DataFrame({'status':['Building after'],'count':[0]})])
    bldg_status.reset_index(drop = True, inplace = True) 
    bldg_status_count = graph.get_status(bldg_status)
    
    selected_date_180d_before = selected_date - datetime.timedelta(days=180) # Why go back 180 days?? Need clarification here!
    bldgs_constr = blgds_for_selected_dates[blgds_for_selected_dates['status']=='Construction'].reset_index()

    construction_typo_v = bldgs_constr['project_ty'].value_counts().to_frame().reset_index()
    construction_typo_v.rename(columns={'index':'project_ty','project_ty':'count'},inplace=True)

    blgds_for_selected_dates_180_d_before = sim_bldgs_gdf[(sim_bldgs_gdf['start_date']< selected_date_180d_before ) & (sim_bldgs_gdf['end_date']> selected_date_180d_before )].copy().reset_index(drop=True)
    bldgs_constr = blgds_for_selected_dates_180_d_before[blgds_for_selected_dates_180_d_before['status']=='Construction'].reset_index()

    construction_typo_d = bldgs_constr['project_ty'].value_counts().to_frame().reset_index()
    construction_typo_d.rename(columns={'index':'project_ty','project_ty':'count'},inplace=True)
    construction_typo_graph = graph.current_construction(construction_typo_v,construction_typo_d)


    # Dot Matrix

    dotMAtrixFig = graph.dot_matrix(q_date_for_dot_matrix)

    #time context
    #renters Owners
    if input_select_context == 'Owners Renters Count':
      context_fig = graph.renters_owners(q_date_for_dot_matrix , ref_q_date_e, graph.contextual_width_global, graph.contextual_height_global)
    elif input_select_context == 'Chnage Apartment Size':
      context_fig = graph.apartment(q_date_for_dot_matrix , ref_q_date_e, graph.contextual_width_global, graph.contextual_height_global)
    elif input_select_context == 'Change in Age Distribution':
      context_fig = graph.change_age_distribution(q_date_for_dot_matrix, ref_q_date_e, graph.contextual_width_global, graph.contextual_height_global)                                                                             
    elif input_select_context == 'Change in Income Distribution':
      context_fig = graph.income_distribution(q_date_for_dot_matrix,ref_q_date_e, graph.contextual_width_global, graph.contextual_height_global)
    elif input_select_context == 'Change in Income Category':
      context_fig = graph.income_category(q_date_for_dot_matrix,ref_q_date_e, graph.contextual_width_global, graph.contextual_height_global)                                                                           
    else:
      context_fig = graph.renters_owners(q_date_for_dot_matrix,ref_q_date_e, graph.contextual_width_global, graph.contextual_height_global)

    #sunburst
    agents_synced_buildings_to_date = pd.merge(agents_track_status,blgds_for_selected_dates_copy[['project_nu','status','start_date']],left_on=['ProjNumber','bld_status'], right_on=['project_nu','status'])
    agents_synced_buildings_to_date_stay_new = agents_synced_buildings_to_date[agents_synced_buildings_to_date['status_x']!='Leave'].drop_duplicates().reset_index(drop=True)

    age_grown1 = selected_date.year-years_with_q2_makrs[0].year
    agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='stay','age'] = agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='stay','age'] + age_grown1
    agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='New Comers','age'] = agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='New Comers'].apply(lambda p: p['age'] + (selected_date.year - p['start_date'].year),axis=1)

    agents_synced_buildings_to_date_stay_new['age_group'] = pd.cut(agents_synced_buildings_to_date_stay_new['age'], [0,44,64,84,130],right=True, labels=["18-44", "45-64", "65-84", "85+"],ordered=True)
    agents_stay_age_income =agents_synced_buildings_to_date_stay_new[['status_x','age_group','income_cat']].reset_index(drop=True).rename(columns={'status_x':'Stay or leave','age_group':'Age group','income_cat':'Income category'})
    population_sunburst_graph = graph.demographic_sunburst(date_return,agents_stay_age_income,colorDict)


    #bubble graphs Selected
    agents_synced_buildings_to_date = pd.merge(agents_track_status,blgds_for_selected_dates_copy[['project_nu','status','start_date']],left_on=['ProjNumber','bld_status'], right_on=['project_nu','status'])
    agents_synced_buildings_to_date_stay_new = agents_synced_buildings_to_date[agents_synced_buildings_to_date['status_x']!='Leave'].drop_duplicates().reset_index(drop=True)

    #age the agents
    age_grown1 = selected_date.year-years_with_q2_makrs[0].year
    agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='stay','age'] = agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='stay','age'] + age_grown1
    agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='New Comers','age'] = agents_synced_buildings_to_date_stay_new.loc[agents_synced_buildings_to_date_stay_new['status_x']=='New Comers'].apply(lambda p: p['age'] + (selected_date.year - p['start_date'].year),axis=1)

    #set categories to agents ages
    agents_synced_buildings_to_date_stay_new['age_group'] = pd.cut(agents_synced_buildings_to_date_stay_new['age'], [0,44,64,84,130],right=True, labels=["18-44", "45-64", "65-84", "85+"],ordered=True)
    agents_stay_age_income =agents_synced_buildings_to_date_stay_new[['status_x','age_group','income_cat']].reset_index(drop=True).rename(columns={'status_x':'Stay or leave','age_group':'Age group','income_cat':'Income category'})
    agents_stay_age_income['units'] = 1
    agents_stay_age_income_count = agents_stay_age_income.groupby(['Stay or leave','Age group','Income category']).agg({'units':'count'}).reset_index()
    new_comers_age_income_count = agents_stay_age_income_count[agents_stay_age_income_count['Stay or leave']=='New Comers'].reset_index(drop=True)
    stay_age_income_count = agents_stay_age_income_count[agents_stay_age_income_count['Stay or leave']=='stay'].reset_index(drop=True)
    #total = new_comers_age_income_count['units'].sum()+ stay_age_income_count['units'].sum()
    new_comers_age_income_count['ratio'] = new_comers_age_income_count['units']/1100
    stay_age_income_count['ratio'] = stay_age_income_count['units']/1100

    #reference selection
    blgds_for_reference_selected_dates  = sim_bldgs_gdf[(sim_bldgs_gdf['start_date']< reference_date ) & (sim_bldgs_gdf['end_date']> reference_date )].copy().reset_index(drop=True)

    agents_synced_buildings_ref_date = pd.merge(agents_track_status, blgds_for_reference_selected_dates[['project_nu','status','start_date']],left_on=['ProjNumber','bld_status'], right_on=['project_nu','status'])
    agents_synced_buildings_ref_date_stay_new = agents_synced_buildings_ref_date[agents_synced_buildings_ref_date['status_x']!='Leave'].drop_duplicates().reset_index(drop=True)

    #age the agents
    age_grown1 = reference_date.year-years_with_q2_makrs[0].year
    agents_synced_buildings_ref_date_stay_new.loc[agents_synced_buildings_ref_date_stay_new['status_x']=='stay','age'] = agents_synced_buildings_ref_date_stay_new.loc[agents_synced_buildings_ref_date_stay_new['status_x']=='stay','age'] + age_grown1
    agents_synced_buildings_ref_date_stay_new.loc[agents_synced_buildings_ref_date_stay_new['status_x']=='New Comers','age'] = agents_synced_buildings_ref_date_stay_new.loc[agents_synced_buildings_ref_date_stay_new['status_x']=='New Comers'].apply(lambda p: p['age'] + (reference_date.year - p['start_date'].year),axis=1)

    #set categories to agents ages
    agents_synced_buildings_ref_date_stay_new['age_group'] = pd.cut(agents_synced_buildings_ref_date_stay_new['age'], [0,44,64,84,130],right=True, labels=["18-44", "45-64", "65-84", "85+"],ordered=True)
    agents_stay_age_income_ref =agents_synced_buildings_ref_date_stay_new[['status_x','age_group','income_cat']].reset_index(drop=True).rename(columns={'status_x':'Stay or leave','age_group':'Age group','income_cat':'Income category'})
    agents_stay_age_income_ref['units'] = 1
    agents_stay_age_income_ref = agents_stay_age_income_ref.groupby(['Stay or leave','Age group','Income category']).agg({'units':'count'}).reset_index()
    new_comers_age_income_count_ref = agents_stay_age_income_ref[agents_stay_age_income_ref['Stay or leave']=='New Comers'].reset_index(drop=True)
    stay_age_income_count_ref = agents_stay_age_income_ref[agents_stay_age_income_ref['Stay or leave']=='stay'].reset_index(drop=True)
    #total_ref = new_comers_age_income_count_ref['units'].sum()+ stay_age_income_count_ref['units'].sum()
    new_comers_age_income_count_ref['ratio'] = new_comers_age_income_count_ref['units']/1100
    stay_age_income_count_ref['ratio'] = stay_age_income_count_ref['units']/1100
    bubble_age_income = graph.bubble_age_income_stay_time(stay_age_income_count_ref,new_comers_age_income_count_ref,stay_age_income_count,new_comers_age_income_count,ref_q_date,date_return)


    return bldgsJson, bldg_status_count, dotMAtrixFig, context_fig, construction_typo_graph, population_sunburst_graph, bubble_age_income, map_2d_display, map3d, q_date_for_dot_matrix


if __name__ == '__main__':
    app.run_server(debug=False)