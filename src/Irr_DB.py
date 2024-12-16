import numpy as np
import sqlite3
import json
from src.irrigation_base import DB
from typing import Union


PATH_DB='data/irrigation.db'

class Irr_DB(DB):
    def __init__(self) -> None:
        '''
        Constructor for instance of the irrigation database

        Returns None
        '''
        super().__init__(path_db=PATH_DB, create=True) ##calls the constructor of the parent class DB, even if the path already exists, database will not be made again
        if self.exists == False: #if self.exists (specified in the parent class's constrcutor) is False, the database gets made, where the path is PATH_DB
            self.build_tables() #build_tables() and load_data() specified in parent class DB (found in irrigation_base.py)
            self.load_data()
        return

    def get_states(self) -> list[str]:
        '''
        Gets a list of states the user can select from 

        Returns a list of the available state_id's (in the form of the state's abbreviation)
        Each state_id is a string
        '''

        sql="""
        SELECT DISTINCT state_id FROM tMain
        ;"""
        states=self.run_query(sql, None).values.flatten().tolist()
        return states

    def get_commodity(self)-> list[str]:
        '''
        Queries tMain with run_query(sql, params) for distinct commodities (energy, facilities & equipment, labor, practices, pumps, water, and wells)
        Does not change based on previous user selections (state_id), so no params argument needed to be passed in

        Returns a list of the available commodities a user can choose from, each element is a string
        '''
        
        sql="""
        SELECT DISTINCT commodity FROM tMain
        ;"""
        comms=self.run_query(sql, None).values.flatten().tolist()
        return comms

    def get_domains(self, comm_params:dict[str,list[str]])->list[str]: 
        '''
        Gets the domains a user can pick (dependent on which commodity and states user has previously chosen)

        To be run after get_commodity()
        Uses a dictionary comm_params passed which its keys are strings and each value is a list of strings (only includes state_id and commodity at this step)
        Sets string that utilizes json and json trees to query the database with run.query(sql, params), makes it so that a list can be passed in as a parameter
    
        Returns a list of strings with each valid domain as an element
        '''
    
        my_params = json.dumps(comm_params)
        sql="""
        SELECT DISTINCT domain FROM tMain
        WHERE commodity IN (SELECT value FROM json_tree(:params) WHERE path = '$.commodity')
        AND state_id IN (SELECT value FROM json_tree(:params) WHERE path = '$."state_id"')
        ;"""
        avail_doms=self.run_query(sql, params={'params': my_params}).values.flatten().tolist()
        return avail_doms

    def get_data_items(self, dt_params:dict[str,list[str]])->list[str]: 
        '''
        Gets the data items a user can pick (dependent on the states, commodity, and domain previously chosen)
    
        To be run after get_domains(comm_params)
        Uses a dictionary dt_params passed in, its keys are strings and each value is a list of strings (only includes state_id, commodity, and domain at this step)
        Sets string that utilizes json and json trees to query the database with run.query(sql, params), makes it so that a list can be passed in as a parameter

        
        Returns a list of the valid data items where each element is a string
        '''
        
        my_params = json.dumps(dt_params)
        sql = """
        SELECT DISTINCT data_item FROM tMain
        WHERE commodity IN (SELECT value FROM json_tree(:params) WHERE path = '$.commodity')
           AND domain IN (SELECT value FROM json_tree(:params) WHERE path = '$.domain')
           AND state_id IN (SELECT value FROM json_tree(:params) WHERE path = '$."state_id"')
        ;"""
        dat_items=self.run_query(sql, params={'params': my_params}).values.flatten().tolist() 
        return dat_items

    
    def get_domain_categories(self, dc_params:dict[str,list[str]], mult_dt_q:Union[str, None])->Union[list[str], None]: 
        '''
        Gets possible domain categories the user can choose from (dependent on the states, commodity, domain, and data item previously chosen)
    
        To be run after get_data_items(dt_params)

        Uses a dictionary dc_params passed in which its keys are strings and each value is a list of strings (only includes state_id, commodity, domain, and data_item at this step)
        Checks whether the user specified domain as TOTAL. If they did, that means the only domain categories to choose from are named UNSPECIFIED, which is unhelpful.
        The number_dt_question() and intermediate_domain_categories(idc_params) functions are used to solve this issue.
        
        If the user wants to use only 1 data item compare states or years against each other, exits function and returns None
        If user wants to visualize multiple data items to each other, provides other data items with domain as TOTAL and use the same unit as the original data item chosen. They are also within the same commodity as the original data item chosen.
        
        If user did not specifiy domain as TOTAL, sets string that utilizes json and json trees to query the database with run.query(sql, params)


        If user selected domain=TOTAL, returns a list of the additional valid data items (each element stored as a string) or None in the case where user only wants to visualize one data item
        If user didn't select TOTAL as domain, returns a list of valid domain categories (each element stored as a string)
        '''
    
        if dc_params['domain'] != ['TOTAL']: 
            my_params = json.dumps(dc_params)
            sql = """
            SELECT DISTINCT domain_category FROM tMain
            WHERE commodity IN (SELECT value FROM json_tree(:params) WHERE path = '$.commodity')
               AND domain IN (SELECT value FROM json_tree(:params) WHERE path = '$.domain')
               AND data_item IN (SELECT value FROM json_tree(:params) WHERE path = '$."data_item"')
               AND state_id IN (SELECT value FROM json_tree(:params) WHERE path = '$."state_id"')
            ;"""
            dom_c_items=self.run_query(sql, params={'params': my_params}).values.flatten().tolist() 
            return dom_c_items
        else: ##handles the case in which user picked 'TOTAL' as the domain
            number_dt=self.number_dt_question(mult_dt_q)
            if number_dt == 'one': ##if user only wants to visualize/analyze one data item (and therefore compare across states or years)
                return ##returns None
            else:
                new_dat_i=self.intermediate_domain_categories(dc_params) 
                #returns a list of other possible data_items to compare to that also have 'TOTAL' as their domain
                return new_dat_i


    def number_dt_question(self, mult_dt_q:str) -> str:
        '''
        Called in get_domain_categories(dc_params) when handling case in which user had chosen domain = TOTAL

        In Dash App, the user will either choose 'Multiple Data Items" or "One Data Item" when asked if they want to visualize/analyze multiple data items or only one
        This choice is stored as mult_dt_q, which is a string
        To adhere to the condition in the if statement in the block handing the domain = TOTAL case, returns an encoded version of the user's previous choice to 'multiple' or 'one'
        
  
        Returns a string to be used in get_domain_categories(dc_params)
        '''
        encoder={'Multiple Data Items':'multiple', 'One Data Item':'one'}

        return encoder[mult_dt_q]

    def intermediate_domain_categories(self, idc_params: dict[str,list[str]])->list[str]:
        '''
        Will be called by get_domain_categories(dc_params) if the user specified domain as 'TOTAL' and the item returned by number_dt_question(mult_dt_q) is not equal to 'one'
        Looks at the the data item passed in with the dictionary idc_params (keys are string, each value is a list of strings) (only includes state_id, commodity, domain, and data_item at this step) and finds the units it uses
        Sets string that utilizes json and json trees to query the database with run.query(sql, params), based upon specifications set in idc_params as well as the units of the previously selected data item.

        Returns a list of valid data items (each element is a string)
        '''
        
        unit=idc_params['data_item'][0].split(' - ')[-1] #finds the unit of the data item specified in idc_params
        temp_params=idc_params.copy() #makes new dictionary replicating entries in idc_params
        temp_params['more_data_items']=[unit] #adds another element to the newly created dictionary in order to query the database for data items that use the same unit as the initial data item selected
        my_params = json.dumps(temp_params)
        sql = """
        SELECT DISTINCT data_item FROM tMain
        WHERE commodity IN (SELECT value FROM json_tree(:params) WHERE path = '$.commodity')
            AND state_id IN (SELECT value FROM json_tree(:params) WHERE path = '$."state_id"')
            AND domain IN (SELECT value FROM json_tree(:params) WHERE path = '$.domain')
            AND data_item NOT IN (SELECT value FROM json_tree(:params) WHERE path = '$."data_item"')
            AND data_item LIKE CONCAT('%', (SELECT value FROM json_tree(:params) WHERE path = '$."more_data_items"'))
            
        ;"""
        dat_c_items=self.run_query(sql, params={'params': my_params}).values.flatten().tolist() 
        return dat_c_items


    def get_years(self, year_params:dict[str, list[str]])-> list[str]:
        '''
        Gets possible years the user can choose from, dependent on the states, commodity, domain, data item(s), and possible domain category(ies) previously chosen by user.
        These previous selections are passed in an argument and storde as year_params, where the keys are string and each associated value is a list of strings

        Because of json tree structure and IN() sql operator that essentially acts as the OR operator, found that run_sql_query(sql, params), where params=year_params, would return years that would be valid for a state, even if it wasn't valid for another
        The same can be said about keys that have values that are lists with more than a length of one (possibly data item and domain category depending on user selection)
        
        To combat this issue: 
            for each list (value associated with a key in the dictionary year_params) with multiple items:
                finds valid years for each entry in those lists, and then finds years common to all those entries. This is done in particular for the list detailing the states chosen by the user,
                    and the cases where the user selected more than one domain category specified, or more than one data item
            Once finding years common to all entries in each of those lists, compares the lists of valid years to each other if needed (when more than one data item or domain category selected) and find the common years between those
        
        To find the valid years for values that are lists with more than 1 element in year_params, uses the function each_choice_year(key_name, year_params)  
        If needed to compare multiple "valid year" lists to each other, uses set intersection to find the common years between all lists  
        If there aren't multiple "valid year" lists to compare to each other, still looks at the valid years common to all states specified in year_params['state_id]
        Sorts the final "valid year" list in ascending order, as once becoming sets the order of list elements does not matter. This is done to match up the labels of years to the final results, as SQL presents results by default in ascending order 


        Returns a list of valid years (each element is stored a string)
        '''
        
        by_state_year=set(self.each_choice_year('state_id', year_params)) ##gets valid years common to all states specified in year_params['state_id'], stored as a set of strings
    
        if len(year_params['data_item'])>1: ##indicates that the user wants to compare data items across states or years
    
            by_dt_year=set(self.each_choice_year('data_item', year_params)) ##gets valid years common to all data items specified, stored as a set of strings
    
            year_set=by_state_year.intersection(by_dt_year) ##getting the valid years across both states and data_items
        elif 'domain_category' in year_params.keys(): ##This only occurs when len(data_item)==1 
            if len(year_params['domain_category'])>1: #have to check existence of domain_category in the keys of year_params before checking for length of its assocated value
                by_dc_year=set(self.each_choice_year('domain_category', year_params)) #gets valid years for each domain_category specified, stored as a set of strings
                year_set=by_state_year.intersection(by_dc_year) #getting the valid years across both states and domain categories
            else:
                year_set=by_state_year
        else:
            year_set=by_state_year
        return_yr_list=list(year_set) #converts set to list
        return_yr_list_sort = sorted(return_yr_list, key=int) #sorts the list of strings as if they were integers
        return return_yr_list_sort

    def each_choice_year(self, key_name: str, year_params: dict[str, list[str]]) -> list[str]:
        '''
        Called by get_years(year_params)
        Gets valid years common to all entries in a list of strings, which is stored as value in year_params
        To look at an individual value (list) in year_params, takes in a key_name as string
        For each entry in the year_params[key_name], finds valid years
        Then determines the years that are common to all of those entries by utilizing numpy.unique()
        
        Returns a list of valid years, where each element is a string
        '''


        stored_years=[]
        for i in year_params[key_name]: #looks at list stored at key name in the dictionary year_params
            temp_params=year_params.copy()
            temp_params[key_name]=[i] #resets the value associated with the key name to an individual item
            my_params = json.dumps(temp_params)
            sql = """
            SELECT DISTINCT year FROM tMain
            WHERE commodity IN (SELECT value FROM json_tree(:params) WHERE path = '$.commodity')
               AND domain IN (SELECT value FROM json_tree(:params) WHERE path = '$.domain')
               AND data_item IN (SELECT value FROM json_tree(:params) WHERE path = '$."data_item"') --NEED DOUBLE QUOTES HERE
               AND state_id IN (SELECT value FROM json_tree(:params) WHERE path = '$."state_id"')
            ;"""
            if 'domain_category' in temp_params.keys(): 
                ##in the case the user selected "TOTAL" as the domain, and therefore has items for 'domain category'
                sql=sql[:-1]+"""AND domain_category IN (SELECT value FROM json_tree(:params) WHERE path = '$."domain_category"');"""
            avail_years=self.run_query(sql, params={'params': my_params})['year'].values ##recieves a numpy array
            stored_years+=avail_years.tolist() ##adds a list version of the numpy array to stored_years
        stored_years_np=np.array(stored_years) ##includes all years that are valid for at least one item stored in year_params[key_name]
        unique_years=np.unique(stored_years_np) ##finds the unique entries in the array stored_years_np
        all_years= stored_years_np.tolist()##converts the numpy array of possible years for any entry in year_params[key_name] to a list 
        unique_years=unique_years.tolist() #converts the array of unique years to a list
        return_yrs=[] 
        for i in unique_years: 
            #to be valid, the amount of times a year in unique_years occurs in all_years has to be the same as the amount of items in year_params[key_name],
            # This means the particular year i in unique_years is valid for each entry in the list year_params[key_name] 
            if all_years.count(i) ==len(year_params[key_name]):
                return_yrs+=[i]
        return return_yrs


    def which_statistic(self, user_click:str) -> str:
        '''
        In the final Dash app, user will click a button to select the statistic they want to visualize .
        The names of these buttons corresponds with the keys specifed in the dictionary encoding 
        
        This converts that selection (stored as string in user_click) to its correspondign SQL aggregate function (needed to sufficently build the final sql query in final_query(operation, params, line_graph))
    
        Returns a string
        '''
        
        encoding={'Minimum':'MIN', 'Maximum':'MAX', 'Average': 'AVG', 'Sum':'SUM'}
        return encoding[user_click]

    

    def execute_final_query(self, query:str, params: dict[str,list[str]], line_graph: bool=False) -> Union[list[float], list[list[float]]]:
        '''
        Queries the database for the values to be visualized or analyzed, called after final_query(operation, params, s_multople_or_one, yr_or_states, line_graph)
        Uses the string output of final_query, passed as query in run_query(query, params). Also uses params, a dictionary where each key is a string and each value is a list of strings, that holds all of the user's data specifications
        
        When line_graph is False (meaning user wants a bar plot), returns a list of floats 
        When line_graph is True (meanign user wants a line graph), returns a list of lists of floats, each the length of how many years specified by the user, 
            to adhere to how traces are added using plotly.graph_objects to make a line graph
        '''
    
        
        my_params = json.dumps(params)
        results=self.run_query(query, params={'params': my_params})
        if line_graph: 
            ##this means the values in the "value" column of the results are organized where there is an entry for each year, 
            #for each set fo specifications set by the user (state_id, commodity, domain, data item(s), domain category(ies))
            #For instance, if 2013, 2018, 2023 were the years specified in params['year'], there would be a row for each of those years with the same other specifications otherwise
            #They then need to be grouped together in a list so the other specifications can be read as one line in the final line graph
            
            intermed=results.iloc[:,-1].values.tolist() #looks at value column in the results of run_query(query, params)
            cutoff=len(params['year']) ##gets the amount of years specified by the user
            yr_based_results=[]
            count=0
            while count < len(intermed):
                yr_based_results+=[intermed[count:count+cutoff]] ##groups a set of years using the same  specifications, and adds them as a list to existing list yr_based_results
                count+=cutoff #sets new index to start from 
            return yr_based_results
        return results.iloc[:,-1].values.tolist()##gets last column detailing the results associated with the operation performed 

    def final_query(self, operation:str, params:dict[str,list[str]], s_multiple_or_one:Union[str, None], yr_or_states:Union[str, None],line_graph=False) -> str:
        """
        Constructs a string detailing the final query to the database 
        
        Gets a value using the aggregation method (MAX, MIN, SUM, AVG) chosen by the user (it is named operation here and is the full name of the method, ex. Minimum) 
    
        Looks at the amount of items stored at each key in the dictionary params(keys are strings, each value is a list of strings) and the type of visualization (line_graph either True or False) 
        and sets the group by accordingly,
        If necessary, looks at further specifications set by user that are needed to properly set the group by:
            If the user chose multiple states and multiple years for line graphs, looks further with set_line_state_groupby(params['state_id'],s_multiple_or_one), 
            where s_multiple_or_one is either "Multiple Lines" or "One Line" or None

            If the user chose multiple states and multiple years, or one state and one year, looks further with set_group_by_bar(params:dict[str,list[str]], yr_or_states:str=None)
            where yr_or_states is either 'States' or 'Years' or None
    
        Returns a string to be used as query in execute_final_query(query, params, line_graph)
        """
        operation=self.which_statistic(operation) ##gets sql operation equivalent to user selection (Minimum, Maximum, Sum, Average), which is passed in as operartion, in final Dash app
        start="SELECT 1.*"+operation+"(value) from tMain"
        
        middle="""
        WHERE commodity IN (SELECT value FROM json_tree(:params) WHERE path = '$.commodity')
               AND domain IN (SELECT value FROM json_tree(:params) WHERE path = '$.domain')
               AND data_item IN (SELECT value FROM json_tree(:params) WHERE path = '$."data_item"') --NEED DOUBLE QUOTES HERE
               AND state_id IN (SELECT value FROM json_tree(:params) WHERE path = '$."state_id"')
               AND year IN (SELECT value FROM json_tree(:params) WHERE path = '$.year') 
        """
        if 'domain_category' in params.keys(): ##taking into account cases where user didn't pick "TOTAL" as domain, so domain_category must exist in the keys and additional querying needs to be done
            middle=middle+"""AND domain_category IN(SELECT value FROM json_tree(:params) WHERE path = '$."domain_category"')"""
        if line_graph: ##if the user specified a line graph, the sql aggregation method chosen must be grouped by year at the minimum.
            if len(params['data_item'])>1: ##accounts for case where user chose domain = TOTAL, and chooses multiple data items to compare
                suffix="GROUP BY data_item,year;"
            elif 'domain_category' in params.keys():
                if len(params['domain_category'])>1:##accounts for case where user didn't choose domain = TOTAL, and chooses multiple domain categories within 1 data item to compare
                    suffix="GROUP BY domain_category, year;"
                else: ##this means user only chose one domain category
                    suffix=self.set_line_state_groupby(params['state_id'],s_multiple_or_one)      
            else: ##this means the user only chose one data item and domain=TOTAL
                suffix=self.set_line_state_groupby(params['state_id'], s_multiple_or_one)
        else: ##user specified "Bar Plot" for visualization type
            if len(params['data_item'])==1:
                if 'domain_category' in params.keys(): 
                    if len(params['domain_category'])==1:
                        ##only one data item and domain category chosen, so years and states specified by user must be investigated next to decide what is on the x axis
                        group_by=self.set_group_by_bar(params, yr_or_states)
                    else: #multiple domain_categories so domain category is along the x axis
                        group_by='domain_category'
                else: ##only one data item chosen and domain=TOTAL, so years and states specified by user must be investigated next ot decide what is on the x axis
                    group_by=self.set_group_by_bar(params, yr_or_states)     
            else: ##multiple data items selected so data item is along the x axis
                group_by='data_item'    
            suffix="GROUP BY "+group_by+';'    
        new=start+middle+suffix
        return new 

    def set_line_state_groupby(self, state_id_list:list[str], s_multiple_or_one: str=None)->str:
        '''
        Gets called by final_query(operation, params, s_multiple_or_one, yr_or_states, line_graph)

        It is triggered when line_graph = True and the user only specified one data item if domain=TOTAL, or one data item and one domain category is domain isn't TOTAL
        In theses instances, the final group by statement in the final sql query depends on the amount of states specified in the list state_id_list (each element is a string)
        Takes in a string s_multiple_or_one that is either 'Multiple' or 'One' if they chose multiple states
        If the user chose only one state, then that means s_multiple_or_one=None and there will be only 1 line on the bar graph 

        Returns the entire group by statement as a string to be used in the final query in the case the user wants a line graph as a string, and only chose one data item and possibly one domain category to be visualized
        '''
        if len(state_id_list)>1:  ##state_id_list is equivalent to params['state_id']
            ##if more than one state is chosen, and the user only chose 1 data item and 1 domain category, 
            # need to know if the user wants to have multiple lines, each line representing a state, or one line
            # showing the aggregation method done over all the states
            check_combine=self.set_group_by_line(s_multiple_or_one) #returns 'multiple' if the user chose 'Multiple Lines' or 'one' if hte user chose 'One Line' for how they want their line graph to be formatted
            ##the user should have specified if they want Multiple Lines or One Line for their line graph if they have met all of the previosu conditions, 
        else:
            check_combine='one' ##if user chose only one state, this means they only want one line on the line graph
        if check_combine == 'multiple': #indicates user chose 'Multiple Lines' for how they want states represented on final graph
            suffix="GROUP BY state_id, year;"
        else: #check_combine == 'one' so user chose 'One Line' as s_mutliple_or_one in the case they chose multiple states, or only specified one state
            suffix="GROUP BY year;"

        
        return suffix


    def set_group_by_line(self, user_click:str)->str:
        '''
        Gets called by set_line_state_groupby(state_id_list:list[str], s_multiple_or_one: str), where user_click is a string and is the s_multiple_or_one in set_line_groupby
        
        Uses encoder that changes user_click (Multiple Lines or One Line), which describes how the user wants their specified state(s) to be reflected on the final bar graph
       
        Returns a string that is used in a conditional in set_line_state_groupby 
        '''
        encoder={'Multiple Lines':'multiple', 'One Line':'one'}
        
        return encoder[user_click]



    def set_group_by_bar(self, params:dict[str,list[str]], yr_or_states:str=None)->str:
        """
        Gets called by final_query(operation, params, s_multiple_or_one, yr_or_states, line_graph) where line_graph = False, so the desired visualization is a bar plot
        
        yr_or_states is not None when user either specifies multiple years and multiple states, or one year and one state. In these instances, the x-axis can be either 
            so yr_or_states is either 'States' or 'Years' that the user clicks on in the final dash app. The value in yr_or_state is then used to determine the column in the database that is used int he group by statement in the final sql query
        yr_or_states is None when the user specifies multiple years and one state (wants to compare states), or multiple states and one year (wants to compare years)

        Uses the dictionary params (keys are strings, each value is a list of strings) holding all the data specifications set by the user and looks at the length of the lists associated with the keys 'year' and 'state' if yr_or_states = None

        Returns a string indicating the column in the database to perform the sql aggregate function over (state_id or year)
        """
 
        if yr_or_states == None:
            if (len(params['year'])>1) & (len(params['state_id'])==1): ##indicates user wants to compare years
                group_by='year'
        
            else:  ##other instance is when len(params['state_id]>1 and len(params['year'])==1), indicating user wants to compare states. If both of them have over a length of 1, or exactly 1, yr_or_states !=None
                group_by='state_id'
            return group_by
        else: #yr_or_states has a value, so user specified only 1 year and 1 state, or multiple years and multiple states, 
            group_by=self.check_if_time_barplot(yr_or_states)##looks at yr_or_states and returns a column name to be in the group by statement in the final sql query(year for Years, or state_id for States)
            return group_by



    def check_if_time_barplot(self, user_click:str)->str: 
        """
        Called by set_group_by_bar(params, yr_or_states) where user click is a string that is the same as yr_or_states in set_group_by_bar
        user_click (a string) is either 'States' or 'Years' and is translated into a column name that is included in the irrigation database
        
        Returns the column name of the database as a string 
        """

        encoder={'States':'state_id', 'Years':'year'}
        return encoder[user_click]
   