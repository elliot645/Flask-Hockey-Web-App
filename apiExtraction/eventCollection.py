import os
import pandas as pd
import numpy as np
import requests
from joblib import dump, load

from .nhlDataFrame import nhlDataFrame

current_directory = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_directory, 'goal_probability_model.joblib')
clf = load(model_path)

class eventDataFrame(nhlDataFrame):

    #override
    def get_url(self,game_id):
        return f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live"

    def _extract_type_data_from_json(self,json,event_types,event_extraction_function):

        #event_ty = ['Shot','Goal','Missed Shot','Blocked Shot']
        events = filter(lambda a : a["result"]["event"] in event_types, json["liveData"]["plays"]["allPlays"]) 
        data = []
        for event in events:
            extracted_data = event_extraction_function(event)
            generic_data = {
                **event['coordinates'],
                'team': event['team']['name'], 
                'period': event['about']['period'],
                'time_left' : event['about']['periodTimeRemaining'],
                'home_goals' : event['about']['goals']['home'],
                'away_goals' : event['about']['goals']['away'],
                'home_team' : json['gameData']['teams']['home']['name'],
                'away_team' : json['gameData']['teams']['away']['name'],
                'game_id': json['gamePk']
                            }

            data.append({**extracted_data,**generic_data})
        return data

class shotDataFrame(eventDataFrame):
    
    #override
    def extract_data_from_json(self,json):
        def _extract_shot_data_from_event(shot):
            shot_data = {
                'type' : shot['result']['event'],
                'secondary_type' : shot['result'].get('secondaryType'),
                'shooter' : shot['players'][0]['player']['fullName'] if shot['result']['event'] != "Blocked Shot" else shot['players'][1]['player']['fullName'],
                'blocker' : shot['players'][0]['player']['fullName'] if shot['result']['event'] == "Blocked Shot" else 'None',
            }
            #Assists
            assisters = list(filter(lambda a : a['playerType'] == 'Assist',shot['players']))

            for i in range(2):
                if i < len(assisters):
                    shot_data[f"assist_{i+1}"] = assisters[i]['player']['fullName']
                else:
                    shot_data[f"assist_{i+1}"] = None
            
            #empty net goals mean there may not be a goalie in net
            goalie_info = list(filter(lambda a : a['playerType'] == 'Goalie',shot['players']))
            shot_data['goalie'] = goalie_info[0]['player']['fullName'] if len(goalie_info) > 0 else 'None'

            #add additional data to shot_data
            shot_data = {**shot_data,
                'strength' : shot['result']['strength']['name'] if shot['result']['event'] == 'Goal' else 'None',
                'game_winning_goal' : shot['result'].get('gameWinningGoal'),
                'empty_net' : shot['result'].get('emptyNet')
            }
            return shot_data

        event_types = ['Shot','Goal','Missed Shot','Blocked Shot']
        df = pd.DataFrame( super()._extract_type_data_from_json(json,event_types,_extract_shot_data_from_event) )
        #change x and y to be mapped vertically:
        try:
            df['x'] = np.abs(df['x'])
            df['y'] = (df['y'] * np.sign(df['x']))

            #take subset of df that the model can predict on: only shots and goals, with no nans in x and y
            shots_and_goals = df.loc[df['type'].isin(['Shot','Goal'])]
            shots_and_goals = shots_and_goals.dropna(subset=['x', 'y'])

            #remove the shots_and_goals from the original df to prevent duplication
            df = df.drop(shots_and_goals.index)

            #predict on the subset
            shot_locations = shots_and_goals[['x', 'y']].values
            probs = pd.DataFrame(clf.predict_proba(shot_locations))
            shots_and_goals['shot_probability'] = probs[1].values

            #add the subset back to the original df, in the same order
            df = pd.concat([df,shots_and_goals]).sort_index()


        except:
            print("An error occured trying to change the x and y coordinates of the shotDataFrame")
        return df


class hitDataFrame(eventDataFrame):
    

    #override
    def extract_data_from_json(self,json):
        def _extract_hit_data_from_event(hit):
            hit_data = {
                'hitter' : hit['players'][0]['player']['fullName'],
                'hittee' : hit['players'][1]['player']['fullName'],
            }
            return hit_data

        event_types = ['Hit']
        return super()._extract_type_data_from_json(json,event_types,_extract_hit_data_from_event)

class penaltyDataFrame(eventDataFrame):
    
    #override
    def extract_data_from_json(self,json):
        def _extract_pen_data_from_event(penalty):
            pen_data = {
                'penalty_on' : penalty['players'][0]['player']['fullName'] if 'players' in penalty else 'None',
                'drew_penalty' : penalty['players'][1]['player']['fullName'] if 'players' in penalty and len(penalty['players']) > 1 else 'None',
                'penalty_type' : penalty['result']['secondaryType']
            }
            return pen_data

        event_types = ['Penalty']
        return super()._extract_type_data_from_json(json,event_types,_extract_pen_data_from_event)

class faceoffDataFrame(eventDataFrame):

    #override
    def extract_data_from_json(self,json):
        def _extract_faceoff_data_from_event(faceoff):
            data = {
                'winner' : faceoff['players'][0]['player']['fullName'],
                'loser' : faceoff['players'][1]['player']['fullName'] if len(faceoff['players']) > 1 else 'None',
            }
            return data

        event_types = ['Faceoff']
        return super()._extract_type_data_from_json(json,event_types,_extract_faceoff_data_from_event)    

class giveawayDataFrame(eventDataFrame):

    #override
    def extract_data_from_json(self,json):
        def _extract_giveaway_data_from_event(giveaway):
            data = {
                'player' : giveaway['players'][0]['player']['fullName'],
            }
            return data 

        event_types = ['Giveaway']
        return super()._extract_type_data_from_json(json,event_types,_extract_giveaway_data_from_event)

class takeawayDataFrame(eventDataFrame):

    #override
    def extract_data_from_json(self,json):
        def _extract_takeaway_data_from_event(takeaway):
            data = {
                'player' : takeaway['players'][0]['player']['fullName'],
            }
            return data

        event_types = ['Takeaway']
        return super()._extract_type_data_from_json(json,event_types,_extract_takeaway_data_from_event)