import pandas as pd
import requests
from .nhlDataFrame import nhlDataFrame

class boxscoreDataFrame(nhlDataFrame):
    #override
    def get_url(self,game_id):
        return f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live"

class skaterBoxscoreDataFrame(boxscoreDataFrame):
    #override
    def extract_data_from_json(self,json):
        def _extract_single_player(player):
            skater_data = {
                'player_id' : player['person']['id'],
                'player_name' : player['person']['fullName'],
                **player['stats']['skaterStats']
            }
            if 'faceOffPct' not in skater_data:
                skater_data['faceOffPct'] = None
            return skater_data

        box = json['liveData']['boxscore']['teams']
        skater_data = []

        for team in box:
            for person in box[team]['players']:
                #check if they are a player or goalie
                if 'skaterStats' in box[team]['players'][person]['stats']:
                    player_stats = {**_extract_single_player(box[team]['players'][person]),'game_id' : json['gamePk'], 'team': box[team]['team']['name']}
                    skater_data.append(player_stats)

        return skater_data

class goalieBoxscoreDataFrame(boxscoreDataFrame):
    #override
    def extract_data_from_json(self,json):
        def _extract_single_player(player):
            goalie_data = {
                'player_id' : player['person']['id'],
                'player_name' : player['person']['fullName'],
                **player['stats']['goalieStats']
            }
            for stat in ['powerPlaySavePercentage','shortHandedSavePercentage']:
                if stat not in goalie_data:
                    goalie_data[stat] = None

            print(len(goalie_data.keys()))
            print(goalie_data.keys())
            return goalie_data

        box = json['liveData']['boxscore']['teams']
        goalie_data = []

        for team in box:
            for person in box[team]['players']:
                #check if they are a player or goalie
                if 'goalieStats' in box[team]['players'][person]['stats']:
                    player_stats = {**_extract_single_player(box[team]['players'][person]),'game_id' : json['gamePk'], 'team': box[team]['team']['name']}
                    goalie_data.append(player_stats)

        return goalie_data

class teamBoxscoreDataFrame(boxscoreDataFrame):
    #override
    def extract_data_from_json(self,json):
        def _extract_single_team(team):
            team_data = {
                'team_id' : team['team']['id'],
                'team_name' : team['team']['name'],
                **team['teamStats']['teamSkaterStats']
            }
            return team_data

        box = json['liveData']['boxscore']['teams']
        team_data = []

        for team in box:
            team_stats = {**_extract_single_team(box[team]),'game_id' : json['gamePk']}
            team_data.append(team_stats)

        return team_data