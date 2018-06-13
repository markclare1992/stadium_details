from pymongo import MongoClient
import googlemaps, config
client = MongoClient()
gmaps = googlemaps.Client(key = config.gmaps_api_key)
if client:
    matches = client.opta.matches
    stadiums = client.opta.stadiums
    wiki = client.opta.wiki
    eventsSorted = client.opta.eventsSorted
    matchdetails = client.opta.matchdetails
    goals = client.opta.goals

