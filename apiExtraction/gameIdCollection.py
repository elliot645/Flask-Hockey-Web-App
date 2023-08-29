import pandas as pd
import requests

#game type inputs:
def game_types():
    response = requests.get('https://statsapi.web.nhl.com/api/v1/gameTypes')
    game_types =  response.json()
    types = []
    for code in game_types:
        types.append(f"{code['description']} : {code['id']}")
    return types

#dates inputted as strings in format "YYYY-MM-DD"
def get_schedule_over_range(start_date,end_date,gametype=None):
    #get url with proper gameId, convert to json
    url = f"https://statsapi.web.nhl.com/api/v1/schedule"
    response = requests.get(url, params={"startDate" : start_date,"endDate" : end_date,"Content-Type": "application/json"})
    return response.json()

#season inputted as string in format "YYYY"
def get_schedule_over_season(season,game_types :list =None):
    #get url with proper gameId, convert to json
    season = str(season)
    season = f"{season}{int(season)+1}"
    url = f"https://statsapi.web.nhl.com/api/v1/schedule?season={season}"
    if game_types is None:
        game_types = ['R','P']
    for game_type in game_types:
        url += f"&gameType={game_types}"
    response = requests.get(url, params={"Content-Type": "application/json"})

    return response.json()

def schedule_to_ids(schedule_data):
    dates = schedule_data['dates']
    game_ids = []
    for date in dates:
        for game in date['games']:
            game_ids.append(game['gamePk'])
    return game_ids

def collect_ids_over_range(start_date,end_date):
    start_date = str(start_date)
    end_date = str(end_date)
    schedule_data = get_schedule_over_range(start_date,end_date)
    return schedule_to_ids(schedule_data)

def collect_ids_over_season(season):
    schedule_data = get_schedule_over_season(season)
    return schedule_to_ids(schedule_data)
    
def remove_duplicate_ids(game_ids,nhlDataFrames):
    #first, get a list of game_ids that are common to all nhlDataFrames. These can be skipped completely
    common_ids = game_ids
    for df in nhlDataFrames:
        common_ids = set(df.game_ids).intersection(common_ids)

    #return a list of game_ids to go over
    return set(game_ids).difference(common_ids)

def update_dataframes(start_season,end_id,nhlDataFrames):
    game_ids = collect_ids_over_range(start_season,end_id)
    game_ids = remove_duplicate_ids(game_ids,nhlDataFrames)

    #for each game_id: 
    for game_id in game_ids:
        #get a set which dataframes don't include that game_id yet
        url_dict = {}
        for df in nhlDataFrames:
            if game_id not in df.game_ids:
                #get url for that game_id
                url = df.get_url(game_id)

                #if that url is already in the url_dict, then add that dataframe to the list of dataframes that need to be updated
                if url in url_dict:
                    url_dict[url].append(df)

                #otherwise, add that url to the url_dict with a list containing that dataframe
                else:
                    url_dict[url] = [df]

        #for each url in the url_dict, get the json, and update each dataframe in the list of dataframes
        for url in url_dict:
            json = requests.get(url, params={"Content-Type": "application/json"}).json()
            for df in url_dict[url]:
                df.update(json)

    return nhlDataFrames