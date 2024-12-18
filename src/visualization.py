from typing import Union
import plotly
import plotly.express as px
import plotly.graph_objects as go



def name_encode_ys(yr_or_states:str)->str:
    '''
    Converts the database column name (a string passed in as yr_or_states) that represents the x axis in bar plot 
    to the approprate x-axis title in the final bar plot to be presented to the user in the final dash app
    
    Returns a string
    '''
    encoder={'year':'YEAR', 'state_id':'STATE'}
    return encoder[yr_or_states]

def encode_viz_type(user_click:str)-> bool:
    '''
    Takes in the value (the string user_click) associated with the radio item the user clicks in the final dash app that specifies what tpe of visualization they want
    Many functions querying the database use line_graph (a boolean) as an argument. This is used to convert the user specification into a boolean

    Returns a boolean, indicating whether the user wants a line graph (True) or bar plot (False)
    '''
    encoder={'Bar Plot': False, 'Line Graph': True}
    return encoder[user_click]

def encode_key_name_ys(user_click:str)->str: 
    '''
    Takes in a string called user_click, which is either 'States' or 'Years', values associated with the radio items the user can click in the final dash app
    It is called in main_dash.py when it calls the make_barplot function within the display_graph and display_table functions
    make_barplot, when only 1 data item and possibly 1 domain category have been chosen, and either multiple states and multiple years, or one state and one year chosen
    make_barplot needs to know if states or years are on the x-axis, so uses the argument yr_or_states, which is the database's column name equivalent of 'States' or 'Years' that the user chooses
    
    Returns the database's column name equivalent of the user's choice 'States' or 'Years'
    '''
    
    encoder={'States': 'state_id', 'Years': 'year'}
    return encoder[user_click]


def form_x_tick_labels(label_list:list[str], line_graph:bool=False, data_item:bool=False)->list[str]:
    '''
    Called by both 
    
    Prevents overlap of text in barplots and minimized visualizations in line graphs (once accomodating long horiztontal labels)
    Returns a list of strings to be used as the tick labels in a bar plot or line labels to be used in the legends of line graphs
    '''
    
    
    x_tick_labels=[] #represents final list of formatted tick labels for bar plots, or line labels in the legends of line graphs

    for i in label_list: 

        if data_item: #if comparing multiple data items, they will already have the same units specified on the y axis, this gets rids of the unit info for each tick(bar plot) or line(line graph) label
            i=i.split(' - ')[0]
        initial=i.split(' ') #splits each label in label list 
        if initial[-1]=="$": #prevents awkward labels in which 2nd line is just $
            initial=initial[:-2]+[initial[-2]+" $"]
        fin_l='' #represents the final formatted individual label of either a tick (bar plot) or line (line graph)
        label_line_n=len(initial)//3 #record how many lines that have 3 words in them 
        rem_w=len(initial)%3 #record how many remaining words there are after the grouping
        j=0
        for k in range(label_line_n): #gets every 3 words in an individual label and adds <br> to the end of it
            ret=initial[j:j+3]
            to_add=' '.join(ret)+'<br>'
            j+=3
            fin_l+=to_add #adds each newly formatted line to the final version of the individual label
        if rem_w !=0: ##if there were remaining words after grouping every 3 words of an individual label, adds a line break after them. Mainly done for readablility purposes in bar plots
            fin_l+=' '.join(initial[-rem_w:])+'<br>'
        if line_graph:
            #Items are spaced apart appropriately in make_line graph, so don't need the extra '<br>' in the last line of each label unlike in bar plots
            fin_l=fin_l[:-4] #removes '<br>'
        x_tick_labels+=[fin_l] #adds the final formatted label to the list of formatted labels

    return x_tick_labels

