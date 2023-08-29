import pandas as pd
import requests
from apiExtraction import gameIdCollection as gidc

class nhlDataFrame:
    def __init__(self):
        self.df = pd.DataFrame()
        self.game_ids = []

    def get_url(self,game_id):
        raise NotImplementedError("Subclasses should implement this method!")
        #return self.id_to_url_method(game_id)

    def extract_data_from_json(self,json):
        raise NotImplementedError("Subclasses should implement this method!")
        #return self.json_collection_method(json)

    def get_game_ids(self):
        try:
            return self.df['game_id'].unique().tolist()
        except:
            print(f"An error occured trying to get game_ids for the nhlDataFrame")
            return []

    def get_json(self,game_id):
        API_URL = self.get_url(game_id)
        return requests.get(API_URL, params={"Content-Type": "application/json"}).json()

    def update_from_game_id(self, game_id):
        if game_id in self.game_ids:
            return 
        json = self.get_json(game_id)
        self.update_from_json(json)

    def update_from_json(self, json):
        temp_df = pd.DataFrame(self.extract_data_from_json(json))
        #if that game_id is already in the df, then return
        try:
            if temp_df['game_id'].unique().tolist()[0] in self.game_ids:
                return
        except:
            print(f"An error occured trying to get game_ids for the nhlDataFrame")
            return
            
        #if temp_df doesn't have the same columns as self.df, then return
        if set(temp_df.columns.tolist()) != set(self.df.columns.tolist()) and len(self.df.columns.tolist()) != 0:
            print(f"current columns: {self.df.columns.tolist()}")
            print(f"new columns: {temp_df.columns.tolist()}")
            print(f"Updating nhl DF with a dataframe that has different columns")

        #update, and add the indeces of the new df to the old df
        self.df = pd.concat([self.df,temp_df],ignore_index=True)
        self.game_ids = self.get_game_ids()

    def update_over_range(self, start_date, end_date):
        game_ids = gidc.collect_ids_over_range(start_date,end_date)
        for game_id in game_ids:
            self.update_from_game_id(game_id)

    def update_over_season(self, season):
        game_ids = gidc.collect_ids_over_season(season)
        for game_id in game_ids:
            self.update_from_game_id(game_id)

    
