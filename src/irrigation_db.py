import pandas as pd
import sqlite3
import os

class DB:
    def __init__(self,
                 path_db: str ,        # Path to the database file
                 create: bool = False # Should we create a new database if it doesn't exist?
                ):
        
        # Check if the file does not exist
        if not os.path.exists(path_db):
            # Should we create it?
            if create:
                self.conn = sqlite3.connect(path_db)
                self.conn.close()
            else:
                raise FileNotFoundError(path_db + ' does not exist.')
        self.path_db = path_db
        return
    
    def connect(self) -> None:
        self.conn = sqlite3.connect(self.path_db)
        self.curs = self.conn.cursor()
        self.curs.execute("PRAGMA foreign_keys=ON;")
        return
    
    def close(self) -> None:
        self.conn.close()
        return
    
    def run_query(self, sql:str):
        self.connect()
        results = pd.read_sql(sql, self.conn)
        self.close()
        return results


    def drop_all_tables(self, are_you_sure=False):
        '''
        Drop all tables from the database
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
    
    
    def build_tables(self, are_you_sure=False):
        # Drop all tables first
        self.connect()
        self.curs.execute("DROP TABLE IF EXISTS tState;")
        self.curs.execute("DROP TABLE IF EXISTS tMain;")
 
        '''
        sql = """
        CREATE TABLE tDataDescribe (
            data_item TEXT --PRIMARY KEY,
            commodity TEXT NOT NULL,
            PRIMARY KEY (data_item, commodity)
            
        )
        ;"""
        self.curs.execute(sql)
        
        sql = """
        CREATE TABLE tDomainDescribe (
            domain_category TEXT --PRIMARY KEY,
            domain TEXT NOT NULL,
            PRIMARY KEY (domain_category, domain)
            
        )
        ;"""
        self.curs.execute(sql)
        '''   

        sql = """
        CREATE TABLE tState (
            state_id TEXT NOT NULL PRIMARY KEY,
            
            state TEXT NOT NULL,
            state_ANSI TEXT NOT NULL
        )
        ;"""
        self.curs.execute(sql)

        sql = """
        CREATE TABLE tMain (
            state_id TEXT NOT NULL REFERENCES tState(state_id), -- bc state_id part of primary key in tState
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

    def load_data(self):
        data = self.prep_data() 
        

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


    def load_table(self,sql:str, data:pd.DataFrame):
            
        
        '''
        SQL statment should have named parameters with names appear the same in the dataframe
        
        '''
        
        self.connect()
        
        for i, row in enumerate(data.to_dict(orient = 'records')):
            try:
                self.curs.execute(sql, row)
            except Exception as e:
                print(e)
                print('\nrow: ', i)
                print('\n', row) ##errors in all rows -- see that all of them have 0's in them 
                self.conn.rollback() #undo everything since the last commit
                raise e #display error and reraise error (print error message again)
        self.conn.commit() ##either get all data on table or get none of it
        self.close
        
        return


    def prep_data(self):
        '''
        Import the data to pandas, do any cleanup needed,
        and split into spearate dataframes to load into the database
        '''
        
        df = pd.read_csv('data/Irrigation_Data.csv', low_memory=False)

        irr=df.copy()

        
        ##drop all unnnecesaary columns
        irr.drop(['Week Ending', 'Geo Level', 'Ag District','Ag District Code', 'County', 'County ANSI', 'Zip Code', 
                 'Region', 'watershed_code', 'Watershed', 'CV (%)'], axis=1, inplace=True)
        
        ##now dropping all week data
        index_year = irr[irr['Period'] != "YEAR"].index
        irr.drop(index_year, inplace=True)

        ##dropping any rows that have " (D)" or " (Z)" listed
        index_val_wrong = irr[(irr['Value'] == ' (D)') | (irr['Value'] == ' (Z)')].index
        irr.drop(index_val_wrong, inplace=True)

        ##remove commas from value column
        irr['Value'] = irr['Value'].str.replace(',', '') 

        ##setting columns to proper dtypes
        irr['Year']=irr['Year'].astype(str)
        irr['State ANSI']=irr['State ANSI'].astype(str)
        irr['Value']=irr['Value'].astype(float)

        ##cleaning Domain Category column
        for index, row in irr.iterrows():
            if row['Domain Category'].find(":") != -1:
                initial=row['Domain Category'].split(":")
                new="".join(initial[1:])[2:-1]
                irr.loc[index, 'Domain Category']=new

        ##cleaning Data Item column
        
        ##clean pumps
        for index, row in irr.loc[irr['Commodity']=='PUMPS'].iterrows():
            initial=row['Data Item'].split("PUMPS, IRRIGATION")
            new="".join(initial[1:])[2:]
            if new[0]==" ": #11/12
                new=new[1:]
            new=new.split("(EXCL WELLS), ")[-1] ##11/18
            irr.loc[index, 'Data Item']=new
        
        #clean wells
        for index, row in irr.loc[irr['Commodity']=='WELLS'].iterrows():
            initial=row['Data Item'].split("WELLS, USED FOR IRRIGATION")
            new="".join(initial[1:])[2:]
            if new[0]==" ": #11/12
                new=new[1:]
            irr.loc[index, 'Data Item']=new
        
        #clean labor
        for index, row in irr.loc[irr['Commodity']=='LABOR'].iterrows():
            initial=row['Data Item'].split(",")
            new=",".join(initial[1:])[1:] #11/12
            irr.loc[index, 'Data Item']=new
        
        #clean water
        for index, row in irr.loc[irr['Commodity']=='WATER'].iterrows():
            initial=row['Data Item'].split(",")
            new=",".join(initial[2:])[1:] #11/12
            irr.loc[index, 'Data Item']=new
        
        #clean energy
        for index, row in irr.loc[irr['Commodity']=='ENERGY'].iterrows():
            initial=row['Data Item'].split("ENERGY, IRRIGATION, ON FARM PUMPING")
            new="".join(initial[1:])[2:]
            if new[0]==" ": #11.12
                new=new[1:]
            irr.loc[index, 'Data Item']=new
        
        #clean faciltlies and equipment
        for index, row in irr.loc[irr['Commodity']=='FACILITIES & EQUIPMENT'].iterrows():
            initial=row['Data Item'].split("IRRIGATION")
            new="".join(initial[1:])[2:]
            if new[0]==" ": #11/12
                new=new[1:]
            irr.loc[index, 'Data Item']=new
        
        ##clean practices
        for index, row in irr.loc[irr['Commodity']=='PRACTICES'].iterrows():
            initial=row['Data Item'].split("PRACTICES, IRRIGATION")
            new="".join(initial[1:])[2:]
            if new[0]==" ": #11/12
                new=new[1:]
            irr.loc[index, 'Data Item']=new
        
        
        
        
        ##setting up table prep

        tState = irr[['State ANSI','State']].drop_duplicates()
        tState.columns=['state_ANSI', 'state']

        ##loading in state_id data
        states=pd.read_csv('data/data-map-state-abbreviations.csv')
        states.rename(columns={'Name': 'state', 'Abbreviation': 'state_id'}, inplace=True)
        for i, row in states.iterrows():
            new=row['state'].upper()
            states.loc[i, 'state']=new
        tState=pd.merge(states, tState, on=['state'])
        tState = tState[['state_id', 'state', 'state_ANSI']]
        


        
        
        tMain = irr[['State','Year', 'Commodity', 'Data Item', 'Domain', 'Domain Category', 'Value']].drop_duplicates()
        tMain.columns=['state', 'year', 'commodity', 'data_item', 'domain', 'domain_category', 'value']
        tMain=pd.merge(tMain, states, on=['state'])
        tMain=tMain[['state_id','year', 'commodity', 'data_item', 'domain', 'domain_category', 'value']]
        

        return {'tState': tState, 'tMain': tMain}