def set_dt_title(dt_list:list[str])->str:
    '''
    Called by get_full_title(operation, params, y_ax_title) and result is implemented in the case that there is only one data item specified by the user. 
    The data item is held as string in a list passed in as dt_list. 
    Otherwise dt_list is one long string of multiple data items (yet the result of this funciton is not used for the title in that case)
    
    The data item will be presented in the final title of the visualization and data table the user is able to obtain.
    Some data item names are quite long, so adds a line break after the 2nd comma if there are 3 or more commas
    
    Returns a string representing the properly formatted data item to be presented in the title of the final visualizations or data tables the user obtains
    '''
    d_title="".join(dt_list) #converts the list of one data item (a string) into an individual string
    check_sep=d_title.split(", ") #splits the string based on how many commas there are 
    if len(check_sep)>=3: #if there are more than 3 commas, adds a line break after the 2nd 
        new_title=", ".join(check_sep[:2])+"<br>"+", ".join(check_sep[2:])
        return new_title
    return d_title

def get_full_title(operation:str, params:dict[str,list[str]], y_ax_title:str)->str:
    '''
    Called by make_bar_plot and make_line_graph in visualization.py to set titles for the visualizations, and display_table in main_dash.py in order to set a heading over the final data table

    Constructs title based on amount of domain categories or data items specified by the user in params (a dictionary where each key is a string and each value is a list of strings)
    Utilizes other values in params if necessary to construct a sufficientiy specific title 
    To give accurate title for visualization/data table, takes in operation (in the sql aggregate function form of either Minimum, Maximum, Average, or Sum)
    Items that are present in all titles are the states and years selected by the user, held in params
    
    In the case multiple data items were chosen by the user, uses the y axis title passed in as y_ax_title(a string) in the overall title 


    Returns a sufficiently specific title for the visualization/data table the user wants to obtain as a string
    '''
    dt_title=set_dt_title(params['data_item'])
    if 'domain_category' in params.keys(): ##formats the data item to be presented in the title of the visualizations or data table appropriately 
        if len(params['domain_category'])==1: #domain, data item (only 1 was selected by user), domain category, state(s), year(s) included in title
            full_title= operation+ " OF "+dt_title+",<br>"+"".join(params['domain'])+": "+"".join(params['domain_category'])+",<br> IN "+", ".join(params['state_id'])+",<br>"+", ".join(params['year'])

        else: #domain, data item (only 1 was selected by user), state(s), year(s) included in title
            full_title=operation+ " OF "+dt_title+",<br>"+"".join(params['domain'])+" ITEMS"+"<br> IN "+", ".join(params['state_id'])+",<br>"+", ".join(params['year'])
     
    else: #domain=TOTAL since no domain category specified by the user in params
        if len(params['data_item'])>1: #multiple data items so uses y axis title in overall title 
            #y axis title, commodity, state(s), year(s) included in title
            full_title=operation+" OF TOTAL "+ y_ax_title+" FOR VARIOUS "+"".join(params['commodity'])+" DATA ITEMS"+",<br> IN "+", ".join(params['state_id'])+",<br>"+", ".join(params['year'])
        else: #only one data item specified so uses the properly formatted data item in dt_title, in addition to state(s) and year(s), in the title
            full_title=operation+" OF TOTAL "+dt_title+",<br>IN "+", ".join(params['state_id'])+",<br>"+", ".join(params['year'])
    return full_title

def set_title_pos(title:str)->float:
    '''
    Depending on specifications set by the user, the length of the title and how many line breaks it has changes
    In order to keep the title (passed in as a string and named title) look visually appealing no matter the amount of line breaks, 
    changes the vertical (y) position of the title depending on how many line breaks there are
    Approximately centers the table between the top of the line graph or bar plot and the top of the entire visualization

    Returns a float t_ypos describing the vertical position of the visualization titles
    '''
    t_ypos=0.9725
    t_br_ct=title.count('<br>') #counts how many line breaks there are in title
    if t_br_ct<3:
        t_ypos=0.945
    elif t_br_ct==3:
        t_ypos=0.96
    return t_ypos

