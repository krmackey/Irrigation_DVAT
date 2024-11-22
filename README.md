# Irrigation Data Visualization and Analysis Tool
### Kirin Mackey

## Brief Description of Project
Irrigation is an essential device in the U.S. agricultural industry, as it improves efficiency of farms and offers a way for states that have a dry and arid climate to sustain themselves. It has many components, such as energy, facilities and equipment, labor, practices, water, pumps, and wells. All of these components have further details, which can reveal the negative effects of irrigation such as the depletion of significant aquifers in the United States. On the other hand, these details can reveal sustainable practices and indicate future irrigation use, such as the amount of land irrigated with recycled water or the amount of land equipped for irrigation in a certain state. Learning about these details and finding statistics about them is an arduous task that involves searching through multiple research reports, especially if the user wants to look at a particular state or year.


In this project, I am going to make a tool in Dash where a user can visualize and analyze irrigation data from the United States Departmentment of Agriculture (USDA). By using this tool, a user can specify an individual or multiple states, the specific data they want to visualize or analyze, and what years the data to be visualized or analyzed reflects. The tool can be used to aid in creating research reports, serve as reference material for government officials, and be used in classroom settings for students studying environmental science and its associated public policies and economics.

The current status of my project is that there is a database containing cleaned data, and a series of functions querying it using values stored in a dictionary. Each function represents a decision the user will have to make, and can be represented with this [flowchart](writeup/Flowchart_of_decisions.png). The current functions account for the decisions regarding commodity and after. **They must be done in the order specified.** In my final project, these functions will be called in the background when a user clicks a button, checks a box in a checklist, or selects an option in a dropdown list. Whenever the user performs these actions, a dictionary will be updated.


A more detailed description of my project can be found in my writeup found [here](writeup/Revised_Project_Proposal.pdf).


## Quick Start Guide
To explore my current code, first create a `data` folder, containing both files held in the `data` folder in this repository. They hold irrigation data collected by the USDA, and state abbreviation data used by the CDC. More information about them can be read about in the data description section of my project proposal found [here](writeup/Revised_Project_Proposal.pdf). You'll then also want to create a `src` folder containing the `irrigation_db.py` file found in the `src` folder in this repository and linked [here](src/irrigation_db.py). This file builds a database, cleans the data from the USDA and CDC, and inserts the cleaned data into the database's relational tables. Lastly, download the `demo.ipynb` notebook (linked [here](demo.ipynb) )to look at my functions with some documentation, as well as some examples (one of which directly references my writeup) with some instructions to run through. 

## Extended Function Descriptions
### Functions in the DB class located in [`irrigation_db.py`](src/irrigation_db.py)

- `__init__(self, path_db: str, create: bool = False)-> None`
    - Constructor for the database that is found at `path_db`, a string object, specified by the user. If the user wishes to create the database, they can set the boolean `create` to `True`.
    - Returns `None`
- `connect(self)->None`
    - Sets up a connection to the database and enables foriegn key constraint checking
    - Returns `None` 
- `close(self)->None`
    - Closes the connection to the database
    - Returns `None`
- `run_query(self, sql:str)-> pd.DataFrame`
    - Sets up connection to database
    - Performs `pd.read_sql`
    - Returns results from the query in a pandas DataFrame
- `drop_all_tables(self)-None`
    - Drops the `tState` and `tMain` tables made with `prep_data`, `load_data`, and `load_table`
    - Returns `None`
- `build_tables(self)->None` 
    - Drops the `tState` and `tMain` tables made with `prep_data`, `load_data`, and `load_table` in case they already exist
    - Builds empty relational table `tMain` with primary keys: `state_id`, `year`, `commodity`, `data_item`, `domain`, and `domain_category`. All columns are of the text type except a `value` column that is numeric because some entries in the USDA irrigation data had decimal points
    - Builds empty relational table `tState` with `state_id` as primary key. All columns are of the text type.
    - Returns `None`
