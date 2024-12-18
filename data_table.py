from typing import Union
import pandas as pd
from src.visualization import name_encode_ys




def build_stat_df_line(col_names: list[str], df_params: dict[str, list[str]], df_vals: list[list[float]],param_key:str)->pd.DataFrame:
    '''
    Called by get_statistics(path, vals, params, yr_or_states, s_multiple_or_one, line_graph) when line_graph=True, indicating that the user wanted a line graph

    Takes in a list object with one string as its only value called col_names that denotes the title of the first column of the data table to be made,  
    a dictionary passed in as df_params, with each key a string and each value a list of strings, describes the specifications set by the user for state_id, commodity, domain, data item, year, and possibly domain category
        a list of lists called df_vals, where each element in a list is a float, the corresponding value of a particular line on the line graph at a specific year chosen by the user,
        a string called param_key to denote what key in the irrigation database each line on the corresponding line graph relates to (state_id, data_item, or domain_category)
    
    Constructs a 2-d list that is then translated into a pandas DataFrame that will be presented to the user if desired.
    Each list is composed of the name of a line represented on the line graph and its corresponding values for each year specified by the user
    Sorts the list of strings assoicated with df_params[param_key] to match the ordering of data in df_vals

    Return the pandas DataFrame to get_statistics
    '''
    
    
    data=[] #sets up list of lists to be converted to a pandas DataFrame
    df_col_names= col_names #sets the name of the first column to be the category under which each line in the line graph the user obtains correponds to each 
    #(ex. if each line is a domain category, the title of the first column is the corresponding domain, if each line is a state, the tite of the first column is STATE )
    df_col_names+=df_params['year'] #sets the rest of the column names to the years specified by the user (each column is one year)
    sorted_params=sorted(df_params[param_key]) #sorts the associated item labels for each line in the line graph in alphabetical order to match the odering of their correspondign values for each year (found in df_vals)
    for i in range(len(sorted_params)): #creates a 2-d list, where the first element is the label for an individual line in the lien graph the user obtain, and the remaining elemnets are its values for each year specified by the user
        insert_data=[]#sets up list to be added to the list of lists named data
        insert_data+=[sorted_params[i]] #sets first element in list to be the name of the item represented by a line in the line graph
        for j in range(len(df_params['year'])): ##retrieves the associated values for each year, for this particular item represented by a line in the line graph
            #ex. if 2013, 2018, 2023 specified by the user, the list to be added to the list of lists is [name of item represented by line, value for 2013, value for 2018, value for 2023]
            insert_data+=[df_vals[i][j]] 
        data +=[insert_data]  #adds newly made list to the list of lists      
    df = pd.DataFrame(data, columns=df_col_names) #converts the lists to a dataframe
    return df

