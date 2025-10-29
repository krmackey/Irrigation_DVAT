import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback, ctx
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
from src.Irr_DB import Irr_DB
from src.data_table import get_statistics
from src.visualization import *
from plotly.io import write_image
from typing import Union, Tuple

##setting up data table file name for when the user wants to look at a data table representative of the specifications they set when using the tool
PATH_DT="user_results/tables/table_"

##setting up figure file name for when the user wants their created visualizations to be saved as a png to their computer
PATH_FIG="user_results/figures/figure_"



# Creates the application, sets bootstrap components theme
app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA])

# Title (will appear in the browser tab)
app.title = 'Irrigation DVAT'

##Prepping the first checklist (states) that is not dynamic to the previous selections made by the user, needs to be in the format of a list of dictionaries
state_layout=[] 
for i in Irr_DB().get_states(): #retrieves state abbreviation data stored in the irrigation database
    single_state={'label': i, 'value': i} #for each item in the checklist, the state abbreviation is both the label presented to the user and its value 
    state_layout+=[single_state]

def layout()->list[Union[html.H1,html.Label, html.H6, dbc.RadioItems, dbc.Checklist, dcc.Dropdown, html.Div]]:
    ''''
    Sets up the layout for the entire Dash app
    Returns a list of children that an html.Div takes as argument. The order in which the children are added determines their order in the webpage. 
    The children consist of the types html.H1, html.Label, html.H6, dbc.RadioItems, 
        dbc.Checklist, dcc.Dropdown, and html.Div

    All dash.dcc.Dropdown.Dropdown objects have optionHeight=50, specifying the height of each possible item in the dropdown menu to 50px to prevent text overlap
    All dash_bootstrap_components._components.RadioItems.RadioItems have inline=True, meaning they display horizontally

    All items in children have no initial value set so that user can make their own selection
    Many items have options set to empty versions of their default type since they change dynamically and are set by callback functions
    
    '''
    # Sets up list to hold the items to be placed on the webpage
    children = []

    ##overall header for page
    header = html.H1('Irrigation Data Visualization and Analysis Tool', style={'textAlign': 'center'})
    children += [header]

    ##Label for welcome section
    wel_head=html.H5('Welcome!')
    children +=[wel_head]

    #Text for welcome message
    wel_message=html.Label('After you make a selection for a certain category, a new selection or question to answer will pop up in order to filter the data. For checklist items, the maximum number you can select is 5, with the exception of the additional data item section where the limit is 4, for effective visualization purposes. The final items that should pop up after you make all your data specifications are buttons allowing you to generate the graph, save it (as a .png), and generate the associated data table (which will also save it as a .csv). Before you can make a visualization or data table, you will be prompted to choose a statistic to be computed (average, sum, maximum, minimum) over the values of data you specified. The tool may ask you for which piece of data to compute the statistic over, but otherwise infers it based on the amount of items you chose for a particular category. If you do not want a visualization but a data table, you still must choose a type of graph in order to tell the tool how to compute your chosen statistic.')
    children +=[wel_message]

    #Break to separate text
    t_space=html.Div([html.Br()])
    children+=[t_space]

    #Text for user to see assumptions made when cleaning the intitial data
    assumps=html.Label('Assume that all data items for the ENERGY commodity relate to on farm pumping, and all data items for the commodity PUMPS exclude wells. These assumptions were made in preprocessing the data from the USDA to reduce redundant text.', style={'color':'#d1251a'})
    children +=[assumps]

    #Break to separate text
    a_space=html.Div([html.Br()])
    children+=[a_space]
  
    #Text for warning message about invalid data specifications, colored red
    warning=html.Label('If you stop seeing options for further data specification before seeing the final 3 buttons, your previous selections are likely invalid and you must specify different data to be visualized/analyzed.', style={'color':'#d1251a'})
    children +=[warning]

    #Break to separate text
    r_space=html.Div([html.Br()])
    children+=[r_space]

    #Text for warning users to rename file names
    rename=html.Label('After you save a figure or data table (found in either the figures or tables folders in the user_results folder), you should rename them so that they are not overwritten in your next session using this tool.', style={'color':'#d1251a'})
    children +=[rename]

    #Break to separate text
    e_space=html.Div([html.Br()])
    children+=[e_space]


    #Radio item to choose line or bar plots, formatted horizontally
    viz_label=html.H6('What type of visualization do you want?')
    viz_radio=dbc.RadioItems(id="viz-r", options=["Line Graph", "Bar Plot"], value="", inline=True) 
    ##when selected, viz-r value is set to either 'Line Graph' or 'Bar Plot'
    children +=[viz_label, viz_radio]
    

    ##State checklist , displayed horizontally, no initial values chosen, the items user can choose from is state layout, the states a user can choose to visualize irrigation data from
    #User limited to 5 choices with callback over function update_multi_options(value, viz_type), whether or not this section is displayed controlled by same callback 
    state_cl_label=html.H6('Select States', id='state-label') #introduces state section
    state_cl=dbc.Checklist(id='state-cl', 
        options=state_layout,
        value=[], inline=True #inline=True so that checklist displays horizontally and saves vertical space
    ) #the value of state-cl after the user makes their selections is a list of strings (each a state abbreviation)
    children += [state_cl_label, state_cl]


    # First dropdown menu, allows user to select a commodity (not affected by previous user choices of visualization type and state(s))
    # Options and whether or not displayed determined by callback function display_coms(state_id)
    com_label = html.H6('Select a commodity', id='com-label') ##introduces commodity section 
    com_dd = dcc.Dropdown(id='com-dd', 
                          options=[''] , 
                          value='', optionHeight=50 
                          ) #the value for com-dd after the user makes their selection is a string 
    children += [com_label, com_dd]
 
    # Second dropdown menu, allows user to select a domain, options based on commodity and state(s) already chosen by user
    #Option and whether or not displayed determined by callback over function update_doms(state_id, commodity)
    dom_label = html.H6('Select a domain', id='dom-label') ##introduces domain section
    dom_dd = dcc.Dropdown(id='dom-dd', 
                             options=[],
                             value='', optionHeight=50
                             ) #the value for dom-dd after the user makes their selection is a string
    children += [dom_label, dom_dd]


    #Third dropdown menu, allows user to select a data item, options based on the commodity, domain, and state(s) chosen by the user
    # Options and whether or not displayed determined by callback over function update_dts(state_id,commodity, domain)
    dt_label = html.H6('Select a data item', id='dt-label') ##introduces data item section
    dt_dd = dcc.Dropdown(id='dt-dd', 
                             options=[], #needs a list 
                             value='', optionHeight=50
                             ) #the value for dt-dd after the user makes their selection is a string
    children += [dt_label, dt_dd]


    #If user chooses TOTAL as the domain, the only domain categories possible to choose from are named UNSPECIFIED which is unhelpful. 
    #To combat this issue, this question asks the user if they want to visualize multiple data items that use the same units as the one they initially picked, or just one data item
    #Options 'Multiple Data Items' and 'One Data Item' are set by callback over function ask_mult_dt(domain, data_item), whether they are displayed or not is determined in same callback
    #If user chooses 'One Data Item' the next selection possible is years. If user chooses 'Multiple Data Items' the user will be presented with the next item (id = 'tot-dom-dt')
    mult_dt_r_label=html.H6('Do you want to visualize/analyze multiple data items, or one?', id='mult-dt-r-label')
    mult_dt_r=dbc.RadioItems(id="mult-dt-r", options=[''], value='', inline=True)
    children += [mult_dt_r_label, mult_dt_r]


    ##Presents a checklist of valid data items to choose from in the occassion that user selected total as domain, and wants to compare multiple data items 
    ##valid options dependent on user selections of state(s), commodity, domain, and data item, options are then set by callback over function update_mult_dts_items(mult_dt_q, state_id, commodity, domain, data_item, init_vals)
    ##Limited to 4 choices (makes it 5 including the data item chosen in the data item section) through a callback function update_mult_dts_items(mult_dt_q, state_id,commodity, domain, data_item, init_vals)
    tot_dom_dt_label=html.H6('Select Additional Data Items', id='tot-dom-dt-label') ##introduces additional data item section
    tot_dom_dt=dbc.Checklist(id='tot-dom-dt',
        options=[], #needs a list of dictionaries (dynamic)
        value=[] #the value of tot-dom-dt after the user makes their selections is a list of strings
    )
    
    children += [tot_dom_dt_label, tot_dom_dt]

    ##checklist for domain_categories, will only appear if user didn't pick TOTAL as the domain
    #valid domain categories to chose from are dependent on state(s), commodity, domain, and data item previously selected by user
    #valid options set by callback over function update_dc(state_id,commodity, domain, data_item, init_vals)
    # user limited to select 5 options in same callback 
    dc_label=html.H6('Select domain categories', id='dc-label') ##introduces domain category section
    dc_cl=dbc.Checklist(id='dc-cl',
            options=[],
            value=[]) #the value of dc-cl after the user makes their selections is a list of strings
    children += [dc_label, dc_cl]

    ##checklist for user to choose valid years, valid years are dependent on state(s), commodity, domain, data item(s), and possibly domain category(ies) previously selected by the user
    ##valid options and whether they are displayed or not determined by callback over function update_years(mult_dt_q, state_id, commodity, domain, data_item, add_data_item, domain_category, init_vals)
    # user limited to select 5 options in same callback 
    year_cl_label=html.H6('Select Years', id='year-cl-label') ##introduces year section
    year_cl=dbc.Checklist(id='year-cl',
        options=[], #needs a list of dictionaries (dynamic)
        value=[] #the value of year-cl after the user makes their selections is a list of strings
    )
    children += [year_cl_label, year_cl]

    
    # Asks what statistic user wants to visualize/analyze
    ##Creates 4 radio buttons user can select from (can only select 1) that describe the statistic they want to implemented over the data the user specified (Minimum, Maximum, Average, Sum)
    #Sets options with callback over function ask_stat(mult_dt_q, state_id, commodity,year, domain, data_item, add_data_item, mult_dt_r, domain_category)
    statq_r_label=html.H6('What statistic do you want to visualize/analyze?', id='statq-r-label') ##introduces choose statistic section
    statq_r=dbc.RadioItems(id="statq-r", options=[''], value='', inline=True)
    children += [statq_r_label, statq_r]


    # If bar plot chosen, where either (number states chosen >1 and number of years chosen >1) OR (number of states chosen =1 and number of years chosen =1)
    # and domain=TOTAL and one data item chosen 
    # or domain isn't TOTAL, and user chose one data item with one domain category
    #tool needs to know what item, years or states, that user wants as the x axis
    #Asks with 2 radio buttons (user must choose one) 'States' or 'Years', values and whether or not question displayed determined by callback over function ask_barplot_xax
    #User must have already picked visualization type, state(s), commodity, domain, data item(s), year(s), and possibly domain category(ies)
    barxax_r_label=html.H6("Do you want states or years on the x-axis? In other words, what do you want your chosen statistic to be reflective of?", id="barxax-r-label")
    barxax_r=dbc.RadioItems(id="barxax-r", options=[''], value='', inline=True)
    children += [barxax_r_label, barxax_r]

    # If line graph chosen, where user chose multiple states, 
    #  and domain=TOTAL with one data item chosen
    # or domain isn't TOTAL, where user chose one data item and one domain category
    # the tool needs know how many lines need to be on the line graph to display the states specified (represent a collection of states individually, or as one line)
    # Asks with 2 radio buttons (user must choose one) 'Multiple Lines' or 'One Line', values and whether or not question displayed determined by callback over function ask_linegraph_line_n
    #User must have already picked visualization type, state(s), commodity, domain, data item(s), year(s), and possibly domain category(ies)
    line_n_r_label=html.H6("Do want one line, representing your operation over all states specified, or multiple lines, each representing your state and your specified operation for only that state?",id="line-n-r-label")
    line_n_r=dbc.RadioItems(id="line-n-r", options=[''], value='', inline=True)
    children += [line_n_r_label, line_n_r]
    

    ##generate graph button, presents graph associated with past user data specifications once clicked
    #disabled property determined by callback over function display_graph
    graph_button=dbc.Button("Generate Graph", id='graph-button', n_clicks=0,className="me-1")

 

    ##save figure button (saves the graph obtained by the user as .png)
    ##intially disabled because user must click the generate graph button before clicking this button (disabled property determined by callback over function display_save_fig_button)
    save_fig_button=dbc.Button("Save Figure", id='save-fig-button', n_clicks=0, disabled=True,className="me-1")
    
   
    #creates a button for user to click if they want to download a .csv version and see the results they obtain from all their specifications on the data
    #whether or not button is disabled is determined by callback over function display_table (disabled after clicking once for a specific set of selections made by the user)
    data_table_button=dbc.Button("Generate Data Table", id='data-table-button', n_clicks=0)
    
    #creates a container for all 3 buttons so that they can be displayed horizontally with space in between them (why graph-button and save-fig-button have the className me-1)
    #whether or not all 3 buttons are displayed determiend by callback over function display_g_or_dt_buttons (dependent on whether all required data specifications have been made by the user)
    fig_button_group=html.Div([graph_button, save_fig_button, data_table_button], id='fig-bt-div')
    
    #adds container of 3 buttons to children 
    children+=[fig_button_group]
    
    #adds space between the button group and the graph or data table the user specifies they want to see 
    mes_space=html.Div([html.Br()])
    children+=[mes_space]
    

    ##adds graph to screen, whether or not displayed is determined by callback over function display_graph (dependenet on whether all previosu selections have been made and the button 'Generate Graph' has been clicked)
    graph=html.Div([dbc.Row([dbc.Col(dcc.Graph(id="graph",figure={}), width={ "offset": 1})])]) #sets an offset to center the graph in a typical webpage
    children+=[graph]

    ##adds space in in between graph and title of data table if user chooses to display both the graph and data table corresponding to their selections
    mes_space1=html.Div([html.Br()])
    children+=[mes_space1]
    
    ##adds data table based on user selections and its title to screen, data table and header over it (and whether displayed or not) are set in callback over function
    # because they are dependent on previous selections made by the user, and whether the 'Generate Data Table' button has been clicked

    table=html.Div(id="table-container")
    children+=[table]
    
    return children

