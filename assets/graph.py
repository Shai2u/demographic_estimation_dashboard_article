import plotly.express as px

class graph:

    status_graph_color = {''}
    status = {''}
    # Generate count status graph
    @staticmethod
    def get_status(bldg_status, width_input = 600, height_input = 250):
        fig = px.bar(bldg_status, x = 'status', y = "count",width=width_input, height = height_input, color = 'status', color_discrete_map = graph.status_graph_color, template='plotly_white', category_orders={'status' : graph.status})
        fig.update_layout(margin = {"r" : 0, "t" : 0, "l" : 0, "b" : 0, "pad" : 0},
        showlegend = False,

        )
        fig.update_yaxes(automargin = True)
        fig.update_yaxes(range = [0, 70])
            # Add images
        fig.add_layout_image(
            dict(
                source = "https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/assets/graphics/Status_Graph.jpg",
                xref = "paper", yref = "paper",
                x = 0, y = 0,
                sizex = 1, sizey = 1,
                xanchor = "left", yanchor = "bottom",
                layer = "below"))
        fig.update_yaxes(showticklabels = False, visible = False)
        fig.update_xaxes(showticklabels = False, visible = False)
        fig.update_traces(marker = dict(line_color = "black"))
    @staticmethod
    def dot_matrix(list_, date_, maatrix_df, width_ = 580, height_ = 450):
        '''
        Generate dot matrix style graph
        '''
        maatrix_df['Who'] = list_
        maatrix_df['squre_'] = 'square'
        fig = px.scatter(maatrix_df, x = "x", y = "y", color = "Who",
                        title= f'Staying vs Leaving Snapshot {date_}',
                        labels= {"Who" : "Legend"}, # customize axis label
                        template= 'simple_white' , color_discrete_map={
                            "Staying": "firebrick",
                            "New Comers": "royalblue",
                            "Future Units": "hsv(0,0%,95%)"})
        fig.update_layout(width = width_,height=height_, margin = dict(l=0, r=0, t=30, b=0) , legend = dict(yanchor="top", y=0.95, xanchor="left", x = 0.01, font = dict(size = 15)))
        fig.update_yaxes(showticklabels = False, visible = False)
        fig.update_xaxes(showticklabels = False, visible = False)
        fig.update_traces(marker = dict(size = 5.5))

        return fig