- `load_data(self)->None`
    - Inserts preprocessed data created in `prep_data` into the appropriate relational tables (`tMain` or `tState`) using sql and by calling `load_table`
    - Returns `None`
- `load_table(self,sql:str, data:pd.DataFrame)->None`
    - Takes in a sql query represented stored as string named `sql`
    - Uses the `to_dict` function in pandas to convert the pandas DataFrame passed in into a dictionary and inserts the data row by row into the table specified by the sql query stored as `sql`
    - Returns None
- `prep_data(self)->dict[str, pd.DataFrame]`
    - Reads the data stored in the Irrigation_Data.csv file
    - Drops all unnecessary columns and rows that have either no information or information that does relate to this project's purpose
    - Casts columns to their proper types
    - Cleans the 'Domain Category' and 'Data Item' columns in the dataframe to remove redundant information across columns. More specific information on what is removed can be found in comments in the irrigation_db.py file 
    - Returns a dictionary with its keys as strings, and their corresponding values as pandas DataFrames

### Functions in `demo.ipynb`
- `get_commodity()->np.ndarray[np.ndarray[str]]`
    - Queries `tMain` for distinct commodities (energy, facilities & equipment, labor, practices, pumps, water, and wells)
    - Returns a multidimensional numpy array giving the names of the commodities a user can choose from
- `get_domains(comm_params:dict[str,list[str]])->np.ndarray[str]`
    - To be run after `get_commodity`
    - Uses a dictionary `comm_params` passed in which its keys are strings and each value is an array of strings (only includes `state_id` and `commodity` at this step)
    - Sets string that utilizes json and json trees to query the database
    - Uses `pd.read_sql` with the query
    - Returns a multidimensional numpy array giving the names of the domains a user can choose from (dependent on their choice of commodity)
- `get_data_items(dt_params:dict[str,list[str]])->np.ndarray[np.ndarray[str]]`
    - To be run after `get_domains`
    - Uses a dictionary `dt_params` passed in which its keys are strings and each value is an array of strings (only includes `state_id`, `commodity`, and `domain` at this step)
    - Sets string that utilizes json and json trees to query the database
    - Returns a multidimensional numpy array giving the names of the data items a user can choose from (dependent on their choice of commodity and domain)
- `get_domain_categories(dc_params:dict[str,list[str]])->Union[np.ndarray[np.ndarray[str]], None]`
    - To be run after `get_data_items`
    - Uses a dictionary `dc_params` passed in which its keys are strings and each values is an array of strings (only includes `state_id`, `commodity`, `domain`, and `data_item` at this step)
    - Checks whether the user specified `domain` as TOTAL. If they did, that means the only domain categories to choose from are named UNSPECIFIED. The `number_dt_question` and `intermediate_domain_categories` functions to solve this issue and either exits this function (if the user wants to use only 1 data item to compare states or years against each other), or provides other data items with `domain` as TOTAL that use the same units as the original data item chosen. They are also within the same commodity as the original data item chosen.
    - Otherwise sets string that utilizes json and json trees to query the database and uses it in `pd.read_sql`
    - Returns either a multidimensional numpy array giving the names of the domain categories, data items a user can choose from (dependent on their choices of commodity, domain, and data item), or `None` (in which the user want to use only 1 data item and they set the domain to TOTAL)
- `number_dt_question() -> str`
    - Called in `get_domain_categories` when handling case in which user had chosen domain = TOTAL
    - Utilizes `input()` function and used in the event the user specified `domain` as 'TOTAL'
    - Asks whether the user only wants one data item to analyze (and therefore look at the relationships between states or years) or multiple data items
    - The user needs to press enter after either typing in 'multiple' or 'one' (but without the quotation marks)
    - Will likely turn into some sort of encoding function, called when a user clicks a button (Multiple or One)
    - Returns the user input as a string