app.layout = html.Div(id='main-div', children=layout(), style={'margin': '20px'}) #add layout to the webpage, specifying margin aroudn items to be 20px


#===================Callbacks=======================



##State section (user can choose multiple, selection is a list of strings)
@app.callback(
    Output("state-cl", "options"),
    Output("state-cl", "style"),
    Output("state-label", "style"),
    Input("state-cl", "value"), 
    Input("viz-r", "value")
)
def update_multi_options(value:list[str], viz_type:str)->Tuple[list[dict[str,str]], dict[str,str], dict[str,str]]: ##limiting state layout to only 5 possible states to pick
    '''
    Takes in list of strings detailing the states already chosen by the user as value, and the visualization type (passed in as string viz_type)if the user has specified it yet (its default value is '')
    If the visualization type hasn't been chosen yet, state section is not displayed
    If the type has been chosen, limits the amount of states the user can choose to 5 by resetting the options for 'state-cl' to have disabled items if 5 have already been clicked

    Returns the options for 'state-cl' as a list of dictionaries of strings (both as keys an values)
    For whether or not the state section is displayed, returns its style as a dictionary of strings twice 
        (once for the header and the other for actual checklist), where the key is 'style' and the value is either 'inherit' (displays as a checklist) or 'none'(doesn't display)
    '''
    
    style={'display':'none'}
    options = state_layout #already created
    if viz_type!="": #if no visualization type is chosen yet, the choose state section will not be displayed
        style={'display':'inherit'} #style of checklists
        if len(value) >= 5: #limits the amount of states a user can click to 5 by using dictionary comprehension, 
            #sets all other items to disabled if limit of 5 has been reached
            options = [
                {
                    "label": option["label"],
                    "value": option["value"],
                    "disabled": option["value"] not in value,
                }
                for option in options  
            ]
    return options, style, style



#Commodity section (user can only choose one, when chosen is a string)
@app.callback(
    Output("com-dd", "options"),
    Output("com-dd", "style"),
    Output("com-label", "style"),
    Input("state-cl", "value")
) 

def display_coms(state_id:list[str])->Tuple[list[str], dict[str,str], dict[str, str]]:
    '''
    Takes in the user's choice of state(s) as a list of strings, if no states have been chosen it is an empty string
    If the user has done a selection of states, the commodity dropdown and header are then displayed to the user, 
    with options being the results from get_commodity() in the Irr_DB class found in Irr_DB.py

    Returns a list of strings (to be the options for comm-dd the commodity dropdown), and two dictionaries (both key and value are strings) detailing the styling of the dropdown (whether its displayed or not)
    '''
    
    vals=Irr_DB().get_commodity() #get list of values to be chosen as commodity
    if len(state_id): #checking if any items are selected in the state field by the user
        style = {'display': 'block'} #display commodity field if states have been chosen
    else:
        style = {'display': 'none'} #don't display if states haven't been chosen
        vals=[]
    return ['']+vals, style, style


# Domain section (user can only choose one, when chosen is a string)

@callback(Output('dom-dd', 'options'),
        Output('dom-dd', 'style'), 
          Output('dom-label', 'style'), 
          Input('state-cl', 'value'),
          Input('com-dd', 'value')
          )
def update_doms(state_id:list[str],commodity: str)-> Tuple[list[str], dict[str, str], dict[str, str]]:
    '''
    Takes in values for state(s) as state_id (a list of strings) that were chosen by the user in a checklist
    and takes in the commodity chosen via dropdown (stored as a string called commodity), this is because domain options are dependent on these previous selections

    Queries the irrigation database, using get_domains function in the Irr_DB class, according to the available specifications, to get valid domains to choose from 
    if one of the parameters passed in has not been filled out by the user, the results from the query will be [] with no length
    
    Checks whether results of the query to the database have any length (more than []), if there are items in the results (called vals in this function), the dropdown to choose a domain is presented to the user
    If the results from the query are [], the dropdown is not displayed 

    Returns a list of strings (to be the options for dom-dd the domain dropdown), and two dictionaries (both key and value are strings) detailing the styling of the dropdown (whether its displayed or not)
    '''
    insert_dict={'state_id':state_id,'commodity': [commodity]} #each value must be a list of strings
    vals = Irr_DB().get_domains(insert_dict)
    if len(vals): #if results exist when querying the database
        style = {'display': 'block'} #display dropdown to user 
    else:
        style = {'display': 'none'}#don't display dropdown to user
    return ['']+vals, style, style


#Data Item section (user can only choose one, when chosen is a string)

@callback(Output('dt-dd', 'options'),
        Output('dt-dd', 'style'),
        Output('dt-label', 'style'),
          Input('state-cl', 'value'),
          Input('com-dd', 'value'),
          Input('dom-dd', 'value')
          )