def make_bar_plot(params:dict, yr_or_states: Union[str, None], y_data:list[float], operation:str)-> plotly.graph_objs._figure.Figure: 
    '''
    Takes in all of the specifications set by the user in the dictionary params (each key is a string, each value is a list of strings, the keys 
    consist of state_id, commodity, domain, data_item, possibly domain_category, and year), for bar plots takes in yr_or_states (a str representing the column of the user's choice 'year' or 'state_id') describing if states or years is on the x axis (otherwise is None),
    takes in the results of the query of the database according to the specifications in params as y_data( a list of floats), and takes in the sql aggegrate function (used in the query) in the form of a string passed in as operation (MIN, MAX, AVG, SUM) 
    
    Determines the x axis based on the amount of values and existence of keys in params, or value passed in as yr_or_states, and sets the corresponding axis title 
    Sets the appropriate x tick labels and formats them to avoid text overlap by calling form_x_tick_labels(label_list, line_graph, data_item)
    Sets the x tick label size based on what is on the x axis :
        Year or states have a slightly larger tick label font size on the x axis compared to domain categories or data items on the x axis for readability purposes 
    When setting x_tick_labels, sorts the list of items (held in by one the keys in params) in ascending order to match the ordering of results from execute_final_query (held in y_data)
    Determines what units will be on the y axis, stored as y_ax_title
    Gets the appropriate title for the bar plot by calling get_full_title(operation, params, y_ax_title), and its position by calling set_title_pos(title)
    Formats the hovertext for all bars, text dependent on what is on the x axis
    Creates bar plot
    
    
    Returns the bar plot to be placed in the final Dash app as a plotly.graph_objs._figure.Figure
    '''
    
    if yr_or_states == None: ##indicates that year or states aren't guaranteed to be x axis
        x_ax_tick_font=9 
        if 'domain_category' in params.keys(): #indicates only one data item specified, so data item is not on the x axis
            if len(params['domain_category']) >1:  ##indicates domain category is on the x axis
                x_ax_title="".join(params['domain']) ##domain name is x axis title since each domain category is related to it
                x_tick_labels=form_x_tick_labels(sorted(params['domain_category'])) #gets properly formatted x tick labels with line breaks to avoid overlap of text
                hover_x='Domain Category'
            elif len(params['state_id'])>1 & len(params['year'])==1: #indicates states are on the x axis
                x_ax_title="STATE" #sets title of x axis to STATE

                x_tick_labels=[i+"<br>" for i in sorted(params['state_id'])] #adding <br> to the end of every state to match format of other tick labels formatted by form_x_tick_labels
                #keeps consistent hovertext format no matter what is displayed on x axis
        
                hover_x='State' # State is category of first item in hovertext for each bar
                x_ax_tick_font=12
            else: ##only instance left that wouldnt require a value for yr_or_states is where years is on the x axis, or len(params['year']>1) & len(params['state_id']==1)
                x_ax_title="YEAR" #sets title of x axis to YEAR

                x_tick_labels=[i+"<br>" for i in sorted(params['year'])] #adding <br> to the end of every year to match format of other tick labels formatted by form_x_tick_labels 
           
                hover_x='Year' #Year is category of first item in hovertext for each bar
                x_ax_tick_font=12
        else: ##indicates at least one data item was chosen, while no domain categories were chosen (domain=TOTAL)
            if len(params['data_item']) >1: ##indicates data item is the x axis
                x_ax_title="".join(params['commodity'])+' DATA ITEM' ##adds commodity name to axis title to be specific
                x_tick_labels=form_x_tick_labels(label_list=sorted(params['data_item']), line_graph=False, data_item=True) #gets properly formatted x tick labels with line breaks to avoid overlap of text
                hover_x='Data Item' #Data Item is category of first item in hovertext for each bar
            
            elif len(params['state_id'])>1 & len(params['year'])==1: ##indicates states are on the x axis
                x_ax_title="STATE"
                x_tick_labels=[i+"<br>" for i in sorted(params['state_id'])] #adding <br> to the end of every state  to match format of other tick labels formatted by form_x_tick_labels
             
                hover_x='State' #State is category of first item in hovertext for each bar
                x_ax_tick_font=12
            else: ##only instance left that wouldnt require a value for yr_or_states is where years is on the x axis, or len(params['year']>1) & len(params['state_id']==1)
                x_ax_title="YEAR"
                x_tick_labels=[i+"<br>" for i in sorted(params['year'])] #adding <br> to the end of every year  to match format of other tick labels formatted by form_x_tick_labels
                hover_x='Year' #Year is category of first item in hovertext for each bar
                x_ax_tick_font=12

      
    else: ##year or state is guaranteed to be on the x-axis
        x_ax_tick_font=12
        x_ax_title=name_encode_ys(yr_or_states) #retrieving visualization format of column names of database (which are held in yr_or_states as 'year' or 'state_id')
  
        x_tick_labels=[i+"<br>" for i in sorted(params[yr_or_states])] ##yr or states will be either 'state_id' or 'year'
        hover_x=name_encode_ys(yr_or_states).capitalize()
    ##making y axis:
    y_ax_title=params['data_item'][0].split(' - ')[-1] #obtaining units to put on the y axis


    # Creating bar plot
    x_key=x_ax_title
    data={x_key: x_tick_labels, 'value': y_data}
    fig = px.bar(data, x=x_key, y='value', width=850, height=600, color=x_tick_labels)
    fig.update_traces(hovertemplate=hover_x+': %{x}<br>Value: %{y}<extra></extra>') #configuring hovertext 
    full_title=get_full_title(operation, params, y_ax_title) #obtaining appropriate title for visualization 
    t_ypos=set_title_pos(full_title) #obtaining vertical position for overall title of visualization

    fig.update_layout(
    title={'text': full_title, #formatting title
           'x':0.5,
           'y':t_ypos,
           'font': dict(size=14),
           'xanchor':'center'},
        showlegend=False,
        xaxis_title=x_ax_title,
        yaxis_title=y_ax_title,
        width=940,
        height=705,
        xaxis = dict( #adjusting tick labels
        tickfont = dict(size=x_ax_tick_font), 
        tickangle=0),
        hoverlabel=dict(bgcolor='white',font=dict(color='black')), #styling hovertext
        margin=dict(l=50, r=50, t=100, b=50) #setting margins of visualization
    )

    return fig



