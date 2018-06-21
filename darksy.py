from pymongo import MongoClient
import requests, config
from settings import matches, stadiums, wiki, eventsSorted, matchdetails, goals, weather, matchheaders, stadium_matchId
from datetime import datetime, date, time

def convert_timestamp(timestamp):
    return  (timestamp - datetime(1970, 1, 1)).total_seconds()


def historical_request(lat,lng,timestamp,units='si',exclude='currently,flags'):
    url = "https://api.darksky.net/forecast/{}/{},{},{}".\
        format(config.darksky_api_key, lat, lng, timestamp)
    params = {"units": units, "exclude":exclude}
    r = requests.get(url, params=params)
    return r.json()


def scrape_weather(seasonId, overwrite=False):
    for m in matchheaders.find({'seasonId': seasonId}):
        stad = stadium_matchId.find_one({'matchId': m['matchId']})
        if stad:
            stad_loc = stadiums.find_one({'venueName': stad['venueName']})
            weather_data = {'matchId':m['matchId'],
                        'startTime': int(convert_timestamp(m['startTime'])),
                        'data': historical_request(stad_loc['location_data']['geometry']['location']['lat'],
                                                  stad_loc['location_data']['geometry']['location']['lng'],
                                                  int(convert_timestamp(m['startTime'])))}

            weather.replace_one({'matchId': m['matchId']}, weather_data, upsert=True)


# Needed a function to overwrite weather data for a venue, if venue location was found to be incorrect
def update_weather(seasonId, venueName, overwrite=False):
    for m in matchheaders.find({'seasonId': seasonId}):
        stad = stadium_matchId.find_one({'matchId': m['matchId'], 'venueName': venueName})
        if stad:
            stad_loc = stadiums.find_one({'venueName': stad['venueName']})
            weather_data = {'matchId':m['matchId'],
                        'startTime': int(convert_timestamp(m['startTime'])),
                        'data': historical_request(stad_loc['location_data']['geometry']['location']['lat'],
                                                  stad_loc['location_data']['geometry']['location']['lng'],
                                                  int(convert_timestamp(m['startTime'])))}

            weather.replace_one({'matchId': m['matchId']}, weather_data, upsert=True)



# API returns weather data for every hour on requested day, unwind hour data, keep data entry for hour which is closest
# to kick off for each game
pipeline = [
    {"$unwind":"$data.hourly.data"},
    {"$addFields": {"diff": {"$abs": {"$subtract": ["$startTime", "$data.hourly.data.time"]}}}},
    {"$sort": {"diff": 1}},
    {"$group": {
		"_id": "$matchId",
		"doc": {"$first": "$$ROOT"}}},
    {"$project": {"matchId": "$doc.matchId", "startTime": "$doc.startTime", "latitude": "$doc.data.latitude",
                  "longitude": "$doc.data.longitude", "temperature": "$doc.data.hourly.data.temperature",
                  "summary":"$doc.data.hourly.data.summary"}},
    {"$lookup": {
            "from": "matchheaders",
            "localField": "matchId",
            "foreignField": "matchId",
            "as": "details"}},
    {"$project": {"matchId": 1, "startTimestamp": "$startTime", "latitude": 1,
                  "longitude": 1, "temperature": 1, "summary": 1,
                  "tournamentId": {"$arrayElemAt": ["$details.tournamentId",0]},
                  "startTime": {"$arrayElemAt": ["$details.startTime",0]},
                  "score": {"$arrayElemAt": ["$details.score",0]},
                  "home": {"$arrayElemAt": ["$details.home.name",0]},
                  "away": {"$arrayElemAt": ["$details.away.name",0]}}},
    {"$lookup": {
            "from": "tournaments",
            "localField": "tournamentId",
            "foreignField": "tournamentId",
            "as": "tournament"}},
    {"$project": {"matchId": 1, "startTimestamp": "$startTime", "latitude": 1,
                  "longitude": 1, "temperature": 1, "summary":1,
                  "tournamentId": 1,
                  "startTime": 1,
                  "score": 1,
                  "home": 1,
                  "away": 1,
                  "tournament": {"$arrayElemAt": ["$tournament.name",0]}}},
    {"$addFields":{
		"game": {"$concat":["Game: ", "$home", " vs ", "$away"]}}},
    {"$out": "match_weather"}
]


#Can tidy up above aggregation quite a bit.

if __name__ == "__main__":
    #scrape_weather(6833)
    #update_weather(6974, 'Olimpico', overwrite=True)
    weather.aggregate(pipeline, allowDiskUse=True)