def update_dts(state_id:list[str],commodity: str, domain: str)-> Tuple[list[str], dict[str, str], dict[str, str]]:

    '''
    Takes in the previous selections by the user: state(s) with state_id (a list of strings), commodity chosen with commodity (a string), domain chosen with domain (a string)
    This is because data item selection is dependent on state(s), commodity, and domain specified by the user

    Queries the irrigation database, using get_data_items function in the Irr_DB class, according to the available specifications, to get valid data items to choose from 
    if one of the parameters passed in has not been filled out by the user, the results from the query will be [] with no length

    Checks whether results of the query to the database have any length (more than []), if there are items in the results (called vals in this function), the dropdown to choose a data item is presented to the user
    If the results from the query are [], the dropdown is not displayed 
    
    Returns a list of strings (to be the options for dt-dd the data item dropdown), and two dictionaries (both key and value are strings) detailing the styling of the dropdown (whether its displayed or not)
    '''

    insert_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain]} #each value must be a list of strings
    vals = Irr_DB().get_data_items(insert_dict)
    if len(vals): #if results exist when querying the database
        style = {'display': 'block'} #display dropdown to user
    else:
        style = {'display': 'none'} #don't display dropdown to user

    return ['']+vals, style, style


##Additional Data Item question section (in the case the user chooses TOTAL as the domain) (user can only choose one option, stored as string)

@callback(Output('mult-dt-r', 'options'),
        Output('mult-dt-r', 'style'),
        Output('mult-dt-r-label', 'style'),
        Input('dom-dd', 'value'),
        Input('dt-dd', 'value')
          )

def ask_mult_dt(domain: str, data_item:str)->Tuple[list[str], dict[str, str], dict[str, str]]:
    '''
    If domain is set to TOTAL by the user, the next possible selection domain category only consists of UNSPECIFIED. 
    To combat issue, asks user if they want to only visulize the data item they have already chosen, 
    or if they want to compare across data items that also have TOTAL as their domain and have the same units as the initial 
    data item they have chosen 

    To know whether to ask the question, takes user selected domain as domain (a string), and user selected data item as data_item(a string)
    If the data item selection exists (is not None and is not ''), and if domain == TOTAL, the radio button item mult-dt-r is displayed with the options 'Multiple Data Items' and 'One Data Item'
    Otherwise, this question does not appear
    
    Returns a list of strings (to be the options for mult-dt-r (a radio button item), and two dictionaries detailing the styling (whether its displayed or not)

    '''

    style = {'display': 'none'} #by default, the question does not display
    vals=['']
    if data_item!=None: ##data_item must be defined 
        if (domain=="TOTAL") & (data_item!=''): #domain must be equal to TOTAL in order to ask this question
            style = {'display': 'inherit'} ##inherit sets the style to the default settings of radio items (the parent element mult-dt-r)
            vals=['Multiple Data Items', 'One Data Item'] #the options to be presented to the user if radio items are to be displayed

    return vals, style, style


##Additional Data Item selection section
##if user answered Multiple Data Items to the above question, need to give checklist of other possible data items
#selection is held as a list of strings

@callback(Output('tot-dom-dt', 'options'),
        Output('tot-dom-dt', 'style'),
        Output('tot-dom-dt-label', 'style'),
        Input('mult-dt-r', 'value'),
        Input('state-cl', 'value'),
        Input('com-dd', 'value'),
        Input('dom-dd', 'value'),
        Input('dt-dd', 'value'),
        Input('tot-dom-dt', 'value') 

          )

def update_mult_dts_items(mult_dt_q:str, state_id:list[str],commodity: str, domain: str, data_item:str, init_vals: list[str])->Tuple[list[dict[str,str]], dict[str,str], dict[str,str]]:
    '''
    Displays a checklist of additional data items the user can choose to visualize, only if they selected TOTAL as the domain and selected 'Multiple Data Items' to previous question 
    Otherwise doesn't display to the user. 

    Takes in answer to previous question (mult_dt_q, a string), all previous selections made according to the type of their values (dependent on what type of item they are),
        makes it so state selection is a list of strings state_id, commodity is a string commoidty, domain is a string domain, and initial data item is a string data_item. These are needed because the additional data item feild is dependent on all of these selections
    Function also needs the values already chosen by the user in this checklist (a list of strings called init_vals) to limit the amount of item a user can select in the checklist to 4

    Callback remembers past selections for this item (init_vals), even if they were for different previous data specifications (state, commoodity, domain, data item)
    To combat this, finds items already selected that match the results of additional data items returned by the get_domain_categories function in the Irr_DB class (which handles the case for choosing additional data items rather than domain categories)
    and ensures they match the units of the initial data item selected as well. Then sets the disabled items in the newly returned checklist of additinal valid items based upon the filtered initial values selected by the user
    
    Limits the amount of items a user can choose for this field to 4 so that final visualization only displays five items at a time
    

    Returns a list of dictionaries (each key and value is string) to denote the layout of the checklist for additional data items, and two dictionaries (each key and value is a string) detailing the styling (whether its displayed or not)
    '''
   
    dt_layout=[] #by default the checklist does not display
    style = {'display': 'none'}

    if all([state_id, commodity, domain,data_item]): ##returns True if all items are iterable -- returns false if any of them are None or not iterable (None, '' or [''])
        #if any of them are noniterable, the database will not be able to be queried 
        if ((data_item!='') and (domain=='TOTAL')) and (mult_dt_q!=''): ##a data item need to be chosen, the multiple data items question needs to be answered, and domain=TOTAL in order to display these additional data item options
            if mult_dt_q == "Multiple Data Items": #answer to previous question must be Multiple Data Items to display additional data items
                insert_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]} #input dictionary to get_domain_categories must have its values be lists of strings
                results = Irr_DB().get_domain_categories(insert_dict, mult_dt_q) #querying the database for valid adiditonal data items
                if len(results)==0: #indicates no valid results so additional data items to choose from are not displayed
                    return dt_layout, style, style 
                
                style = {'display': 'inherit'}#sets styling to default style of checklist 
                
                for i in results: #constructs list of dictionaries that make up the checklist tom-dom-dt, the label is what is presented to user, value is value associated with the label, in this case they are the same
                    single_dt={'label': i, 'value': i}
                    dt_layout+=[single_dt]
       
                ##found that the callback would remember previous user selections for additional data items in init_vals that didn't apply to most recent other data specifications
                ## to combat this checked if the the values already chosen by the user are within the results of asking the database for more data items, 
                # and if the data items already chosen by the user have the same units as the data item selected by the user and held in data_item

                filtered_vals=[]
                unit=data_item.split(' - ')[-1]
                for i in init_vals:
                    if i in results: ##making sure whatever data items previsouly picked for a previous data item apply still
                        i_unit=i.split(' - ')[-1]
                        if i_unit==unit: #further ensures by checking the units of these items
                            filtered_vals+=[i]
             
                if len(filtered_vals)>=4: ##limiting the amount of items a user can select to 4 (making so a total of 5 data items can be display on the visualizations)
                    dt_layout = [
                    {
                        "label": option["label"],
                        "value": option["value"],
                        "disabled": option["value"] not in filtered_vals,
                    }
                    for option in dt_layout ##dictionary comprehension
                ]
 
    return dt_layout, style, style


##Domain Category selection (checklist) section
##Only displays if user didn't pick TOTAL as domain, user can choose mulitple options, overall selection held as a lsit of strings

@callback(Output('dc-cl', 'options'),
        Output('dc-cl', 'style'),
        Output('dc-label', 'style'),
        Input('state-cl', 'value'),
        Input('com-dd', 'value'),
        Input('dom-dd', 'value'),
        Input('dt-dd', 'value'),
        Input('dc-cl', 'value') 

          )


def update_dc(state_id:list[str],commodity: str, domain: str, data_item:str, init_vals: list[str])->Tuple[list[dict[str,str]], dict[str,str], dict[str,str]]:
    '''
    Displays a checklist of domain categories the user can choose to visualize, only if they didn't selected TOTAL as the domain, and therefore only chose 1 data item (as well as chose items for all previous selections possible)
    Otherwise doesn't display to the user.
    
    To query database for domain categories the user can choose from, takes in all previous user data specifications (states as state_id, a list of stirngs, commodity as a string commodity, domain as a string domain, data item as a string data_item) because
    domain category is dependent on these choices
    
    Callback remembers past selections for this item (init_vals, as list of strings), even if they were for different previous data specifications (state, commoodity, domain, data item)
    To combat this, finds items already selected that match the results of domain categories returned by the get_domain_categories function in the Irr_DB class 

    Limits the amount of domain categories a user can choose to 5, based upon the valid domain categories already chosen 
    
    Returns a list of dictionaries (each key and value is string) to denote the layout of the checklist for domain categories, and two dictionaries(each key and value is a string) detailing the styling (whether its displayed or not)

    '''
    dc_layout=[] #by default checklist doesn't display
    style={'display':'none'}
    if (domain!="TOTAL"): #domain can't be TOTAL in order for checklist to display
        insert_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}
        results=Irr_DB().get_domain_categories(insert_dict, None) #querying the database for domain categories to choose from according to user's previosu selections

        if len(results): #if there are any results display the checklist, if not, doesn't display checklist
            style = {'display': 'inherit'} #sets styling to default style of checklist 
        

            for i in results: #constructs list of dictionaries that make up the checklist dc-cl, the label is what is presented to user, value is value associated with the label, in this case they are the same
                single_dc={'label': i, 'value': i}
                dc_layout+=[single_dc]
      
            #checking the the values already chosen by the user are within the results of asking the database for domain categories
            filtered_vals=[]
            for i in init_vals:
                if i in results:
                    filtered_vals+=[i]

            if len(filtered_vals)>=5: #set the amount of items that can chosen by the user to 5, and determines validity of the options by using the filtered values
                dc_layout = [
                {
                    "label": option["label"],
                    "value": option["value"],
                    "disabled": option["value"] not in filtered_vals,
                }
                for option in dc_layout ##dictionary comprehension
            ]


    return dc_layout, style, style



##Year section, a checklist (user can choose multiple, value is stored as a list of strings)

