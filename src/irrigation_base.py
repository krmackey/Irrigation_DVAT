import pandas as pd
import sqlite3
import os
from typing import Union

class DB:
    def __init__(self,
                 path_db: str , # Path to the database file
                 create: bool = False 
                ) -> None:
        '''
        Constructor for the DB class, 
        Takes in a string specifying the path to the database that will be created or already exists
        
        Returns None
        '''
        self.exists=False
        # Check if the file does not exist
        if not os.path.exists(path_db):
            if create:
                self.conn = sqlite3.connect(path_db) #creates connection
                self.conn.close()
            else:
                raise FileNotFoundError(path_db + ' does not exist.')
        else:
            self.exists=True #the file exists so the database does not need to get made again in the Irr_DB class constructor
        self.path_db = path_db
        return
    
    def connect(self) -> None:
        '''
        Sets up connection to database, so it can then be queried
        Enables foriegn key constraint checking
        
        Returns None
        '''
        self.conn = sqlite3.connect(self.path_db)
        self.curs = self.conn.cursor()
        self.curs.execute("PRAGMA foreign_keys=ON;")
        return
    
    def close(self) -> None:
        '''
        Closes the database

        Returns None
        '''
        self.conn.close()
        return
    
    def run_query(self, sql:str, params:Union[dict[str,str],None]) -> pd.DataFrame:
        '''
        Takes in a string with a SQL query (stored as sql) and a dictionary of parameters to fill in dynamic elements in the sql query
        Another input possible for params is None because the user specifies commodity first, which does not change dynamically so no additional input is needed
        Uses pd.read_sql to query database
        
        Returns the results of the query in a pandas DataFrame
        '''
        self.connect()
        results = pd.read_sql(sql, self.conn,params=params)
        self.close()
        return results


    def drop_all_tables(self) -> None:
        '''
        Drop all tables from the database

        Returns None
        '''
        self.connect()
        
        try:
            self.curs.execute("DROP TABLE IF EXISTS tState;")
            self.curs.execute("DROP TABLE IF EXISTS tMain;")
        except Exception as e:
            self.close()
            raise e
        self.close()
        return
    
    
    def build_tables(self) -> None:
        '''
        Drops all tables in case they already exist, 


        Builds empty relational table tMain with primary keys: state_id, year, commodity, data_item, domain, and domain_category. 
        All columns are of the text type except a value column that is numeric because some entries in the USDA irrigation data had 
        decimal points.
        
        Builds empty relational table tState with state_id as primary key. All columns are of the text type.

        Returns None
        '''
        
        #Drop all tables first
        self.drop_all_tables()
        self.connect()

        #state_id is the primary key, where each entry in that column is a state abbreviation
        # the names of states and corresponding ANSI codes make up the other columns
        sql = """
        CREATE TABLE tState (
            state_id TEXT NOT NULL PRIMARY KEY,
            
            state TEXT NOT NULL,
            state_ANSI TEXT NOT NULL
        )
        ;"""
        self.curs.execute(sql)
        
        #state_id is a foreign key in tMain, meaning it is the primary key in the other table tMain
        #All entries must not be equal to None
        sql = """
        CREATE TABLE tMain (
            state_id TEXT NOT NULL REFERENCES tState(state_id), 
            year TEXT NOT NULL,
            commodity TEXT NOT NULL,
            data_item TEXT NOT NULL, 
            domain TEXT NOT NULL,
            domain_category TEXT NOT NULL, 
            value NUMERIC NOT NULL, 
            PRIMARY KEY (state_id, year, commodity, data_item, domain, domain_category)
        )
        ;"""
        self.curs.execute(sql)
        
        
        return

    def load_data(self) -> None:
        
        '''
        Inserts preprocessed data created in prep_data() into the appropriate relational tables (tMain or tState) 
        using sql and by calling load_table()
        
        Returns None
        '''


        data = self.prep_data() ##recieves the data to be loaded into the tState and tMain tables in the form of pandas DataFrames
        sql = """
        INSERT INTO tState (state_id, state, state_ANSI)
        VALUES (:state_id, :state, :state_ANSI)

        ;"""
        self.load_table(sql, data['tState'])
        
        


        sql = """
        INSERT INTO tMain (state_id, year, commodity, data_item, domain, domain_category, value) 
        VALUES (:state_id, :year, :commodity, :data_item, :domain, :domain_category, :value) 

        ;"""
        self.load_table(sql, data['tMain'])

        
        
        return


    def load_table(self,sql:str, data:pd.DataFrame) -> None:
        '''
        Takes in a sql query stored as string named sql
        Uses the to_dict function in pandas to convert the pandas DataFrame passed in as data
        into a dictionary, and inserts the data row by row into the table specified by the sql query 
        
        Returns None
        '''
        
        self.connect()
        
        for i, row in enumerate(data.to_dict(orient = 'records')):
            try:
                self.curs.execute(sql, row)
            except Exception as e:
                print(e)
                print('\nrow: ', i)
                print('\n', row) ##errors in all rows 
                self.conn.rollback() #undo everything since the last commit
                raise e #display error and reraise error (print error message again)
        self.conn.commit() ##either get all data on table or get none of it
        self.close
        
        return


    def prep_data(self) -> dict[str, pd.DataFrame]:
        '''
        Imports the data from .csv files to pandas DataFrames, does any cleaning of the data,
        and splits into separate dataframes that will eventually become tables in the database.

        For cleaning the Data Item column, each commodity has a different pattern of displaying redundant information for their corresponding data items
        Data Items are thus cleaned according to specific commodity.
        
        Pattern of cleaning the data item column is fully detailed for the first commodity specified,
        assume similar details for the rest of the commodities unless noted otherwise.

        Returns a dictionary where the key is the table name and the value is the associated data in a pandas DataFrame.
        '''
        
        #.csv found in GitHub
        df = pd.read_csv('data/Irrigation_Data.csv', low_memory=False)

        #ensuring original data is not modified
        irr=df.copy()

        ##drop all unnecessary columns
        irr.drop(['Week Ending', 'Geo Level', 'Ag District','Ag District Code', 'County', 'County ANSI', 'Zip Code', 
                 'Region', 'watershed_code', 'Watershed', 'CV (%)'], axis=1, inplace=True)
        
        ##now dropping all week-based data
        index_year = irr[irr['Period'] != "YEAR"].index
        irr.drop(index_year, inplace=True)

        ##dropping any rows that have " (D)" or " (Z)" listed
        index_val_wrong = irr[(irr['Value'] == ' (D)') | (irr['Value'] == ' (Z)')].index
        irr.drop(index_val_wrong, inplace=True)

        ##remove commas from value column
        irr['Value'] = irr['Value'].str.replace(',', '') 

        ##setting columns to proper data types
        irr['Year']=irr['Year'].astype(str)
        irr['State ANSI']=irr['State ANSI'].astype(str)
        irr['Value']=irr['Value'].astype(float)

        ##cleaning Domain Category column
        for index, row in irr.iterrows():
            if row['Domain Category'].find(":") != -1: #getting rid of the redundant information that repeats the domain type
                initial=row['Domain Category'].split(":")
                new="".join(initial[1:])[2:-1]
                irr.loc[index, 'Domain Category']=new

        ##cleaning Data Item column -- each commodity has a different pattern of displaying redundant information 
        #for their corresponding data items
        
        ##clean based on pumps as commodity
        for index, row in irr.loc[irr['Commodity']=='PUMPS'].iterrows():
            initial=row['Data Item'].split("PUMPS, IRRIGATION") ##splitting based on the redudant information about the commodity
            new="".join(initial[1:])[2:] ##getting the essential information without the beginning " - "
            if new[0]==" ": #getting rid of space at the beginning after the split (didn't occur for all rows)
                new=new[1:]
            new=new.split("(EXCL WELLS), ")[-1] ##making the pumps commodity have the assumption that its data items don't include wells, as "(EXCL WELLS)" is seen in all data items (where commodity == pumps)
            irr.loc[index, 'Data Item']=new ##setting the entry in the dataframe to be the newly processed item
        
        #clean based on wells as commodity
        for index, row in irr.loc[irr['Commodity']=='WELLS'].iterrows():
            initial=row['Data Item'].split("WELLS, USED FOR IRRIGATION")
            new="".join(initial[1:])[2:]
            if new[0]==" ": #getting rid of space at the beginning after the split (didn't occur for all rows)
                new=new[1:]
            irr.loc[index, 'Data Item']=new
        
        #clean based on labor as commodity
        for index, row in irr.loc[irr['Commodity']=='LABOR'].iterrows():
            initial=row['Data Item'].split(",")
            new=",".join(initial[1:])[1:] ##getting rid of the redundant information located before the 1st comma
            irr.loc[index, 'Data Item']=new
        
        #clean based on water as commodity
        for index, row in irr.loc[irr['Commodity']=='WATER'].iterrows():
            initial=row['Data Item'].split(",")
            new=",".join(initial[2:])[1:]## getting rid of the redundant information before the 2nd comma
            irr.loc[index, 'Data Item']=new
        
        #clean based on energy as commodity
        for index, row in irr.loc[irr['Commodity']=='ENERGY'].iterrows():
            initial=row['Data Item'].split("ENERGY, IRRIGATION, ON FARM PUMPING") ##making the assumption that all data items under the water commodity relate to on farm pumping, ("ON FARM PUMPING" seen in all rows)
            new="".join(initial[1:])[2:] 
            if new[0]==" ": 
                new=new[1:]
            irr.loc[index, 'Data Item']=new
        
        #clean based on facilities and equipment as commodity
        for index, row in irr.loc[irr['Commodity']=='FACILITIES & EQUIPMENT'].iterrows():
            initial=row['Data Item'].split("IRRIGATION")
            new="".join(initial[1:])[2:]
            if new[0]==" ": 
                new=new[1:]
            irr.loc[index, 'Data Item']=new
        
        ##clean based on practices as commodity
        for index, row in irr.loc[irr['Commodity']=='PRACTICES'].iterrows():
            initial=row['Data Item'].split("PRACTICES, IRRIGATION")
            new="".join(initial[1:])[2:]
            if new[0]==" ": 
                new=new[1:]
            irr.loc[index, 'Data Item']=new
        
        
        ##Preparing the tables tState and tMain

        tState = irr[['State ANSI','State']].drop_duplicates() ##getting only the unique pairs of State ANSI and State
        tState.columns=['state_ANSI', 'state'] ##renaming the columns

        ##loading in state abbreviation data provided by the CDC, but also contains data about US territories
        states=pd.read_csv('data/data-map-state-abbreviations.csv') 

        ##setting all values in column to be uppercase to match format of USDA irrigation data
        states['Name']=states['Name'].str.upper() 
        
        ##renaming the columns
        states.rename(columns={'Name': 'state', 'Abbreviation': 'state_id'}, inplace=True)
        
        ##performing inner merge on state name so the 50 states will be the only items included 
        # (gets rid of the extra entries about US territories in the pd.DataFrame states).
        tState=pd.merge(states, tState, on=['state']) 
        tState = tState[['state_id', 'state', 'state_ANSI']] ##rearranging the columns
        

        ##getting only the unique pairs of State, Year, Commodity, Data Item, Domain, Domain Category, and Value
        tMain = irr[['State','Year', 'Commodity', 'Data Item', 'Domain', 'Domain Category', 'Value']].drop_duplicates()
        
        #renaming columns
        tMain.columns=['state', 'year', 'commodity', 'data_item', 'domain', 'domain_category', 'value']
        
        ##obtaining the state abbreviation data (state_id) and making it so that it takes the place of a state name in tMain
        tMain=pd.merge(tMain, states, on=['state']) 
        tMain=tMain[['state_id','year', 'commodity', 'data_item', 'domain', 'domain_category', 'value']]
        

        return {'tState': tState, 'tMain': tMain}
