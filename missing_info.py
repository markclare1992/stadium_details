from pymongo import MongoClient
import googlemaps, numpy, wikipedia, wptools, re, html, config
from googlemaps import convert
gmaps = googlemaps.Client(key = config.gmaps_api_key)
client = MongoClient()
if client:
    matches = client.whoscored.matches
    stadiums = client.whoscored.stadiums
    wiki = client.whoscored.wiki


def missing_stadiums():
    for stadium in matches.find().distinct('venueName'):
        if not stadiums.find_one({'venueName': stadium}):
            print(stadium)


# Should really save alternative name as variable, and add stadium as a wikipedia type for stadium_checks that are okay.
def scrape_stadium_manually(OPTAvenueName,alternativeName, overwrite=False):
    print('Searching for {}'.format(OPTAvenueName))
    if stadiums.find_one({'venueName': OPTAvenueName}) and not overwrite:
        print('Already in db')
        return True

    wiki_name = wikipedia.search(html.unescape(alternativeName + ' alternativeName'))
    geocode_result = gmaps.geocode(alternativeName)
    if geocode_result:
        elevation_result = gmaps.elevation(convert.normalize_lat_lng(geocode_result[0]['geometry']['location']))
        stadium_data_to_insert = {'venueName': OPTAvenueName, 'location_data': geocode_result[0],
                                  'altitude_data': elevation_result[0]}
        stadiums.replace_one({'venueName': OPTAvenueName}, stadium_data_to_insert, upsert=True)
    if wiki_name:
        wiki_page = wptools.page(wiki_name[0], silent=True)
        wiki_page.get_parse()
        wiki_data = wiki_page.data['infobox']
        wiki_data_to_insert = {'venueName': OPTAvenueName, 'wiki_name': wiki_name[0], 'wiki_data': wiki_data}
        wiki.replace_one({'venueName': OPTAvenueName}, wiki_data_to_insert, upsert=True)


#scrape_stadium_manually("Municipal de Chap�n", "Municipal de Chapín")
#  Oosterenkstadion demolished, was  52.516997932 6.118832858

def stadium_check():
    for stadium in stadiums.find({"location_data.types": {"$ne": "stadium"}}):
        print(stadium['venueName'], stadium['location_data']['geometry']['location'],
              stadium['location_data']['types'])


def wiki_check():
    """ Check google and wikipedia coordinates against each other
    to confirm both are about the same venue"""


stadium_check()

# Almaarderhout should be Alkmaarderhout