@callback(Output('year-cl', 'options'),
        Output('year-cl', 'style'),
        Output('year-cl-label', 'style'),
        Input("mult-dt-r", 'value'),
        Input('state-cl', 'value'),
        Input('com-dd', 'value'),
        Input('dom-dd', 'value'),
        Input('dt-dd', 'value'),
        Input('tot-dom-dt', 'value'), 
        Input('dc-cl', 'value'),
        Input('year-cl', 'value')
        )
def update_years(mult_dt_q:str,state_id:list[str], commodity:str, domain:str, data_item:str, add_data_item:list[str], domain_category:list[str], init_vals: list[str])->Tuple[list[dict[str,str]], dict[str,str], dict[str,str]]: 
   
    
    '''
    Constructs checklist of valid years user can choose for their data specified above to reflect
    
    Valid years is dependent on all previous selections, so needs to account for cases in which user chose domain= TOTAL (so includes choice of multiple data items or one data item) and when they didn't
    If any essential specifications haven't been filled out, checklist doesn't display
    
    Since dependent on all previous selections, which types are dependent on the type of item they are, takes in answer to multiple data item as a string mult_dt_q, state(s) as a list of strings state_id,
    commodity as a string commodity, domain as a string domain, data item as a string data_item, possible additional data items as a list of strings add_data_item, and possible domain categories as a list of strings domain_category
    
    Because of callback remembering issue, needs to check for validity of domain categories stored in domain_category('dc-cl' value) in case domain !=TOTAL, 
    or needs to check for validity of data items stored in add_data_item('tom-dom-dt' value) in case domain == TOTAL and user chose 'Multiple Data Items' when asked with the radio items in mult-dt-r
    
    Sets up unique dictionary to send to get_years function in the Irr_DB class for each of these cases in order to adhere to how get_years works in its own conditional statements
    
    Then checks validity of years already chosen by user in a previous callback, stored as init_vals, a list of strings, and determines whether any of those are still valid based upon results of the get_years function

    Limits the amount of years a user can choose to 5, based upon the amount already valid and checked by the user

    Returns a list of dictionaries (each key and value is string) to denote the layout of the checklist for years, and two dictionaries detailing the styling (whether its displayed or not)

    '''
    
    yr_layout=[] #by default doesn't display checklist
    style={'display':'none'}
    if all([state_id, commodity, domain,data_item])==False: #if any of the essential specifications aren't specified (None, '' or ['']), year checklist isn't displayed
        return yr_layout, style, style
    
    ##Because of callback remembering issue, needs to check for validity of domain categories stored in domain_category('dc-cl' value) in case domain !=TOTAL, 
    # or needs to check for validity of data items stored in add_data_item('tom-dom-dt' value) in case domain == TOTAL and user chose 'Multiple Data Items' when asked with the radio items in mult-dt-r

    

    if (data_item !='') and (domain_category !=[]) and (domain !='TOTAL'): #means single data_item and some sort of domain category is defined
        ##check domain_categories that are valid w/in callback (remembers past selections even if dont apply to currents specifications)
        check_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}
        results=Irr_DB().get_domain_categories(check_dict, None) #gets all domain_category results possible
        valid_dc=[i for i in domain_category if i in results]  #gets valid domain categories(previous domain category results that are within the ones the user has already chosen)
        if len(valid_dc)==0: #if no valid domain categories, year checklist doesn't display
            return yr_layout, style, style
        insert_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item], 'domain_category': valid_dc}
         
    elif (domain == 'TOTAL') and (data_item != ''): ##domain ==TOTAL and data item exists

        if (mult_dt_q == 'Multiple Data Items') and (add_data_item!=[]): #user chose Multiple Data Items and items for the additional data items field
            ##check additional data items that are valid w/in callback (remembers past selections even if dont apply to currents specifications)
            check_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}
            results = Irr_DB().get_domain_categories(check_dict, mult_dt_q) #gets all additional data items possible
            valid_adt=[i for i in add_data_item if i in results] #gets valid additional data items(previous additional data item results that are within the ones the user has already chosen)
            if len(valid_adt)==0: #if no valid additional data items, year checklist doesn't display
                return yr_layout, style, style
   
            insert_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]+valid_adt}

        elif (mult_dt_q == 'One Data Item'): #user chose 'One Data Item', so not using add_data_item in any way
            insert_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}

        else: #indicates the question for  Multiple Data Items and One Data Item was not answered so year checklist doesn't display

            return yr_layout, style, style
    else:#checklist doesn't display if any of the base conditions aren't met
        return yr_layout, style, style
    
    results=Irr_DB().get_years(insert_dict) #querying database for years according to the valid specifications

    if len(results): #if there were any results, displays the year checklist of available years, if not, doesn't display checklist
        style={'display':'inherit'}#{'display':'initial'}
        #constructs list of dictionaries that make up the checklist year-cl, the label is what is presented to user, value is value associated with the label, in this case they are the same
        for i in results:
            single_yr={'label': i, 'value': i}
            yr_layout+=[single_yr]
        #checks for valid years alredy checked by user for past combination of data specifications
        filtered_vals=[]
        for i in init_vals:
            if i in results:
                filtered_vals+=[i]
        
        ##Limits amount of years that can be chosen by user to be 5, sets the rest of the items as disabled once 5 items are checked
        if len(filtered_vals)>=5:
            yr_layout = [
            {
                "label": option["label"],
                "value": option["value"],
                "disabled": option["value"] not in filtered_vals, 
            }
            for option in yr_layout ##dictionary comprehension
        ]

    return yr_layout, style, style

#Type of Statistic Section, presented as radio buttons (user can only choose one, when selected value is stored as a string )

@callback(Output('statq-r', 'options'),
        Output('statq-r', 'style'),
        Output('statq-r-label', 'style'),
        Input("mult-dt-r", 'value'),
        Input('state-cl', 'value'),
        Input('com-dd', 'value'),
        Input("year-cl", 'value'),
        Input("dom-dd", 'value'),
        Input('dt-dd', 'value'),
        Input('tot-dom-dt', 'value'),
        Input('dc-cl', 'value')
)

##need to include all past arguments and whether some are checked out not

def ask_stat(mult_dt_q:str, state_id: list[str], commodity:str,year:list[str], domain:str,data_item:str, add_data_item:list[str],  domain_category: list[str])->Tuple[list[str], dict[str,str], dict[str,str]]:
    '''
    Presents radio buttons that represent the statistic the user can choose to visualize for the specific data they have chosen( based on previous choices if certain conditions are met, otherwise doesn't display radio buttons)

    Dependent on all previous specifications possibly made, so takes in the answer to multiple data item question as a string mult_dt_q, state(s) as a list of strings state_id,
    commodity as a string commodity, domain as a string domain, data item as a string data_item, possible additional data items as a list of strings add_data_item, and possible domain categories as a list of strings domain_category

    Needs to check if all specifications are made for each possible case of domain=TOTAL (and thus whether or not additional data items were specified, and the question of displaying multiple data items or not has been answered), 
    and domain isn't equal to TOTAL (whether domain categories have been specified )

    Because of this and the callback remembering previous selections discussed above, checks validity of either additional data items, and in that whether the multiple data item question has been answered,
    or checks validity of domain categories selected
    In each case constructs a valid query to the database to check for years possible 
    From there also checks the validity of years chosen by the user, as the callback remembers year selections for different data specifications as well 
    
    If all required conditions have been met and there are valid years selected by the user, presents the radio buttons (Sum, Minimum, Maximum, Average)

    Returns a list of strings to denote labels of the radio buttons, and two dictionaries detailing the styling (whether they are displayed or not)
    '''
    
    
    options=[] #by default radio buttons don't display
    style={'display':'none'}

    if all([state_id, commodity, year, domain, data_item])==False: #checks if all essential arguments are iterable , if False (items are either None, '' or ['']) radio buttons don't display
        return options, style, style

    if domain=="TOTAL" and (mult_dt_q=='' or mult_dt_q==None): #if domain==TOTAL, the answer to the multiple data items question must be answered, if not radio buttons don't display
        return options, style, style

    if domain =="TOTAL" and mult_dt_q=="Multiple Data Items": #if domain=TOTAL and Multiple Data Items chosen, the additional data items must be filled and there must be valid entries
        check_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}
        results = Irr_DB().get_domain_categories(check_dict, mult_dt_q) #gets all possible additional data items based upon most current data specifications
        valid_adt=[i for i in add_data_item if i in results] #valid additional data items from previous user selection
        if len(valid_adt)==0:
            return options, style, style
        ##sets up checking for valid years
        year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]+valid_adt}
    elif domain!="TOTAL" and data_item!='' and len(domain_category)>0: #user didn't chose TOTAL as domain and has filled out domain categpry field
        #checks for if valid domain categories have been chosen by the user
        check_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]} 
        results=Irr_DB().get_domain_categories(check_dict, None) #gets all possible domain categories based upon most current data specifications
        valid_dc=[i for i in domain_category if i in results] #valid domain categories from previous user selection
        if len(valid_dc)==0: #if no valid domain categories chosen, radio buttons dont display
            return options, style, style
        year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item], 'domain_category':valid_dc}
    elif domain!="TOTAL" and data_item!='' and len(domain_category)==0: #radio buttons dont display if domain(domain!=TOTAL) and data item fields have been filled, but the domain category field has been filled 
        return options, style, style
    
    else: ##Last case possible is where domain=TOTAL and user has specified One Data Item, sets up year checking dictionary
        year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}

    year_results=Irr_DB().get_years(year_dict) #gets all possible years based upon most current data specifications
    valid_yrs=[i for i in year if i in year_results] #checks validity of previously selected years
    if len(valid_yrs)==0: #if there are no valid years then radio buttons don't display
        return options, style, style
    else: #if valid years have been chosen the radio buttons are displayed 
        options=['Average', 'Sum', 'Minimum', 'Maximum']
        style={'display':'inherit'}


    return options, style, style


