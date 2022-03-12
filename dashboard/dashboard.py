# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

#Statistical Stats
statisticalStatsGdf = gpd.read_file('https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/statistical_tract_4326.geojson')
statisticalStatsJson = json.loads(statisticalStatsGdf.to_json())
simulatedBldgsGdf = gpd.read_file('https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/buildings_for_dashboard_4326.geojson')
simulatedBldgsJson = json.loads(simulatedBldgsGdf.to_json())
simulatedBldgsGdf['start_date'] = pd.to_datetime(simulatedBldgsGdf['start_date'])
simulatedBldgsGdf['end_date'] = pd.to_datetime(simulatedBldgsGdf['end_date'])


fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

attribution = '© OpenStreetMap contributors, © CARTO'
cartoUrl = 'http://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

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
])

if __name__ == '__main__':
    app.run_server(debug=True)