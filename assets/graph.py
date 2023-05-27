import plotly.express as px

class graph:

    status_graph_color = {''}
    status = {''}
    # Generate count status graph
    @staticmethod
    def get_status(bldg_status):
        fig = px.bar(bldg_status, x='status', y="count",width=600, height=250, color='status',color_discrete_map = graph.status_graph_color, template='plotly_white',category_orders={'status' : graph.status})
        fig.update_layout(margin={"r" : 0,"t" : 0,"l" : 0,"b" : 0,"pad" : 0},
        showlegend = False,

        )
        fig.update_yaxes(automargin=True)
        fig.update_yaxes(range=[0, 70])
            # Add images
        fig.add_layout_image(
            dict(
                source="https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/assets/graphics/Status_Graph.jpg",
                xref="paper", yref="paper",
                x=0, y=0,
                sizex=1, sizey=1,
                xanchor="left", yanchor="bottom",
                layer="below"))
        fig.update_yaxes(showticklabels=False,visible=False)
        fig.update_xaxes(showticklabels=False,visible=False)
        fig.update_traces(
            #marker=dict(line_color="grey", pattern_fillmode="replace") #excellent!!
            marker=dict(line_color="black")
        )

                
        return fig