#Bar Plot States vs. Years section (radio buttons where user can only choose, when selected value is stored as a string)

##In the case the user chose Bar Plot, and only chose either 1 data item and one domain category when domain!=TOTAL, or 1 data item when domain=TOTAL
##and where there were either multiple states and multiple years chosen, or one state and one year chosen
#tool needs to know whether states or years is on the x axis, and therefore what the statistic specified by statq-r is representative of)


@callback(Output('barxax-r', 'options'),
        Output('barxax-r', 'style'),
        Output('barxax-r-label', 'style'),
        Input('viz-r', 'value'),
        Input('state-cl', 'value'),
        Input('com-dd', 'value'),
        Input('dom-dd', 'value'),
        Input('dt-dd', 'value'),
        Input("mult-dt-r", 'value'), 
        Input('dc-cl', 'value'),
        Input('year-cl', 'value'),
        Input('statq-r', 'value')
          )

def ask_barplot_xax(viz_type:str,state_id:list[str], commodity:str, domain:str, data_item:str, mult_dt_q:str, domain_category:Union[list[str],list], year:list[str], stat_type:str) ->Tuple[list[str], dict[str,str], dict[str,str]]:
    '''
    If the user specified bar plot, and only chose one piece of data (either one data item if domain=TOTAL, or one data item and one domain category if domain !=TOTAL),
        and user has also either chosen multiple states and multiple years, or one state and one year, tool needs to know whether states or years are represented on the x axis of the bar plot

    Presents radio buttons 'State' and 'Years' for user to choose

    Existence dependent on all previous specifications, including the visualization type stored as a string viz_type and the type of statistic chosen stored as string stat_type. This means it also takes the answer to multiple data item question as a string mult_dt_q, year(s) as a list of strings year, state(s) as a list of strings state_id,
    commodity as a string commodity, domain as a string domain, data item as a string data_item, and possible domain categories as a list of strings domain_category (doesn't need to take in additional data items because mult_dt_q must be 'One Data Item' for the buttons to display)
    
    To account for all cases where domain=TOTAL and where it doesn't equal TOTAL, function checks validity of either item(s) in domain_category, and whether 'One Data Item' was specifed by mult_dt_q
    It then determines whether years have been selected by the user, and if they are valid by querying the irrigation database (if there aren't any valid domain categories or years, or 'One Data Item' has not been chosen, the buttons don't display )
    
    Returns a list of strings to denote labels of the radio buttons, and two dictionaries detailing the styling (whether they are displayed or not)
    '''
    vals=[] #by default radio buttons don't display
    style = {'display': 'none'}
    if all([state_id, commodity, year, domain, data_item, stat_type, viz_type])==False: ## if any previous essential data specification hasn't been made (isn't iterable like None, '' or ['']), radio buttons don't display
        return vals, style, style

    
    lin_bool=encode_viz_type(viz_type) #checking the type of visualization specified by user, if thye specified line graph these radio buttons aren't displayed
    if lin_bool==False:

        if (domain!="TOTAL") & (data_item!='') & (len(domain_category)>=1): #if user didn't choose domain= TOTAL, they must have chosen a domain category
            #retrieves the valid domain categories for the current set of data specifications that the user has already chosen
            check_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}
            results=Irr_DB().get_domain_categories(check_dict, None)
            valid_dc=[i for i in domain_category if i in results]
   
            if len(valid_dc)!=1: #the amount of valid domain categories must be 1, if not the radio buttons don't display
                return vals, style, style

            year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item], 'domain_category':valid_dc}
        elif (domain == 'TOTAL') & (data_item!='') & (mult_dt_q=="One Data Item"): #if the user chose domain=TOTAL, they must have needed to choose 'One Data Item' to require this question to be asked, if not buttons don't display
            
            year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}

        else: #catches any cases where domain_category hasn't been defined for domain !=TOTAL or where domain=TOTAL and mult_dt_q either has no answer or is 'Multiple Data Items'
            #does not display the radio buttons in these cases
            return vals, style, style
        #checks validity of years specified by user since callback remembers years previously chosen for different data specifications
        year_results=Irr_DB().get_years(year_dict)
        valid_yrs=[i for i in year if i in year_results]
        if len(valid_yrs)==0: #if there are no valid years that have been chosen, the buttons don't display
            return vals, style, style
       
        if ((len(state_id)==1) & (len(valid_yrs) ==1)) | ((len(state_id)>1) & (len(valid_yrs)>1)): #checks final condition to display radio buttons (multiple states and multiple years, or one state and one year)
            #if these conditions aren't met radio buttons don't display
         
            style = {'display': 'inherit'}
            vals=['States', 'Years']

    return vals, style, style



#Line Graph Multiple Lines vs. One Line section (radio buttons where user can only choose, when selected value is stored as a string) 

##In the case the user chose Line Graph, and only chose either 1 data item and one domain category when domain!=TOTAL, or 1 data item when domain=TOTAL
##and chose multiple states
#tool needs to know whether user wants multiple lines, each line representing a state, or one line representing the aggregation method (the value in statq-r) done over all the states

@callback(Output('line-n-r', 'options'),
        Output('line-n-r', 'style'),
        Output('line-n-r-label', 'style'),
        Input('viz-r', 'value'),
        Input('state-cl', 'value'),
        Input('com-dd', 'value'),
        Input('dom-dd', 'value'),
        Input('dt-dd', 'value'),
        Input("mult-dt-r", 'value'), 
        Input('dc-cl', 'value'),
        Input('year-cl', 'value'),
        Input('statq-r', 'value')
          )


def ask_linegraph_line_n(viz_type:str, state_id:list[str], commodity:str,domain:str, data_item:str, mult_dt_q:str, domain_category:Union[list[str],list], year:list[str],stat_type:str)->Tuple[list[str], dict[str,str], dict[str,str]]:
    '''
    If the user specified line graph, with either domain=TOTAL and one data item, or domain isn't equal to TOTAL and there is one data item and one domain category, 
    and the user has specified multiple states, tool needs to know whether user wants multiple lines, each line representing a state, or one line representing the statistic the user should have chosen by this step
    

    Present the options a user can pick to answer the question (multiple lines or one) through radio buttons ('Multiple Lines' and 'One Line')
    To ask this question, conditions above must be met, if they are not the buttons are not displayed

    Existence dependent on all previous specifications, including the visualization type stored as a string viz_type and the type of statistic chosen stored as string stat_type. This means it also takes the answer to multiple data item question as a string mult_dt_q, year(s) as a list of strings year, state(s) as a list of strings state_id,
    commodity as a string commodity, domain as a string domain, data item as a string data_item, and possible domain categories as a list of strings domain_category (doesn't need to take in additional data items because mult_dt_q must be 'One Data Item' for the buttons to display)
    
    To account for all cases where domain=TOTAL and where it doesn't equal TOTAL, function checks validity of either item(s) in domain_category, and whether 'One Data Item' was specifed by mult_dt_q
    It then determines whether years have been selected by the user, and if they are valid by querying the irrigation database (if there aren't any valid domain categories or years, or 'One Data Item' has not been chosen, the buttons don't display )
    
    '''
    
    
    
    vals=[] #by default radio buttons don't display
    style={'display':'none'} 
    if all([state_id, commodity, year, domain, data_item, stat_type, viz_type])==False: #if any of these essential fields haven't been filled (are not iterable like None, '' or ['']), the radio buttons do not display
        return vals, style, style
    
    
    lin_bool=encode_viz_type(viz_type)  #encodes viz_type to match the input of functions in Irr_DB.py
    if lin_bool==True: #checks whether the user specified Line Graph, if they did not the radio buttons do not display
        if len(state_id)>1: ##checking whether multiple states have been chosen, if not radio buttons don't display
            if (domain!="TOTAL") & (data_item!='') & (len(domain_category)>=1): #if domain!=TOTAL, domain_category list shoudl exist
                #check validity of items in domain_category (callback remembes previosu selections for different data specifications)
                check_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}
                results=Irr_DB().get_domain_categories(check_dict, None)
                valid_dc=[i for i in domain_category if i in results]
                if (len(valid_dc)!=1): #only 1 valid domain category must have been chosen by the user, if not the radio buttons don't display
                    return vals, style, style
                year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item], 'domain_category': valid_dc}

            elif (domain == 'TOTAL') & (data_item!='') & (mult_dt_q=="One Data Item"): #if the user chose domain=TOTAL, they must have needed to choose 'One Data Item' to require this question to be asked, if not buttons don't display
                year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}
            else: #catches any cases where domain_category hasn't been defined for domain !=TOTAL or where domain=TOTAL and mult_dt_q either has no answer or is 'Multiple Data Items'
            #does not display the radio buttons in these cases
                return vals, style, style
        
            #checks validity of years specified by user since callback remembers years previously chosen for different data specifications
            year_results=Irr_DB().get_years(year_dict)
            valid_yrs=[i for i in year if i in year_results]
            if len(valid_yrs)==0: #if there are no valid years that have been chosen, the buttons don't display
                return vals, style, style
            style = {'display': 'inherit'} #If valid years have been chosen, buttons to answer the question multiple lines or one line are presented as 'Multiple Lines' and 'One Line'
            vals=['Multiple Lines', 'One Line']
                
    return vals, style, style 





