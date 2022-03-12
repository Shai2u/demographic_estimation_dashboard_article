# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output
from dash_extensions.javascript import  assign

import dash_leaflet.express as dlx
import plotly.express as px
import dash_leaflet as dl
import pandas as pd
import numpy as np
import json
import geopandas as gpd

#Statistical Stats
statisticalStatsGdf = gpd.read_file('https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/statistical_tract_4326.geojson')
statisticalStatsJson = json.loads(statisticalStatsGdf.to_json())
simulatedBldgsGdf = gpd.read_file('https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/buildings_for_dashboard_4326.geojson')
simulatedBldgsJson = json.loads(simulatedBldgsGdf.to_json())
simulatedBldgsGdf['start_date'] = pd.to_datetime(simulatedBldgsGdf['start_date'])
simulatedBldgsGdf['end_date'] = pd.to_datetime(simulatedBldgsGdf['end_date'])



attribution = '© OpenStreetMap contributors, © CARTO'
cartoUrl = 'http://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'

line_style = dict(weight=2, opacity=1, color='blue', fillOpacity=0,dashArray="10 10")

classes = ['Building before', 'Construction', 'Building after']
colorscale = ['#FFEDA0', '#FEB24C', '#FC4E2A']
style = dict(weight=2, opacity=1, color='white', fillOpacity=0.7)
#colorbar = dlx.categorical_colorbar(categories=classes, colorscale=colorscale, width=300, height=30, position="bottomleft")

style_handle = assign("""function(feature, context){
    const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value the determines the color
    for (let i = 0; i < classes.length; ++i) {
        if (value == classes[i]) {
            style.fillColor = colorscale[i];  // set the fill color according to the class
        }
    }
    return style;
}""")

mapObj = dl.Map([dl.TileLayer(url=cartoUrl, maxZoom=20, attribution=attribution),dl.GeoJSON(data=statisticalStatsJson, options={'style':line_style}),dl.GeoJSON(data = simulatedBldgsJson,options = {'style':style_handle}, id='simulatedBldgs',hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp="status"))],center=[32.0272,34.7444], zoom=16, style={'width': '100%', 'height': '900px'})

dashboard_page =  html.Div([
  html.Div([
    html.Div([
              #To Do Add static legend, that won't chnaged based on years and statistical stats
              html.Div(['Hello World',mapObj
              
              ])
            ],style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            html.Table([
                html.Tr([html.Td(['Hello World'],id='selectedDate',style={'direction':'rtl','width':'10%'}),
                    html.Td([
                                    dcc.Slider(id='years-slider',
             min=2015,
             max=2030,
             value=2022,
             marks={str(year):str(year) for year in np.arange(2015,2030,1)},
                                                    step=0.5
                                                    )
                    ],style={'direction':'rtl','width':'90%'})
                    
                ])
            ],style={'direction':'rtl','width':'100%'})

                                                    ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
  ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'})
        #dcc.Store(id='eng_heb_data')
])
app = Dash(__name__,prevent_initial_callbacks=True)
app.layout = html.Div([

    dashboard_page
])

@app.callback(
    Output('selectedDate', 'children'),
    Output('simulatedBldgs', 'data'),
    Input('years-slider', 'value')
)
def update_output_div(input_value):
    #simulatedBldgsGdf
    date_return =f' Q3 {int(input_value)}'
    d = pd.to_datetime(f'{int(input_value)}-07-01')
    if input_value % 1 == 0:
        d = pd.to_datetime(f'{int(input_value)}-01-01')
        date_return = f'Q1 {int(input_value)}'
    
    bldgs  = simulatedBldgsGdf[(simulatedBldgsGdf['start_date']< d ) & (simulatedBldgsGdf['end_date']> d )].copy().reset_index(drop=True)
    bldgs['start_date'] = bldgs['start_date'].astype(str)
    bldgs['end_date'] = bldgs['end_date'].astype(str)
    bldgsJson = json.loads(bldgs.to_json())
    return date_return,bldgsJson


if __name__ == '__main__':
    app.run_server(debug=True)