def make_line_graph(params:dict[str, list[str]], y_data:list[list[float]],operation:str, s_multiple_or_one:Union[str, None])->plotly.graph_objs._figure.Figure:

    '''
    Takes in all of the specifications set by the user in the dictionary params (each key is a string, each value is a list of strings, the keys 
    consist of state_id, commodity, domain, data_item, possibly domain_category, and year), for line graphs takes in s_multiple_or_one, a str 'multiple' or 'one' representing the amount of lines the user wanted to display if they chose multiple states, otherwise is None
    takes in the results of the query of the database according to the specifications in params as y_data( a list of lists of floats, where each list is the length of how many years specified by the user), and takes in the sql aggegrate function (used in the query) in the form of a string passed in as operation (MIN, MAX, AVG, SUM) 
    
    Determine what is displayed in the linegraph according to the amount of items in the keys data_item and domain_category in params, or uses s_multiple_or_one if states could possibly be represented by a line in the line graph (when one data item and/or one domain category chosen)
    Formats how the names of each of the lines to be displayed in the legend by calling form_x_tick_lables(params, line_graph, data_item) if each line is a data item or domain category, ensuring a minimal amount of horizontal space is used by using line breaks
    When doing so also sort them in alphabetical order to match the ordering of results from the query to the database held in y_data, if states are representing each line also sorts them in alphabetical order
    
    If multiple lines are to be displayed on the graph, uses a for loop to add traces to the graph, each wiht its own legend group to then be able to set spacing betwene each of the labels for the lines
    Formats hovertext for each line added to the graph

    Determines y axis title, finds title for overall visualization by calling get_full_title(operation, params, y_ax_title), and find vertical position for title by calling set_title_pos(title)
    Adjust hovertext styling, title format, and spacing between items in the legend 

    
    Returns the line graph to be placed in the final Dash app as a plotly.graph_objs._figure.Figure
    '''

    fig = go.Figure()


    ##setting labels of each line in line graph
    if len(params['data_item'])>1: ##each line represents a data item

        data_list=form_x_tick_labels(label_list=sorted(params['data_item']), line_graph=True, data_item=True) ##obtaining properly formatted labels for each line with line breaks to avoid large amount of  horizontal space taking up space on visualization
    elif 'domain_category' in params.keys():
        if len(params['domain_category'])>1: #each line represents a domain category

            data_list=form_x_tick_labels(sorted(params['domain_category']), True)
        else: #state field is what is being analyzed
            if s_multiple_or_one == 'multiple': #if there are multiple states chosen by the user, and they want each line in the line graph to represent one state
                data_list=sorted(params['state_id']) 
            else: #if there is only one state specified by the user, or they chose multiple states but want the line to be an aggregation of them in relation to the domain category chosen (s_multiple_or_one='one')
                data_list=y_data 
        
    else: #indicates only one data item was chosen and no domain category was chosen, leaving states to be represented by the lines
        if s_multiple_or_one == 'multiple': #if user chose multiple states and specified s_multiple_or_one
            data_list=sorted(params['state_id'])
  
        else:
            data_list=y_data ##just the values
 
    ##Creating line graph

    if (len(params['state_id'])==1) and (s_multiple_or_one ==None) and (len(params['data_item'])==1) : ##only one state and data item specified by the user

        if 'domain_category' in params.keys():
            if len(params['domain_category'])==1:
        
                fig.add_trace(go.Scatter(x=params['year'], y=y_data[0], #just one line
                                        mode='lines+markers',
                                        name="".join(params['state_id']),hovertemplate='Year: %{x}, Value: %{y}<extra></extra>'))
            else: ##more than one domain_category
                for i in range(len(data_list)): ##adding a line for every domain category chosen by the user
                    fig.add_trace(go.Scatter(x=params['year'], y=y_data[i],
                                        mode='lines+markers',
                                        name=data_list[i],hovertemplate='Year: %{x}, Value: %{y}<extra></extra>',
                                        legendgroup="Group"+str(i),legendgrouptitle_text=''))
        else:
            fig.add_trace(go.Scatter(x=params['year'], y=y_data[0], #just one line
                                        mode='lines+markers',
                                        name="".join(params['state_id']),hovertemplate='Year: %{x}, Value: %{y}<extra></extra>'))

    elif s_multiple_or_one != 'one': ##if s_multiple_or_one = multiple or None, and already covered case where there could only be just one line
        for i in range(len(data_list)): ##adding a line for every data item or state chosen by the user
            fig.add_trace(go.Scatter(x=params['year'], y=y_data[i],
                                mode='lines+markers',
                                name=data_list[i],hovertemplate='Year: %{x}, Value: %{y}<extra></extra>',
                                legendgroup="Group"+str(i),legendgrouptitle_text=''))
    
    
    
    else: ##last case left is if s_mulitple_or_one = One, meaning multiple states were also chosen by the user, so results to display are the only list held in the list y_data
        fig.add_trace(go.Scatter(x=params['year'], y=y_data[0],
                                mode='lines+markers',hovertemplate='Year: %{x}, Value: %{y}<extra></extra>'))#,
                                #name='filler')





    y_ax_title=params['data_item'][0].split(' - ')[-1] #obtaining units to put on the y axis
    full_title=get_full_title(operation, params, y_ax_title) ##retrieving appropriate title for visualization
    t_ypos=set_title_pos(full_title) ##retrieving appropriate vertical position of the overall title for the visualization

    fig.update_layout(
        title={'text':full_title, #formatting title
               'x':0.5,
               'y':t_ypos,
               'font': dict(size=14),
               'xanchor':'center'},
        xaxis_title='YEARS', #constant YEARS as x axis title since this is a line graph
        yaxis_title=y_ax_title,
        width=940,
        height=705,
        hoverlabel=dict(bgcolor='white',font=dict(color='black')), #formatting hovertext style
        margin=dict(l=50, r=50, t=100, b=50), #sets margins of actual visualization
        legend=dict(tracegroupgap=10) ##setting space in between each label corresponding to a line (legend group) on the line graph
        
        )


    return fig