##Display buttons to generate graph, save figure, and generate data table section
# All of these buttons held in the html.Div fig-bt-div
@callback(Output('fig-bt-div', 'style'),
        Input('viz-r', 'value'),
        Input('state-cl', 'value'),
        Input('com-dd', 'value'),
        Input('dom-dd', 'value'),
        Input('dt-dd', 'value'),
        Input('tot-dom-dt', 'value'),
        Input("mult-dt-r", 'value'), 
        Input('dc-cl', 'value'),
        Input('year-cl', 'value'),
        Input('statq-r', 'value'),
        Input('barxax-r', 'value'),
        Input('line-n-r', 'value')
          )

def display_g_or_dt_buttons(viz_type:str,
                            state_id:list[str],
                            commodity:str,
                            domain:str,
                            data_item:str, 
                            add_data_item:list[str],
                            mult_dt_q:str, 
                            domain_category:Union[list[str],list], 
                            year:list[str],
                            stat_type:str,
                            barax:str,
                            line_n:str) -> dict[str,str]:
    
    '''
    Determines whether final buttons (Generate Graph, Save Figure, Generate Data Table) are displayed

    Checks whether all required specifications have been selected by the user based on their selections, including the instances in which they have to answer targeted questions 
    (such as multiple lines or one line for line graphs, or states or years on the x axis for bar plots)
    
    Because of this, takes in all of these parameters: visualization type described by a string viz_type, the statistic type described by a string stat_type,
    the possible answer to the x axis question for bar plots (a string barax (default value is an empty string)), 
    the possible answer to the number of lines question for line graphs (a string line_n (default value is an empty string)),
    the state(s) selected as a list of strings state_id, year(s) as a list of strings year, commodity as a string commodity, domain as a string domain, data item as a string data_item,
    possible additional data items as a list of strings add_data_item, and possible domain categories as a list of strings domain_category
    
    Checks validity of domain categories and additional data items entries if they are specified by the user since callback remembers past selections for different combinations of data specifications
    Takes into account whether domain=TOTAL and the answer to the multiple data items or one stored in mult_dt_q
    Then checks validity of years chosen by the user according to those valid domain categories or addiaiotnal data items 
    If there are no valid items for these fields, depending on whether domain=TOTAL or not, the three buttons do not display

    Then checks the cases in which barax or line_n need to have an answer, if they do not in these cases, the three buttons do not display

    Returns a dictionary (key and value are strings) describing the display of the final three buttons held in a html.Div (describes whether the buttons are shown to the user or not)
    '''
    
    style={'display':'none'} #by default the three buttons are nto shown to the user

    if all([state_id, commodity, domain, data_item, year, stat_type, viz_type])==False: #if any of these essential fields do not have a item selected (None, '' or ['']), the buttons do not display
        return style

    valid_dc=[]
    valid_adt=[]
    if (domain=='TOTAL') and (mult_dt_q=="Multiple Data Items"): 
        #if domain=TOTAL and user wants to visualize multiple data items, 
        #the additional data item field must at least one item, if not the buttons are not displayed
        if len(add_data_item)==0:
            return style
        #checking validity of already selected data items since callback remembers selections from different data specifications
        check_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}
        results = Irr_DB().get_domain_categories(check_dict, mult_dt_q)
        valid_adt=[i for i in add_data_item if i in results]
        if len(valid_adt)==0: #if there are no valid additional data items when domain=='TOTAL' and mult_dt_q=="Multiple Data Items" the buttons are not displayed
            return style
        ##sets up validity checking for years selected by user
        year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]+valid_adt}
    elif domain=='TOTAL' and mult_dt_q=="One Data Item": #no further validity checking when mult_dt_q=="One Data Item"
        year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}

    elif(domain!="TOTAL") & (data_item!='') & (len(domain_category)>=1):
        #check validity of items in domain_category
        check_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}
        results=Irr_DB().get_domain_categories(check_dict, None)
        valid_dc=[i for i in domain_category if i in results]
        if (len(valid_dc)==0): #if there are no valid domain categories selected by the user the three buttons aren't displayed
            return style
        ##sets up validity checking for years selected by user
        year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item], 'domain_category': valid_dc}
    else: #this accounts for the instances in which there is no answer to mult_dt_q for when domain=TOTAL, and when domain!=TOTAL and one data item has been chosen, but no domain category(ies) have been chosen
        return style #buttons do not display for these cases
    
    ##checking years and whether ones already specified are valid for current data specifications
    year_results=Irr_DB().get_years(year_dict)
    valid_yrs=[i for i in year if i in year_results]
    if len(valid_yrs)==0: #if no valid years are selected by the user, the three buttons are not displayed
        return style#, style
    
    ##Now checking for whether barax or line_n need to be more than empty strings
    
    lin_bool=encode_viz_type(viz_type) #encodes viz_type to match the input of functions in Irr_DB.py 
    if lin_bool == True: #user specified Line Graph
   
        ##check for conditions that would require line_n 
        if ((len(state_id)>1) & (domain!="TOTAL") & (len(valid_dc)==1)) | ((len(state_id)>1)&(domain == 'TOTAL') & (mult_dt_q=="One Data Item")):
            if line_n!='': 
                #if line_n does not have answer for how many lines should represent the multiple states specified by the user, 
                # exits conditional to final return, making it so the three buttons do not display, buttons display otherwise
                style = {'display': 'inherit'}
        else: #buttons display if line_n can be an empty string
            style = {'display': 'inherit'}

    else: #user specified Bar Plot
        ##check for conditions that would require bar_ax, since there are many cases (whether domain=TOTAL, amount of states selected, amount of years selected) broke it up into two conditionals
        if ((len(state_id)==1) & (len(valid_yrs) ==1)) | ((len(state_id)>1) & (len(valid_yrs)>1)):
            #cases where this is only one piece of data to be visualized withthe exception of states and years, requires barax to have a value 
            if ((domain!="TOTAL") & (len(valid_dc)==1)) | ((domain == 'TOTAL') & (mult_dt_q=="One Data Item")):
                if barax!='': #if barax does not have answer for what should be on the x axis (states or years)
                # exits conditional to final return, making it so the three buttons do not display, buttons display otherwise
                    style = {'display': 'inherit'}
            else:
                style = {'display': 'inherit'}
        else:
            style = {'display': 'inherit'}

    return style


##Display Graph section

@callback(Output('graph', 'figure'),
        Output('graph', 'style'),
        Output('graph-button', 'disabled'),
        Input('graph-button', 'n_clicks'),
        Input('viz-r', 'value'),
        Input('state-cl', 'value'),
        Input('com-dd', 'value'),
        Input('dom-dd', 'value'),
        Input('dt-dd', 'value'),
        Input('tot-dom-dt', 'value'),
        Input("mult-dt-r", 'value'), #if dom == TOTAL
        Input('dc-cl', 'value'),
        Input('year-cl', 'value'),
        Input('statq-r', 'value'),
        Input('barxax-r', 'value'),
        Input('line-n-r', 'value')
        )
