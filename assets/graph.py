import plotly.express as px
import numpy as np
import pandas as pd

class graph:
    
    # Define const for graph object
    status_graph_color = {''}
    status = {''}
    total_pop = 0
    matrix_rows_cols = 0
    agents_stat_summary_by_year = pd.DataFrame()
    
    
    # Generate count status graph
    @staticmethod
    def get_status(bldg_status, width_input = 600, height_input = 250):
        '''
        Generate building status graph
        '''
        fig = px.bar(bldg_status, x = 'status', y = "count",width=width_input, height = height_input, color = 'status', color_discrete_map = graph.status_graph_color, template = 'plotly_white', category_orders = {'status' : graph.status})
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
        return fig
    

    @staticmethod
    def prepare_dot_matrix(q_date):
        '''
        Prepare data for dot matrix figure
        '''
        # Number of Columns choose:
        total_cels = (graph.matrix_rows_cols-1) * graph.matrix_rows_cols
        matrix_plot_df = pd.DataFrame({'AgentID':range(0, total_cels)})

        # Set the columns to display the column number
        matrix_plot_df['x'] = list(range(1, graph.matrix_rows_cols)) * graph.matrix_rows_cols
        
        # Prepare the y column (row number)
        y = [[i] * graph.matrix_rows_cols for i in range(1, graph.matrix_rows_cols + 1)]
        temp = []
        for i in range(0,graph.matrix_rows_cols - 1):
            temp += y[i]
        y = temp
        matrix_plot_df['y'] = y
        agents_stat_short = graph.agents_stat_summary_by_year[['year', 'New Comers', 'stay']].copy().fillna(0)
        agents_stat_short['emptyPalces'] =agents_stat_short.apply(lambda p : total_cels - (p['stay'] + p['New Comers']), axis=1)
        stay_count = int(agents_stat_short.loc[agents_stat_short['year'] == q_date,'stay'].values[0])
        new_comers = int(agents_stat_short.loc[agents_stat_short['year'] == q_date,'New Comers'].values[0])
        empty_space = int(agents_stat_short.loc[agents_stat_short['year'] == q_date,'emptyPalces'].values[0])
        stack_list_status = ['Staying'] * stay_count
        stack_list_status = stack_list_status + ['New Comers'] * new_comers
        stack_list_status = stack_list_status + ['Future Units'] * empty_space

        # Add stack list to dataframe
        matrix_plot_df['Who'] = stack_list_status
        
        # type of style for figure
        matrix_plot_df['squre_'] = 'square'
        return matrix_plot_df

    @staticmethod
    def dot_matrix_figure(date_, maatrix_df, width_input, height_input):
        '''
        Generate dot matrix style graph
        '''
        fig = px.scatter(maatrix_df, x = "x", y = "y", color = "Who",
                        title= f'Staying vs Leaving Snapshot {date_}',
                        labels= {"Who" : "Legend"}, # customize axis label
                        template= 'simple_white' , color_discrete_map={
                            "Staying": "firebrick",
                            "New Comers": "royalblue",
                            "Future Units": "hsv(0,0%,95%)"})
        fig.update_layout(width = width_input,height=height_input, margin = dict(l=0, r=0, t=30, b=0) , legend = dict(yanchor="top", y=0.95, xanchor="left", x = 0.01, font = dict(size = 15)))
        fig.update_yaxes(showticklabels = False, visible = False)
        fig.update_xaxes(showticklabels = False, visible = False)
        fig.update_traces(marker = dict(size = 5.5))

        return fig

    @staticmethod
    def dot_matrix(q_date, width_input = 580, height_input = 450):
        '''
        Prepare data and generates dot matrix graphs
        '''
        dot_matrix_df = graph.prepare_dot_matrix(q_date)
        return graph.dot_matrix_figure(q_date, dot_matrix_df, width_input = 580, height_input = 450)

