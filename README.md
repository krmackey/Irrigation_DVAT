# Irrigation Data Visualization and Analysis Tool (DVAT)
### Kirin Mackey

## Brief Description of Project
Irrigation is an essential device in the U.S. agricultural industry, as it improves efficiency of farms and offers a way for states that have a dry and arid climate to sustain themselves. It has many components, such as energy, facilities and equipment, labor, practices, water, pumps, and wells. All of these components have further details, which can reveal the negative effects of irrigation such as the depletion of significant aquifers in the United States. On the other hand, these details can reveal sustainable practices and indicate future irrigation use, such as the amount of land irrigated with recycled water or the amount of land equipped for irrigation in a certain state. Learning about these details and finding statistics about them is an arduous task that involves searching through multiple research reports, especially if the user wants to look at a particular state or year.

This project creates a tool in Dash where a user can visualize and analyze irrigation data from the United States Departmentment of Agriculture (USDA). By using this tool, a user can specify an individual or multiple states, the specific data they want to visualize or analyze, and what years the data to be visualized or analyzed reflects. After all specifications are made, the user can create the corresponding interactive graph, save the graph as a .png, and create the corresponding data table (both shown in the tool and saved as .csv file).

The tool can be used to aid in creating research reports, serve as reference material for government officials, and be used in classroom settings for students studying environmental science and its associated public policies and economics.

A more detailed description of the project can be found [here](writeup/Revised_Project_Proposal.pdf). Further documentation on how the code works can be found in each .py file (`main_dash.py` and all files in the `src` folder).
## Prerequisties
- Python 3.13 or higher

## Quick Setup Guide
To open this tool, follow the steps below:

1. Clone this repository to obtain all required data and code files by running the below on your terminal:
    ```bash
    git clone https://github.com/krmackey/Irrigation_DVAT.git
    ```
2. Install all the dependencies required for this project by running the below on your terminal (may instead use `pip3` rather than `pip` if applicable):
   ```bash
    pip install -r requirements.txt
    ```
3. Run `main_dash.py` in your terminal once you navigate to the cloned repository on your local machine (may instead use `python3` rather than `python` if applicable):
   ```bash
    python main_dash.py
   ```
## How to Use Tool
1. Choose the type of visualization you want (Bar Plot or Line Graph). If you only want a data table, pick the type of visualization that would reflect your desired results. Are you looking at change over time or comparing distinct groups of data to each other?
2. Choose the state(s) you want your final graph and/or data table to reflect. You can pick up to 5.
3. Choose what commodity of irrigation (energy, facilities & equipment, labor, practices, pumps, water, wells) you want to analyze/visualize.
4. Choose what domain (available choices you can explore are dependent on the type commodity and state(s) you chose) of the irrigation data you want to analyze/visualize.
5. Choose what data item (available choices you can explore are dependent on the state(s), commodity, and domain you chose) of the irrigation data you want to analyze/visualize.
6. If you chose TOTAL as the domain, you will be asked if you want to visualize/analyze only one data item, or multiple data items.
   * If you chose 'Multiple Data Items' you will be presented with a checklist to choose up to 4 more data items you want to visualize/analyze alongside the initial one you chose. They use the same units as the first data item you chose, apply to the same commodity you chose, apply to the same state(s) you chose, and also have their domain as TOTAL,
   * If you chose 'One Data Item' you will be presented with the next choice available, years you want your final graph/data table to be reflective of
7. If you didn't choose TOTAL as the domain, you will be presented with a checklist (options you can explore are dependent on the state(s), commodity, domain, and data item you have already chosen) to choose up to 5 domain categories
8. Choose the year(s) you want the data you are going to visalize/analyze to be reflective of. The years given as options and the amount of them are dependent on your previous choices of state(s), commodity, domain, data item(s), and possibly domain category(ies).
9. Choose the statistic you wish the data to represent (Minimum, Maximum, Average, Sum).
    * If you chose bar plot, 3 states, 3 domain categories, 3 years, and the Average option, each bar displayed will be each domain category, with the value being the average value of that domain category for the 3 states and 3 years you chose.
    * If you chose line graph, 2 states, set the domain as TOTAL, chose 3 total data items, and the Sum option, each line displayed will be each data item, and each value for each year is the sum of values for that data item for the 2 states you chose.
10. Additional questions may appear if you either chose 1 data item and 1 domain category (domain selected was not TOTAL), or 1 data item (domain selected was TOTAL and additionally selected One Data Item when asked about multiple data items). The amount of states and years you previosly selected also determines whether you get asked these questions.
    * If you chose line graph as your visualization type and multiple states, you will be asked whether you want multiple lines or one line. If you choose multiple lines, each line represents a state you chose, and each value is the selected statistic done over the values for the isolated data item/domain category for only that state. If you choose one line, the statistic you chose is applied over all the values for the isolated data item/domain category for all the states you previously selected.
    * If you chose bar plot as your visualization type and either multiple states and multiple years, or one state and one year, you will be asked whether states or years should represent the x axis. If you want states on the x axis, each bar is representative of one state selected and the value is the statistic applied over all values of the isolated data item/domain category for all the states specified. If you want years on the x axis, each bar is representative of one year selected and the value is the statistic applied over all values of the isolate data item/domain category for all the states specified.
11. You can generate the corresponding graph and data table for all the selections you have previosly made. For the graphs, you can hover each bar in the bar plot, or each point on the line(s) in the line graph to see specific values. After you click the Generate Graph button, you can click the Save Figure button that will save the graph as a static image and as a .png to a folder called `figures` in a `user_results` folder that is created upon cloning this entire directory. The name of this file will be `figure_<insert_number_of_time_button_has_been_clicked_in_current_session>.png.` Likewise, when you click the Generate Data Table figure, both a data table will be shown in the tool, and be saved as a .csv file to a folder called `tables` in the same `user_results` that holds the `figures` folder. The name of this file will be `table_<insert_number_of_time_button_has_been_clicked_in_current_session>.png.` **You will want to rename these files if you want to save them after your session using the tool terminates, as they will be rewritten in the next session otherwise.**
12. When you make a different selection for a previous choice you have made, the buttons will reset if the selections after the one you changed still apply. If any data selections after the one you changed do not apply, they will all disappear and you will have to traverse through the tool again from the selection you changed. Changing a bar plot to a line graph and vice versa may also trigger the special cases questions (described in step 10) that will have to be answered before the final 3 buttons appear for you.

**Note: If for some reason the next selection you have to make is not displayed, it means that your previous data specifications are invalid. This is likely to occur when expecting the Select Additional Data Item and Select Year sections to appear. To fix this, you must change some/all your previous selections, such as adding/removing a state, domain category, or additional data item.**



