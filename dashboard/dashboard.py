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

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)