- `intermediate_domain_categories(idc_params: dict[str,list[str]])->np.ndarray[np.ndarray[str]]`
    - Will be called by `get_domain_categories` if the user specified `domain` as 'TOTAL'
    - Looks at the the data item passed in with the dictionary `idc_params` (only includes `state_id`, `commodity`, `domain`, and `data_item` at this step) and find the units it uses
    - Sets string that utilizes json and json trees to query the database based upon specifications set in `idc_params` as well as the units of the previously selected data item.
    - Runs `pd.read_sql` and returns a multidimensional numpy array of valid data items (dependent on the user's previous choices of commodity, domain, and data item) to `get_domain_categories` 
- `get_years(year_params:dict[str, list[str]])-> list[str]`
    - To be run after `get_domain_categories`
    - For each state in `year_params`, the database is queried following all other specifications found in `year_params`, which a dictionary in which the keys are string and value is a list of strings. The keys at this point include `state_id`, `commodity`, `domain`, `data_item`, and potentially `domain_category` depending on the actions performed in `get_domain_categories`. The query returns the available years and adds them to a list.
    - It then looks at how many times a unique year appeared in this list, and will be returned to the user if the amount of times matches how many states were specified in `state_id` in the passed in dictionary.
    - Currently returns the valid years in the form of a list of lists, which hold strings. This may change to a np.ndarray to match the other functions described above.
- `which_statistic()-> str`
    - Meant to be an encoder to a button in the final tool, where a user picks minimum, maximum, average, or sum to be the statistic they desire to visualize.
    - The sql represenation of these functions will be returned as strings (either MIN, MAX, AVG, or SUM).
    - Essentially dictates the `operation` argument the user passes in to the `final_query` function described below.
- `check_if_time_barplot()-> str`
    - Called in the case the user either has multiple entries or 1 entry correponding to both `state_id` and `year`.
    - Asks the user whether they are comparing states or years, meaning which one of them would be on the x axis in a visualization
    - Used to aid in the `final_query` and `set_group_by` functions, but in final version will likely be some sort of encoding function called when a user clicks a button (States or Years)
    - The user right now needs to press enter after either typing in 'states' or 'years' (but without the quotation marks)
- `final_query(operation:str, params:dict[str,list[str]], line_graph=False)-> str`
    - Makes the final query using json trees to the database,  which would get a list of values using the aggregation method (max, min, avg, sum) chosen by the user (it is named `operation` here). 
    - Looks at the amount of items stored at each key in the dictionary passed in as `params` and whether the user wants a line graph. It then sets the group by statement in the final sql query accordingly. It does so by storing the dictionary key name in a variable called `group_by`. The `params` dictionary at this point should have the keys `state_id`, `commodity`, 'domain`, 'data_item`, possibly `domain_category`, and `year`.
    - Calls `set_group_by` in the event `group_by` needs to be either `state_id` or `year`
    - Returns a string with the final query to be made to the database in `execute_final_query'
- `set_group_by(params:dict[str,list[str]])->str`
    - Called by `final_query` and looks at the dictionary passed in as `params`
    - Looks at the amount of items stored with the keys `state_id` and `year` and sets them accordingly (1 state vs many years indicates group by on `year`, 1 year vs many states indicates group by on `state_id`)
    - If there is only one state listed and one year listed, or mutliple years and multiple years listed `check_if_time_barplot` is called to then set what `group_by` should be in the final query
    - Returns the string representation of the dictionary key to be used in the group by statement in the final query
- `execute_final_query(query:str, params: dict[str,list[str]])-> list[float]`
    - To be run after `final_query`, as its input is `final_query`'s output (named `query`)
    - Utilizes json objects and the query using json trees to then pass in to `pd.read_sql`
    - Returns a list of floats with the values corresponding to the specifications set in the dictionary the user builds, as well as the operation they specify. The dictionary is named `params` here and should have the keys `state_id`, `commodity`, 'domain`, 'data_item`, possibly `domain_category`, and `year`. The order of these values is determined by the list of values stored in the key name used as group by in the final query
