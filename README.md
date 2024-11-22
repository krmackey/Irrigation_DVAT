# Irrigation Data Visualization and Analysis Tool
### Kirin Mackey

## Brief Description
Irrigation is an essential device in the U.S. agricultural industry, as it improves efficiency of farms and offers a way for states that have a dry and arid climate to sustain themselves. It has many components, such as energy, facilities and equipment, labor, practices, water, pumps, and wells. All of these components have further details, which can reveal the negative effects of irrigation such as the depletion of significant aquifers in the United States. On the other hand, these details can reveal sustainable practices and indicate future irrigation use, such as the amount of land irrigated with recycled water or the amount of land equipped for irrigation in a certain state. Learning about these details and finding statistics about them is an arduous task that involves searching through multiple research reports, especially if the user wants to look at a particular state or year.


In this project, I am going to make a tool in Dash where a user can visualize and analyze irrigation data from the United States Departmentment of Agriculture (USDA). By using this tool, a user can specify an individual or multiple states, the specific data they want to visualize or analyze, and what years the data to be visualized or analyzed reflects. The tool can be used to aid in creating research reports, serve as reference material for government officials, and be used in classroom settings for students studying environmental science and its associated public policies and economics.

The current status of my project is that there is a database containing cleaned data, and a series of functions querying it using values stored in a dictionary. Each function represents a decision the user will have to make, and can be represented with this [flowchart](writeup/Flowchart_of_decisions.png). The current functions account for the decisions regarding commodity and after. **They must be done in the order specified.**


A more detailed description of my project can be found in my writeup found here.


## Quick Start Guide
To explore my current code, first create a `data` folder, containing both files held in the `data` folder in this repository. They hold irrigation data collected by the USDA, and state abbreviation data used by the CDC. More information about them can be read about in the data description section of my project proposal found. You'll then also want to create a `src` folder containing the [irrigation_db.py](src/irrigation_db.py) file found in the `src` folder in this repository. This file builds a database, cleans the data from the USDA and CDC, and inserts the cleaned data into the database's relational tables. Lastly, download the [demo.ipynb](demo.ipynb) notebook to look at my functions with some documentation, as well as some examples (one of which directly references my writeup) with some instructions to run through. 

## Function Descriptions
### Functions in the DB class located irrigation_db.py

- `__init__(self, path_db: str, create: bool = False)`
    - constructor for the database that is found at `path_db`, a string object, specified by the user. If the user wishes to create the database, they can set the boolean `create` to `True`.
    - returns `None`
- `connect(self)`
    - sets up a connection to the database and enables foriegn key constraint checking
    - returns `None` 
- `close`
    - closes the connection to the database
- `run_query`
- `drop_all_tables`
    - drops the tState and tMain tables made with `prep_data`, `load_data`, and `load_table`
- `build_tables` ##get rid fo are you sure
- 
- `load_data`
- `load_table`
- `prep_data`

### Functions in demo.ipynb
- `get_commodity`
- `get_domains`
- `get_data_items`
- `get_domain_categories`
- `number_dt_question`
- `intermediate_domain_categories`
- `get_years`
- `which_statistic`
- `check_if_time_barplot`
- `final_query`
- `set_group_by`
- `execute_final_query`