def get_statistics(path:str, vals: Union[list[list[str]],list[float]], params: dict[str, list[str]],  
                   yr_or_states:Union[str, None], s_multiple_or_one:Union[str,None],line_graph: bool=False)->None:
    '''
    Called by dislay_table in main_dash.py in order to make the datatable presented to the user. Here constructs a pandas DataFrame and writes it to a .csv file that is accessed within display_table in main_dash.py
    Writes the DataFrame to a path specified by the string passed in as path


    To construct the data frame need to know whether the correponding visualization is a bar plot (line_graph=False) or line graph (line_graph=True)
    If the visualization is a line graph, s_multiple_or_one may be a string 'multiple' or 'one' denoting whether states chosen by the user were represented by multiple lines or one, not guaranteed to have a value so s_multiple_or_one can be passed in as None
    If the visualization is a bar plot, yr_or_states may be a string 'year' or 'state_id' denoting whether years or states is on the x axis of the corresponding bar plot, not guaranteed ot have a value so yr_or_states can be passed in as None
    To determine what is being visualized, requires params (a dictionary with strings as keys and a list of string as each value) and then concludes what the x axis is for bar plots, and what each line represents for line graphs
    To fully construct the data tables, requires vals, either a list of floats for bar plots, or a list of lists of floats for line graphs, 
        each holding the results of the query made to the irrigation database according the user specifications for state, year, commodity, domain, data item, and possibly domain catgeory
    The titles of the first column in the data tables are all upeprcase to match the style of the data in the irrigation database, as well as the corresponding visualizations
    
    
    Returns None once writing the pandas DataFrame to a .csv file
    '''
    
    if line_graph: #line_graph=True, so vals is a list of lists of floats
        if s_multiple_or_one=='multiple': ##indicates that each line in the line graph represents a state, so each row in the data table is a state's values for each year specified by the user in params['year']
            df=build_stat_df_line(col_names=['State'.upper()],df_params = params, df_vals=vals, param_key='state_id') #to access the state names specified by the user, sets param_key to state_id
       
        else: ##indicates that each line in the line graph represents a domain category or data item
            if 'domain_category' in params.keys(): #each line is a domain category
                #builds the data table according to a layout appropriate for a line graph, each column after the first is a year specified by the user
                #sets the title of the first column to be the all uppercase version of the domain selected by the user because each domain category falls under that domain
                df=build_stat_df_line(col_names=["".join(params['domain']).upper()], 
                    df_params=params, df_vals=vals, param_key='domain_category')

                #return df

            else: ##indicates each line is a data item
                #builds the data table according to a layout appropriate for a line graph, each column after the first is a year specified by the user
                #sets the title of the first column to be the all uppercase version of the commodity selected by the user because each possible data item specified falls under that category
                df=build_stat_df_line(col_names=["".join(params['commodity']).upper()+' Data Item'.upper()], 
                                      df_params=params, df_vals=vals, param_key='data_item')

    else: ##line_graph=False, so the user wanted a bar plot, and vals is a list of floats
        #in each case specified builds the data table according to a layout appropriate for a bar plot, the first column is the name of the x axis, and the second column is Value

        if yr_or_states == None: ##x axis is not guarenteed to be either YEAR or STATE, so need to look further into params to determine it and the title of the fist column of the data table to be displayed 
            if 'domain_category' in params.keys(): 
                if len(params['domain_category'])>1: #indicates each bar in the bar plot represents a domain category
                    #builds appropriate data table, makes first column title to be the corresponding domain to the domain categories chosen by the user
                    df=build_stat_df_bar(col_names=["".join(params['domain']).upper()], 
                                        df_params=params, df_vals=vals, param_key='domain_category')
                elif len(params['state_id'])>1 & len(params['year'])==1: #indicates each bar in the plot represents a state specified by the user in params['state_id]
                    df=build_stat_df_bar(col_names=["State".upper()], df_params=params, df_vals=vals, param_key='state_id')
                else: #indicates each bar in the plot represents a year specified by the user in params['year']
                    df=build_stat_df_bar(col_names=["Year".upper()], df_params=params, df_vals=vals, param_key='year')
               
            else: ##only data items specified (and are tick labels)
                if len(params['data_item'])>1: #indicates each bar in the bar plot represents a data item (domain=TOTAL)
                    #builds appropriate data table, makes first column title to include the commondity name since all data items specified fall under that category
                    df=build_stat_df_bar(col_names=["".join(params['commodity']).upper()+' Data Item'.upper()], 
                                     df_params=params, df_vals=vals, param_key='data_item')
                      
                elif (len(params['state_id'])>1) & (len(params['year'])==1):  #indicates each bar in the plot represents a state specified by the user in params['state_id]
                    df=build_stat_df_bar(col_names=["State".upper()], df_params=params, df_vals=vals, param_key='state_id')
                else: #indicates each bar in the plot represents a year specified by the user in params['year']
                    df=build_stat_df_bar(col_names=["Year".upper()], df_params=params, df_vals=vals, param_key='year')
        else: #x axis of barplot is guaranteed to be either STATE or YEAR (so STARE or YEAR is the first column title in the data table), yr_or_states denotes the column name in tMain in irrigation database, so calls name_enocde_ys 
            #found in visualization.py to convert the column name to its more common name (state_id -> States, and year --> Years)
            df=build_stat_df_bar(col_names=[name_encode_ys(yr_or_states).upper()], 
                                     df_params=params, df_vals=vals, param_key=yr_or_states)
           
    df.to_csv(path, index=False) #writes the pandas DataFrame to a .csv file saved at the path specified by path, to which then gets accessed in main_dash.py to present the data table to the user  
    return #returns None


def build_stat_df_bar(col_names: list[str], df_params: dict[str, list[str]], df_vals: list[float],param_key:str)->pd.DataFrame:
    '''
    Called by get_statistics(path, vals, params, yr_or_states, s_multiple_or_one, line_graph) when line_graph=False, indicating that the user wanted a bar plot

    
    Takes in a list with one string as the element called col_name, represents the x axis of the bar plot the user obtains. 
    Forms a 2-dimensional list to be translated into a pandas DataFrame, where the first column title is the x axis title of the corresponding bar plot obtained by the user and the second column is Value
    Each entry in the first column represents the corrsponding tick labels to the bar plot obtained by the user, and each entry in the 2nd column is the corresponding y value
    Takes in df_params, a dictionary where each key is a string and each value is a list of strings. Each key is a column in the irrigation database (year, state_id, domain, domain_category, data_item), 
        and this function uses the string passed as param_key (a key name in df_params) to denote which set of strings in the dictionary represent the tick labels in the corresponding bar plot
    Sorts the list of strings assoicated with df_params[param_key] to match the ordering of data in df_vals, a list of floats that represent the results of the query to the database according to the specifications selected by the user in the final Dash app     
    
    Returns a pandas DataFrame to get_statistics
    '''
    
    data=[]
    df_col_names=col_names #sets first column of the to be created DataFrame as what the 
    df_col_names+=['Value'.upper()]#sets the second column name in the output dataframe
    sorted_params=sorted(df_params[param_key]) ##sorts the list strings held in df_params[param_key]
    for i in range(len(sorted_params)): 
        #creates 2-d list #each list has 2 elements (the first a string associated with a string value in df_params[param_key], 
        # and the second the corresponding numeric value held in df_vals)
        insert_data=[]
        insert_data+=[sorted_params[i]] #gets the tick label in the corresponding bar plot
        insert_data+=[df_vals[i]]#gets the numeric data for the tick label in the corresponding bar plot
        data +=[insert_data]        
    df = pd.DataFrame(data, columns=df_col_names) #creates pandas DataFrame
    return df



                
            