def display_graph(n_clicks:int,
                    viz_type:str,
                    state_id:list[str],
                    commodity:str,
                    domain:str,
                    data_item:str, 
                    add_data_item:list[str],
                    mult_dt_q:str, 
                    domain_category:Union[list[str],list], 
                    year:list[str],
                    stat_type:str,
                    barax:str,
                    line_n:str)->Tuple[plotly.graph_objs._figure.Figure, dict[str,str], dict[str,str]]:
    '''
    Determines whether the corresponding graph to all the user's specifications, holding the results from the query to the irrigation database, is displayed or not, 
    and whether the button the user clicks to generate the graph gets disabled

    Since needs access to all previous user selections, takes in all of these parameters: visualization type described by a string viz_type, the statistic type described by a string stat_type,
    the possible answer to the x axis question for bar plots (a string barax (default value is an empty string)), 
    the possible answer to the number of lines question for line graphs (a string line_n (default value is an empty string)),
    the state(s) selected as a list of strings state_id, year(s) as a list of strings year, commodity as a string commodity, domain as a string domain, data item as a string data_item,
    possible additional data items as a list of strings add_data_item, and possible domain categories as a list of strings domain_category

    If the generate graph button has not been clicked for a particular combination of user selections, graph does not display
    If generate graph button has been clicked for a particular combination of user selections, it is disabled
    Uses ctx.triggered to determine what has been most recently clicked (what triggered the callback)
    
    Uses previous function display_g_or_dt_buttons to determine whether all required selections (accounting for all cases regarding the value for domain and the amount of states and years specified) from the user are made, if not the graph is not displayed
    If all required selections are made, acquires applicable valid selections (due to callback remembering past selections) to then use in a final query to the irrigation database (uses final_query and execute_final_query functions found in the Irr_DB class defined in Irr_DB.py)
    Gets result from final query to the database and creates line graph or bar plot depending on earlier user choice by calling make_bar_plot or make_line_graph found in visualization.py, and graph is set to be displayed when the generate graph button is clicked

    Returns a plotly graph object, a dictionary (key and value are strings) to describe whether graph is displayed, and a boolean to describe whether the generate graph button is disabled (True for disabled, False for not disabled)
    '''
    
    style = {'display': 'inherit'} #by default the graph is shown (but its default value is {} so empty graph will appear), and the button to generate the graph is disabled
    disabled=False 

    if n_clicks==0 or ctx.triggered[0]['prop_id']!='graph-button.n_clicks': 
        #if the generate graph button hasn't been clicked at all, or isn't the most recent item interacted with by the user, 
        #the graph is not shown and the generate graph button is disabled
        style = {'display': 'none'}
        fig={}
        return fig, style,disabled

    if ctx.triggered[0]['prop_id']=='graph-button.n_clicks': 
        #once the generate graph button has been clicked (is the most recent action), the button should be disabled
        #the button resets once any earlier choice by the user that filters the data in the irrigation database is changed 
        disabled=True
    
    #calls the previous function display_g_or_dt_buttons because it already checks validity of every possible combination of domain, domain category, addiitonal data item, whether essential specifications have been defined by the user,
    #and whether targeted specifications have been made by the user (special case for line graph with having to display multiple states, and special case for bar plot when determining if states or years are on the x axis)
    check_button_conditions=display_g_or_dt_buttons(viz_type, state_id, commodity, domain, data_item, add_data_item, 
                                                    mult_dt_q, domain_category, year, stat_type, barax, line_n)
    ##returns a dictionary:
    #   either {'display': 'inherit'}, meaning valid specifications set by user 
    #   or {'display': 'none'} (both elements are the same) meaning invalid specifications/some haven't been filled out yet
    
    if check_button_conditions=={'display': 'none'}: ##this means a required selection from the user was not made, so the graph is not displayed
        style={'display': 'none'}
        fig={}
        return fig, style, disabled
    else: #all required data specifications made by the user are valid, 
        #however still need to access the valid domain categories if applicable, valid additional data items if applicable, and corresponding valid years since callback remembers past year selection for different data specifications

        valid_dc=[]
        valid_adt=[]
        ##if domain!=Total, need to access valid domain categories, and then related years
        if domain !="TOTAL" and len(domain_category)>=1:
            check_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}
            results=Irr_DB().get_domain_categories(check_dict, None)
            valid_dc=[i for i in domain_category if i in results]
            year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item], 'domain_category':valid_dc}
        
        ##if domain=Total and mult_dt_q==Multiple data items, need to access valid addtional data items and then related years
        elif domain == "TOTAL" and len(add_data_item)>=1 and mult_dt_q=="Multiple Data Items":
            check_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}
            results = Irr_DB().get_domain_categories(check_dict, mult_dt_q)
            valid_adt=[i for i in add_data_item if i in results]
            year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]+valid_adt}
        else: ##(domain==Total and mult_dt_q == One data item) 
            year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}

        ##retrieving valid years (which should exist because check_button_conditions!={'display': 'none'})
        year_results=Irr_DB().get_years(year_dict)
        valid_yrs=[i for i in year if i in year_results]

        year_dict['year']=valid_yrs ##adds valid years to existing dictionary checking for years (the last specification needed in the dictionary), 
        #so then this dictionary can be used in querying the irrigation database for the final results to be displayed on the final graphs
    
        lin_bool=encode_viz_type(viz_type) #encoding the user choice of visualizatin type to match the input reuired for Irr_DB().final_query, Irr_DB().execute_final_query
        if lin_bool == True:
            ##checking for conditions that would require line_n to be more than '' (such as "Multiple Lines" or "One Line")
            if ((len(state_id)>1) & (domain!="TOTAL") & (len(valid_dc)==1)) | ((len(state_id)>1)&(domain == 'TOTAL') & (mult_dt_q=="One Data Item")):
                ##line_n should exist -- now can be interpreted as s_multiple_or_one to fit input of Irr_DB().final_query and Irr_DB().execute_final_query
                final_query=Irr_DB().final_query(operation=stat_type, params=year_dict, s_multiple_or_one=line_n, yr_or_states=None, line_graph=True) #makes sql string for query
                final_results=Irr_DB().execute_final_query(final_query, year_dict, True) #executes query to irrigation database
                fig=make_line_graph(params=year_dict, y_data=final_results, operation=Irr_DB().which_statistic(stat_type), s_multiple_or_one=Irr_DB().set_group_by_line(line_n)) #makes line graph
                
            else: #line_n does not need to be more than '', so final query, its execution, and resulting line graph are created
                final_query=Irr_DB().final_query(operation=stat_type, params=year_dict, s_multiple_or_one=None, yr_or_states=None, line_graph=True)
                final_results=Irr_DB().execute_final_query(final_query, year_dict, True)
                fig=make_line_graph(params=year_dict, y_data=final_results, operation=Irr_DB().which_statistic(stat_type), s_multiple_or_one=None)
                
        
        else: #user specified Bar Plot

        ##checking for condiitons that would require barax to be more than '' (such as "States" or "Years")
            if ((len(state_id)==1) & (len(valid_yrs) ==1)) | ((len(state_id)>1) & (len(valid_yrs)>1)):
     
                if ((domain!="TOTAL") & (len(valid_dc)==1)) | ((domain == 'TOTAL') & (mult_dt_q=="One Data Item")):
                    ##barax should exist, can now be interpreted as bar_ax to fit format of Irr_DB().final_query and Irr_DB().execute_final_query
                    final_query=Irr_DB().final_query(operation=stat_type, params=year_dict, s_multiple_or_one=None, yr_or_states=barax, line_graph=False) 
           
                    final_results=Irr_DB().execute_final_query(final_query, year_dict, False)
    
                    fig=make_bar_plot(year_dict, encode_key_name_ys(barax), final_results, Irr_DB().which_statistic(stat_type))
    
                    return fig, style, disabled
    
            #a barax does not need to be more than '', so final query, its execution, and resulting bar plot are created
            final_query=Irr_DB().final_query(operation=stat_type, params=year_dict, s_multiple_or_one=None, yr_or_states=None, line_graph=False)
            final_results=Irr_DB().execute_final_query(final_query, year_dict, False)
            fig=make_bar_plot(year_dict, None, final_results, Irr_DB().which_statistic(stat_type))
    

        return fig,style, disabled


#Disable Save Figure button (and save figure) section (button already determined to be displayed or not in display_g_or_dt_buttons function)
@callback(Output('save-fig-button', 'disabled'),
        Input('save-fig-button', 'n_clicks'),
        Input('graph-button', 'n_clicks'),
        Input('graph','figure')
)

def display_save_fig_button(n_clicks:int, graph_clicks:int, output_fig:plotly.graph_objs._figure.Figure)->dict[str,str]:
    '''
    Determines whether the Save Figure button is disabled, and saves the graph figure if the button is clicked
    
    Takes in the number of times the save figure button has been clicked (an int n_clicks), the number of times the generate graph button has been clicked (an int graph_clicks),
    and the resulting figure made once user clicks the generate graph button (a plotly graph object called output_fig)
    
    Uses ctx.triggered to determine what most recently triggered the callback
    If the generate graph button has not been clicked (using graph_clicks), the save figure button is disabled
    If most recent click was the generate graph button, enables the save figure button to be clicked
    
    If most recent click was the save figure button, saves the figure (output_fig) as a png to a folder called figures in a folder called user_results, 
    names newly created figure using the number of times the save figure button has been clicked (n_clicks), so user should rename the file
    and button is then disabled. The figure is written to a static image by using kaleido, as described by plotly documentation. 
    
    Returns a boolean determining whether the save figure button is disabled (True) or not (False)
    '''
    
    disabled=False #by default button is not disabled
    
    if graph_clicks==0: #if the generate graph button has not been clicked, the save figure button is disabled
        disabled=True
        return disabled 
    elif ctx.triggered[0]['prop_id']=='save-fig-button.n_clicks': 
        #if the save figure button has been clicked, saves the resulting graph to a folder called figures in a folder called user_results, 
        # with the name dependent on how many times thesave figure button has been clicked in a session (user should rename this once file is created)
        write_image(output_fig,"user_results/figures/fig_"+str(n_clicks)+".png")
        disabled=True #disables save figure button
    elif (ctx.triggered[0]['prop_id']=='graph.figure'): 
        #this accounts cases in which the most recent item that triggered the callback was graph.figure, 
        # if any data specification was changed by the user, this is what triggers this callback (even if the generate graph button or save figure button wouldn't be clicked)
        #accounts for this to make it specifcally the user clicking on the generate graph button to enable the save figure button, and then only the user clicking the save figure button is what disables it
        disabled=True
        return disabled 

    return disabled


#Display Data Table, and whether the generate data table button is disabled, section

@callback(Output('table-container', 'children'),
        Output('table-container', 'style'),
        Output('data-table-button', 'disabled'),
        Input('data-table-button', 'n_clicks'),
        Input('viz-r', 'value'),
        Input('state-cl', 'value'),
        Input('com-dd', 'value'),
        Input('dom-dd', 'value'),
        Input('dt-dd', 'value'),
        Input('tot-dom-dt', 'value'),
        Input("mult-dt-r", 'value'), 
        Input('dc-cl', 'value'),
        Input('year-cl', 'value'),
        Input('statq-r', 'value'),
        Input('barxax-r', 'value'),
        Input('line-n-r', 'value')
        )
