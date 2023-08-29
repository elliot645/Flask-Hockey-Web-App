import pandas as pd
import requests
from .nhlDataFrame import nhlDataFrame

class boxscoreDataFrame(nhlDataFrame):
    #override
    def get_url(self,game_id):
        return f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live"

    #override
    def extract_data_from_json(self,json):
        data = { 
        'game_id' : json['gamePk'],
        'home_team' : json['gameData']['teams']['home']['name'],
        'away_team' : json['gameData']['teams']['away']['name'],
        'type' : json['gameData']['game']['type'],    
        'venue': json['gameData']['venue']['name'], 
        'date': json['gameData']['datetime']['dateTime'], 
        'home_away_time_diff': json['gameData']['teams']['home']['venue']['timeZone']['offset'] - json['gameData']['teams']['away']['venue']['timeZone']['offset'] 
        }
        return data
        