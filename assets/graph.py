import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

class graph:
    
    # Define const for graph object
    status_graph_color = {''}
    status = {''}
    total_pop = 0
    matrix_rows_cols = 0
    contextual_width_global = 0
    contextual_height_global = 0
    year_ranges = []
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

    @staticmethod
    def renters_owners(q_date, q_date_reference, width_input, height_input):
        """
        Time series graph that compares between renters owners staying and new comers
        """
        rent_own_new_stay_df = graph.agents_stat_summary_by_year[['year', 'New Comers_rent', 'New Comers_own', 'stay_rent', 'stay_own']].copy().fillna(0)
        # Select from start till end date
        end_index = rent_own_new_stay_df[rent_own_new_stay_df['year'] == q_date].index.values[0]
        selected_indexes = range(0,end_index + 1)
        selected_df = rent_own_new_stay_df[rent_own_new_stay_df.index.isin(selected_indexes)]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = selected_df['New Comers_rent'],
            legendgroup = "New Comers",  # this can be any string, not just "group"
            legendgrouptitle_text = "New Comers",
            name = "Renters",
            mode = "lines",
            line=dict(color='royalblue', width=1)
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = selected_df['New Comers_own'],
            legendgroup = "New Comers",  # this can be any string, not just "group"
            legendgrouptitle_text = "New Comers",
            name = "Owners",
            mode = "lines",
            line = dict(color='royalblue', width=3)
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = selected_df['stay_rent'],
            legendgroup = "Staying",  # this can be any string, not just "group"
            legendgrouptitle_text = "Staying",
            name = "Renters",
            mode = "lines",
            line = dict(color='firebrick', width=1)
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = selected_df['stay_own'],
            legendgroup = "Staying",  # this can be any string, not just "group"
            legendgrouptitle_text = "Staying",
            name = "Owners",
            mode = "lines",
            line = dict(color='firebrick', width=5)
        ))

        # Reference line
        fig.add_trace(go.Scatter(x = [q_date_reference, q_date_reference], y=[0,2100],
                        name = q_date_reference,
                        legendgroup = "Reference",
                        legendgrouptitle_text = "Reference",
                        mode = "lines",
                        line = dict(color="LightSeaGreen", width = 2,dash = "dashdot")))
        
        fig.update_layout(title="Staying Leaving and Owenrship", template='plotly_white', yaxis = {'title' : "Absolute Numbers"}, margin={"r" : 0, "t" : 35, "l" : 0, "b" : 35, "pad" : 0},
                            width = width_input, height = height_input, legend=dict(orientation = "h", yanchor = "top", y = 0.99, xanchor = "left", x = 0.01))
        fig.update_layout(hovermode="x unified")
        fig.update_xaxes(range = [0, len(graph.year_ranges)])
        fig.update_yaxes(range = [0, 2100])
        return fig
    
    @staticmethod
    def apartment(q_date , q_date_reference, width_input, height_input):
        """
        Time series graph that compares between apartment size, staying and new comers
        """
        df_less_columns = graph.agents_stat_summary_by_year[['year', 'New Comers_apartment_size_q1', 'New Comers_apartment_size_q2', 'New Comers_apartment_size_q3', 'stay_apartment_size_q1', 'stay_apartment_size_q2', 'stay_apartment_size_q3']].copy()
        
        # fitler till the selected year
        end_index = df_less_columns[df_less_columns['year'] == q_date].index.values[0]
        selected_indexes = range(0, end_index + 1)
        df_for_graph = df_less_columns[df_less_columns.index.isin(selected_indexes)]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['New Comers_apartment_size_q1'],
            legendgroup = "New Comers",  # this can be any string, not just "group"
            legendgrouptitle_text = "New Comers",
            name = "Apartment Size Q1 (25%)",
            mode = "lines",
            line = dict(color = 'royalblue', width = 1)
        ))


        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['New Comers_apartment_size_q2'],
            legendgroup = "New Comers",  # this can be any string, not just "group"
            legendgrouptitle_text = "New Comers",
            name = "Apartment Size Q2 (50%)",
            mode = "lines",
            line = dict(color = 'royalblue', width = 3)
        ))


        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['New Comers_apartment_size_q3'],
            legendgroup = "New Comers",  # this can be any string, not just "group"
            legendgrouptitle_text = "New Comers",
            name = "Apartment Size Q3 (75%)",
            mode = "lines",
            line = dict(color = 'royalblue', width = 4)
            
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['stay_apartment_size_q1'],
            legendgroup = "Staying",  # this can be any string, not just "group"
            legendgrouptitle_text = "Staying",
            name = "Apartment Size Q1 (25%)",
            mode = "lines",
            line = dict(color = 'firebrick', width = 1)
        ))


        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['stay_apartment_size_q2'],
            legendgroup = "Staying",  # this can be any string, not just "group"
            legendgrouptitle_text = "Staying",
            name = "Apartment Size Q2 (50%)",
            mode = "lines",
            line = dict(color = 'firebrick', width = 3)
        ))


        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['stay_apartment_size_q3'],
            legendgroup = "Staying",  # this can be any string, not just "group"
            legendgrouptitle_text = "Staying",
            name = "Apartment Size Q3 (75%)",
            mode = "lines",
            line = dict(color = 'firebrick', width = 4)
            
        ))

        fig.add_trace(go.Scatter(x = [q_date_reference, q_date_reference], y = [50,140],
                    name = q_date_reference,
                    legendgroup = "Reference",
                    legendgrouptitle_text = "Reference",
                    mode = "lines",
                    line = dict(color = "LightSeaGreen", width = 2, dash= "dashdot")))

        # fig.update_layout(title="Apartment Size  (q1-q3) vs Staying or New Comers",template='plotly_white',yaxis = {'title' : "m<sup>2</sup>"})
        
        fig.update_layout(title = "Apartment Size quarter distribution for Staying vs New Comers", template = 'plotly_white', yaxis = {'title' : "m<sup>2</sup>"},margin={"r" : 0,"t" : 35,"l" : 0,"b" : 35,"pad" : 0},
                            width = width_input, height=height_input ,legend = dict(orientation = "h", yanchor = "top", y = 0.99,xanchor = "left", x = 0.01))

        fig.update_layout(hovermode = "x unified")

        #end modification

        fig.update_xaxes(range = [0,len(graph.year_ranges)])
        fig.update_yaxes(range = [50,160])
        return fig
    
    @staticmethod
    def change_age_distribution(q_date, q_date_reference, width_input, height_input):
        """
        Time series graph that examines the change in age distribution between staying and new comers
        """
        df_less_columns = graph.agents_stat_summary_by_year[['year', 'New Comers_age_q1', 'New Comers_age_q2', 'New Comers_age_q3', 'stay_age_q1', 'stay_age_q2', 'stay_age_q3']].copy()
        end_index = df_less_columns[df_less_columns['year'] == q_date].index.values[0]
        selected_indexes = range(0 , end_index + 1)
        df_for_graph = df_less_columns[df_less_columns.index.isin(selected_indexes)]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['New Comers_age_q1'],
            legendgroup = "New Comers",  # this can be any string, not just "group"
            legendgrouptitle_text = "New Comers",
            name = "Average age in q1 (25%)",
            mode = "lines",
            line = dict(color = 'royalblue', width = 1)
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['New Comers_age_q2'],
            legendgroup = "New Comers",  # this can be any string, not just "group"
            legendgrouptitle_text = "New Comers",
            name = "Average age in q2 (50%)",
            mode = "lines",
            line = dict(color = 'royalblue', width = 3)
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['New Comers_age_q3'],
            legendgroup = "New Comers",  # this can be any string, not just "group"
            legendgrouptitle_text = "New Comers",
            name = "Average age in q3 (75%)",
            mode = "lines",
            line = dict(color = 'royalblue', width = 4)
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['stay_age_q1'],
            legendgroup = "Staying",  # this can be any string, not just "group"
            legendgrouptitle_text = "Staying",
            name = "Average age in q1 (25%)",
            mode = "lines",
            line = dict(color = 'firebrick', width = 1)
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['stay_age_q2'],
            legendgroup = "Staying",  # this can be any string, not just "group"
            legendgrouptitle_text = "Staying",
            name = "Average age in q2 (50%)",
            mode = "lines",
            line = dict(color = 'firebrick', width = 3)
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['stay_age_q3'],
            legendgroup = "Staying",  # this can be any string, not just "group"
            legendgrouptitle_text = "Staying",
            name = "Average age in q2 (75%)",
            mode = "lines",
            line = dict(color = 'firebrick', width = 4)  
        ))

        fig.add_trace(go.Scatter(x = [q_date_reference, q_date_reference], y = [20, 100],
                    name = q_date_reference,
                    legendgroup = "Reference",
                    legendgrouptitle_text = "Reference",
                    mode = "lines",
                    line = dict(color = "LightSeaGreen", width = 2, dash = "dashdot")))
        
        fig.update_layout(title = "Age quarter distribution for Staying vs New Comers", template = 'plotly_white', yaxis = {'title' : "Average Age"}, margin={"r" : 0, "t" : 35, "l" : 0, "b" : 35, "pad" : 0},
                            width = width_input, height = height_input, legend = dict(orientation = "h", yanchor = "top",y = 0.99, xanchor = "left", x = 0.01))
        fig.update_layout(hovermode="x unified")

        fig.update_xaxes(range = [0,len(graph.year_ranges)])
        fig.update_yaxes(range = [20,110])

        return fig

    @staticmethod
    def income_distribution(q_date, q_date_reference, width_input, height_input):
        """
        Time series graph that examines the change in income distribution between staying and new comers
        """
        df_less_columns = graph.agents_stat_summary_by_year[['year', 'New Comers_income_q1', 'New Comers_income_q2', 'New Comers_income_q3', 'stay_income_q1', 'stay_income_q2', 'stay_income_q3']].copy()
        end_index = df_less_columns[df_less_columns['year'] == q_date].index.values[0]
        selected_indexes = range(0, end_index+1)
        df_for_graph = df_less_columns[df_less_columns.index.isin(selected_indexes)]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x = graph.year_ranges, 
            y = df_for_graph['New Comers_income_q1'],
            legendgroup = "New Comers",  # this can be any string, not just "group"
            legendgrouptitle_text = "New Comers",
            name = "Income Q1 (25%)",
            mode = "lines",
            line = dict(color = 'royalblue', width = 1)
        ))


        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['New Comers_income_q2'],
            legendgroup = "New Comers",  # this can be any string, not just "group"
            legendgrouptitle_text = "New Comers",
            name = "Income Q2 (50%)",
            mode = "lines",
            line = dict(color = 'royalblue', width = 3)
        ))


        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['New Comers_income_q3'],
            legendgroup = "New Comers",  # this can be any string, not just "group"
            legendgrouptitle_text = "New Comers",
            name = "Income Q3 (75%)",
            mode = "lines",
            line = dict(color = 'royalblue', width = 4)
            
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['stay_income_q1'],
            legendgroup = "Staying",  # this can be any string, not just "group"
            legendgrouptitle_text = "Staying",
            name = "Icome Q1 (25%)",
            mode = "lines",
            line = dict(color = 'firebrick', width = 1)
        ))


        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['stay_income_q2'],
            legendgroup = "Staying",  # this can be any string, not just "group"
            legendgrouptitle_text = "Staying",
            name = "Income Q2 (50%)",
            mode = "lines",
            line = dict(color = 'firebrick', width = 3)
        ))


        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['stay_income_q3'],
            legendgroup = "Staying",  # this can be any string, not just "group"
            legendgrouptitle_text = "Staying",
            name = "Income Q3 (75%)",
            mode = "lines",
            line = dict(color = 'firebrick', width = 4)
            
        ))



        fig.add_trace(go.Scatter(x = [q_date_reference, q_date_reference], y = [0,40000],
                    name = q_date_reference,
                    legendgroup = "Reference",
                    legendgrouptitle_text = "Reference",
                    mode = "lines",
                    line = dict(color = "LightSeaGreen", width = 2, dash = "dashdot")))
        

        fig.update_layout(title = "Income quarter distribution for Staying vs New Comers", template = 'plotly_white', yaxis = {'title' : "Inocme (New Israeli Shekels)"}, margin = {"r" : 0, "t" : 35, "l" : 0, "b" : 35, "pad" : 0},
                            width = width_input, height = height_input, legend = dict(orientation = "h",  yanchor = "top", y = 0.99, xanchor = "left", x = 0.01))
        fig.update_layout(hovermode = "x unified")


        fig.update_xaxes(range = [0, len(graph.year_ranges)])
        fig.update_yaxes(range = [0, 40000])

        #end modification

        return fig
    
    @staticmethod
    def income_category(q_date, q_date_reference, width_input, height_input):
        """
        Time series graph that examines the change in age distribution category between staying and new comers
        """
        df_less_columns = graph.agents_stat_summary_by_year[['year', 'New Comers_income_low_ratio', 'New Comers_income_medium_ratio', 'New Comers_income_high_ratio', 'stay_income_low_ratio', 'stay_income_medium_ratio', 'stay_income_high_ratio']].copy()
        end_index = df_less_columns[df_less_columns['year'] == q_date].index.values[0]
        selected_indexes = range(0, end_index+1)
        df_for_graph = df_less_columns[df_less_columns.index.isin(selected_indexes)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['New Comers_income_low_ratio'],
            legendgroup = "New Comers",  # this can be any string, not just "group"
            legendgrouptitle_text = "New Comers",
            name = "Low Inocme",
            mode = "lines",
            line = dict(color = 'royalblue', width = 1)
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['New Comers_income_medium_ratio'],
            legendgroup = "New Comers",  # this can be any string, not just "group"
            legendgrouptitle_text = "New Comers",
            name = "Medium Income",
            mode = "lines",
            line = dict(color = 'royalblue', width = 3)
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['New Comers_income_high_ratio'],
            legendgroup = "New Comers",  # this can be any string, not just "group"
            legendgrouptitle_text = "New Comers",
            name = "High Income",
            mode = "lines",
            line = dict(color = 'royalblue', width = 5)
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['stay_income_low_ratio'],
            legendgroup = "Staying",  # this can be any string, not just "group"
            legendgrouptitle_text = "Staying",
            name = "Low Income",
            mode = "lines",
            line = dict(color = 'firebrick', width = 1)
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['stay_income_medium_ratio'],
            legendgroup = "Staying",  # this can be any string, not just "group"
            legendgrouptitle_text = "Staying",
            name = "Medium Income",
            mode = "lines",
            line = dict(color = 'firebrick', width = 3)
        ))

        fig.add_trace(go.Scatter(
            x = graph.year_ranges,
            y = df_for_graph['stay_income_high_ratio'],
            legendgroup = "Staying",  # this can be any string, not just "group"
            legendgrouptitle_text = "Staying",
            name = "High Income",
            mode = "lines",
            line = dict(color = 'firebrick', width = 5)
        ))

        fig.add_trace(go.Scatter(x = [q_date_reference, q_date_reference], y = [0, 1],
                    name = q_date_reference,
                    legendgroup = "Reference",
                    legendgrouptitle_text = "Reference",
                    mode = "lines",
                    line = dict(color = "LightSeaGreen", width = 2, dash = "dashdot")))
        

        fig.update_layout(title = "Income by class for Staying vs New Comers", template = 'plotly_white', yaxis = {'title' : "ratio"}, margin = {"r" : 0, "t" : 35, "l" : 0, "b" : 35, "pad" : 0},
                            width = width_input, height = height_input, legend = dict(orientation = "h",  yanchor = "top", y = 0.99, xanchor = "left", x = 0.01))
        fig.update_layout(hovermode = "x unified")
        fig.update_xaxes(range = [0, len(graph.year_ranges)])
        fig.update_yaxes(range = [0, 1])


        return fig

    @staticmethod
    def current_construction(construction_typology_current, construction_typology_delta, width_input = 600, height_input = 250):

        """
        Generates a figure that describe the current typlogies that are bieng constucted for the selected year
        """
        try:
            v_a = construction_typology_current[construction_typology_current['project_ty'] == 1]['count'].values[0]
        except:
            v_a = 0
        try:
            v_r = construction_typology_current[construction_typology_current['project_ty'] == 2]['count'].values[0]
        except:
            v_r = 0
        try:
            v_rr = construction_typology_current[construction_typology_current['project_ty'] == 3]['count'].values[0]
        except:
            v_rr = 0

        try:
            d_a = construction_typology_delta[construction_typology_delta['project_ty'] == 1]['count'].values[0]
        except:
            d_a = 0
        try:
            d_r = construction_typology_delta[construction_typology_delta['project_ty'] == 2]['count'].values[0]
        except:
            d_r = 0
        try:
            d_rr = construction_typology_delta[construction_typology_delta['project_ty'] == 3]['count'].values[0]
        except:
            d_rr = 0
        fig = go.Figure()

        fig.add_trace(go.Indicator(
            mode = "number+delta",
            value = v_a,
            domain = {'x' : [0.06, 0.25], 'y' : [0.7, 0.85]},
            number_font_color="#2052a7",
            
            delta = {'reference' : d_a, 'relative' : True, 'valueformat' : '.2%'}))

        fig.add_trace(go.Indicator(
            mode = "number+delta",
            value = v_r,
            domain = {'x' : [0.3, 0.5], 'y' : [0.7, 0.85]},
            number_font_color = "#4c84cb",
            delta = {'reference' : d_r, 'relative' : True, 'valueformat' : '.2%'}))

        fig.add_trace(go.Indicator(
            mode = "number+delta",
            value = v_rr,
            domain = {'x' : [0.6, 0.80], 'y' : [0.7, 0.85]},
            number_font_color = "#87b1eb",
            delta = {'reference' : d_rr, 'relative' : True, 'valueformat' : '.2%'}))

        # Add images
        fig.add_layout_image(
                dict(
                    source="https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/assets/graphics/Building_Typology_png.png",
                    xref = "paper", yref = "paper",
                    x = 0, y = 0,
                    sizex = 1, sizey = 1,
                    xanchor = "left", yanchor = "bottom",
                    layer = "below")
        )

        fig.update_layout(template = "plotly_white", margin = {"r" : 0, "t" : 0, "l" : 0, "b" : 0, "pad" : 0}, width = width_input, height = height_input)
        return fig