def display_table(n_clicks:int,
                    viz_type:str,
                    state_id:list[str],
                    commodity:str,
                    domain:str,
                    data_item:str, 
                    add_data_item:list[str],
                    mult_dt_q:str, 
                    domain_category:Union[list[str],list], 
                    year:list[str],
                    stat_type:str,
                    barax:str,
                    line_n:str)->Tuple[list, dict[str,str], dict[str,str]]:
    '''
    Determines whether data table holding the results from the query to the irrigation database, is displayed or not, 
    and whether the button the user clicks to generate the data table gets disabled

    The data table and its appropriate title are created here and act as the children to the item 'table-container', which is what actually determined to be displayed or not
    
    If data table is displayed, also displays a title over it as a html.Label matching the title of the corresponding graph to the user's data specifications (retrieved by the get_full_title function in visualization.py)
    
    To display the data table, writes the data table to a .csv with the get_statistics function defined in data_table.py, 
    the name of the file is uniquely identified with how many times the generate data table button has been clicked in a session (an int passed in as n_clicks), 
    and is saved a folder called tables within another folder called user_results (user should rename file once table is created)
    Then reads that .csv file to become a dash bootstrap table component to match the dash bootstrap theme, and the table is then added to 'table-container', along with the appropriate title 
    
    If the generate data table button has not been clicked for a particular combination of user selections, data table does not display
    If generate data table button has been clicked for a particular combination of user selections, it is disabled
    Uses ctx.triggered to determine what has been most recently clicked (what triggered the callback)
    
    Format of visualization is needed to be known in order to format the data table appropriately (passed in as a string viz_type)
    To construct the data table independent of making the corresponding graph, needs access to all previous user data selections.

    Takes in all of these additional parameters: the statistic type described by a string stat_type,
    the possible answer to the x axis question for bar plots (a string barax (default value is an empty string)), 
    the possible answer to the number of lines question for line graphs (a string line_n (default value is an empty string)),
    the state(s) selected as a list of strings state_id, year(s) as a list of strings year, commodity as a string commodity, domain as a string domain, data item as a string data_item,
    possible additional data items as a list of strings add_data_item, and possible domain categories as a list of strings domain_category
    
    Uses previous function display_g_or_dt_buttons to determine whether all required selections (accounting for all cases regarding the value for domain and the amount of states and years specified) from the user are made, if not the graph is not displayed
    If all required selections are made, acquires applicable valid selections (due to callback remembering past selections) to then use in a final query to the irrigation database (uses final_query and execute_final_query functions found in the Irr_DB class defined in Irr_DB.py)
    Gets result from final query to the database and constructs data table with get_statistics function defined in data_table.py
    
    
    Returns a list (one item a dash bootstrap table component, and the other a str for the label above the table), 
    and a dictionary (key and value are strings) that describes whether the container holding the data table and its title is displayed or not,
    and a boolean that describes whether the generate data table button is disabled (True for disabled, False for not disabled) 
    '''

    disabled=False #by default the button to generate the data table is enabled

    if ctx.triggered[0]['prop_id']=='data-table-button.n_clicks': #if the generate data table button has been clicked, the button is disabled
        disabled=True
    
    if n_clicks==0 or ctx.triggered[0]['prop_id']!='data-table-button.n_clicks': 
        #if the generate data table button hasn't been clicked, the html.div container meant to hold the data table is not displayed
        style = {'display': 'none'}
        children=[]
        return children, style, disabled
    #the generate data table button has now been clicked

    #calls the previous function display_g_or_dt_buttons because it already checks validity of every possible combination of domain, domain category, addiitonal data item, whether essential specifications have been defined by the user,
    #and whether targeted specifications have been made by the user (special case for line graph with having to display multiple states, and special case for bar plot when determining if states or years are on the x axis)
    check_button_conditions=display_g_or_dt_buttons(viz_type, state_id, commodity, domain, data_item, add_data_item, 
                                                    mult_dt_q, domain_category, year, stat_type, barax, line_n)
    ##returns a dictionary:
    #   either {'display': 'inherit'}, meaning valid specifications set by user 
    #   or {'display': 'none'} (both elements are the same) meaning invalid specifications/some haven't been filled out yet
    
    
    if check_button_conditions=={'display': 'none'}: ##this means a required selection from the user was not made, so the data table is not displayed
        style={'display': 'none'}
        children=[]
        return children, style, disabled


    else:  #all required data specifications made by the user are valid, 
        #however still need to access the valid domain categories if applicable, valid additional data items if applicable, and corresponding valid years since callback remembers past year selection for different data specifications
        valid_dc=[]
        valid_adt=[]
        ##if domain!=Total, need to access valid domain categories, and then related years
        if domain !="TOTAL" and len(domain_category)>=1:
            check_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}
            results=Irr_DB().get_domain_categories(check_dict, None)
            valid_dc=[i for i in domain_category if i in results]
            year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item], 'domain_category':valid_dc}
        
        ##if domain=Total and mult_dt_q==Multiple data items, need to access valid addtional data items and then related years
        elif domain == "TOTAL" and len(add_data_item)>=1 and mult_dt_q=="Multiple Data Items":
            check_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}
            results = Irr_DB().get_domain_categories(check_dict, mult_dt_q)
            valid_adt=[i for i in add_data_item if i in results]
            year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]+valid_adt}
        else: ##(domain==Total and mult_dt_q == One data item) 
            year_dict={'state_id':state_id,'commodity': [commodity], 'domain':[domain], 'data_item':[data_item]}

       
        ##retrieving valid years (which should exist because check_button_conditions!={'display': 'none'})
        year_results=Irr_DB().get_years(year_dict)
        valid_yrs=[i for i in year if i in year_results]

        year_dict['year']=valid_yrs #adds valid years to existing dictionary checking for years (the last specification needed in the dictionary), 
        #so then this dictionary can be used in querying the irrigation database for the final results to be displayed on the final graphs
    
        
        final_path=PATH_DT+str(n_clicks)+".csv" #constructs unique .csv file name for this paritcular session on the webpage

        lin_bool=encode_viz_type(viz_type) #encoding the user choice of visualizatin type to match the input required for Irr_DB().final_query, Irr_DB().execute_final_query
        
        if lin_bool == True:
            ##checking for conditions that would require line_n to be more than '' (such as "Multiple Lines" or "One Line")

            if ((len(state_id)>1) & (domain!="TOTAL") & (len(valid_dc)==1)) | ((len(state_id)>1)&(domain == 'TOTAL') & (mult_dt_q=="One Data Item")):
                ##line_n should exist -- now can be interpreted as s_multiple_or_one to fit input of Irr_DB().final_query and Irr_DB().execute_final_query
                final_query=Irr_DB().final_query(operation=stat_type, params=year_dict, s_multiple_or_one=line_n, yr_or_states=None, line_graph=True) #makes sql string to be final query to the irrigation database
                final_results=Irr_DB().execute_final_query(final_query, year_dict, True) #gets results from the query to the database 
                get_statistics(path=final_path, vals=final_results, params=year_dict, yr_or_states=None, s_multiple_or_one=Irr_DB().set_group_by_line(line_n), line_graph=True) #writes .csv file in appropriate format for line graph
            
            else: #line_n does not need to be more than '', so final query, its execution, and resulting data table in a .csv file are created
                final_query=Irr_DB().final_query(operation=stat_type, params=year_dict, s_multiple_or_one=None, yr_or_states=None, line_graph=True) #makes sql string to be final query to the irrigation database
                final_results=Irr_DB().execute_final_query(final_query, year_dict, True)#gets results from the query to the database 
                get_statistics(path=final_path, vals=final_results, params=year_dict, yr_or_states=None, s_multiple_or_one=None, line_graph=True) #writes .csv file in appropriate format for line graph

        
        else: #user specified Bar Plot as visualization type
 
        ##checking for condiitons that would require barax to be more than '' (such as "States" or "Years")
    
            if ((len(state_id)==1) & (len(valid_yrs) ==1)) | ((len(state_id)>1) & (len(valid_yrs)>1)):
              
                if ((domain!="TOTAL") & (len(valid_dc)==1)) | ((domain == 'TOTAL') & (mult_dt_q=="One Data Item")):
                    ##barax should exist, can now be interpreted as bar_ax to fit format of Irr_DB().final_query and Irr_DB().execute_final_query
                    final_query=Irr_DB().final_query(operation=stat_type, params=year_dict, s_multiple_or_one=None, yr_or_states=barax, line_graph=False)
                    final_results=Irr_DB().execute_final_query(final_query, year_dict, False)
        
                    get_statistics(path=final_path, vals=final_results, params=year_dict, yr_or_states=encode_key_name_ys(barax), s_multiple_or_one=None, line_graph=False)
                    
                    #obtains .csv file written with get_statistics
                    df = pd.read_csv(final_path)
                    style={'display': 'inherit'} #container holding data table will be displayed

                    
                    #obtaining table to be placed above the data table as an html.Label using get_full_title in visualization.py
                    #removes the line breaks that are within it
                    t_title=get_full_title(operation=Irr_DB().which_statistic(stat_type), params=year_dict, y_ax_title=year_dict['data_item'][0].split(' - ')[-1])
                    table_title=t_title.replace('<br>', ' ')
                    final_t_title=html.Label(table_title, style={'font-weight':'bold'}) #sets the label to be bold
                    table=dbc.Table.from_dataframe(df,  bordered=True, hover=True, index=False) #converts the data frame to a dash bootstrap table component (allows hovering, and gets rid of an index column)
                    children=[final_t_title, table] #adds the label and data table to the container holding them 

                    return children, style, disabled

            #a barax does not need to be more than '', so final query, its execution, and resulting data table is a .csv file are created
            
            final_query=Irr_DB().final_query(operation=stat_type, params=year_dict, s_multiple_or_one=None, yr_or_states=None, line_graph=False)
            final_results=Irr_DB().execute_final_query(final_query, year_dict, False)
            get_statistics(path=final_path, vals=final_results, params=year_dict, yr_or_states=None, s_multiple_or_one=None, line_graph=False)
 
        
        #obtains .csv file written with get_statistics (in case where barax could be '')
        df = pd.read_csv(final_path)
        style={'display': 'inherit'} #container holding data table will be displayed

        #obtaining table (when barax could be '') to be placed above the data table as an html.Label using get_full_title in visualization.py
        #removes the line breaks that are within it
        t_title=get_full_title(operation=Irr_DB().which_statistic(stat_type), params=year_dict, y_ax_title=year_dict['data_item'][0].split(' - ')[-1])
        table_title=t_title.replace('<br>', ' ')
        final_t_title=html.Label(table_title, style={'font-weight':'bold'}) #sets the label to be bold
        table=dbc.Table.from_dataframe(df,  bordered=True, hover=True, index=False) #converts the data frame to a dash bootstrap table component (allows hovering, and gets rid of an index column)
        children=[final_t_title, table] #adds the label and data table to the container holding them
        return children, style, disabled 

    
if __name__ == '__main__':
    # debug=True will show some errors on the webpage if they occur
    app.run(debug=True)
    
