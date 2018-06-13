from pymongo import MongoClient
import googlemaps, numpy, wikipedia, wptools, re, html, config
from googlemaps import convert
from bs4 import BeautifulSoup, NavigableString
from settings import matches, stadiums, wiki, gmaps


def scrape(stadium, overwrite=False):
    print('Searching for {}'.format(stadium))
    if stadiums.find_one({'venueName': stadium}):
        print('Already in db')
        return True

    # Add string stadium to name of the stadium for wikipedia search, take most popular result as correct
    wiki_name = wikipedia.search(html.unescape(stadium + ' stadium'))
    geocode_result = gmaps.geocode(stadium)
    if geocode_result:
        elevation_result = gmaps.elevation(convert.normalize_lat_lng(geocode_result[0]['geometry']['location']))
        stadium_data_to_insert = {'venueName': stadium, 'location_data': geocode_result[0],
                                  'altitude_data': elevation_result[0]}
        stadiums.replace_one({'venueName': stadium}, stadium_data_to_insert, upsert=True)
    if wiki_name:
        wiki_page = wptools.page(wiki_name[0], silent=True)
        wiki_page.get_parse()
        wiki_data = wiki_page.data['infobox']
        wiki_data_to_insert = {'venueName': stadium, 'wiki_name': wiki_name[0], 'wiki_data': wiki_data}
        wiki.replace_one({'venueName': stadium}, wiki_data_to_insert, upsert=True)


if __name__ == "__main__":
    stads = matches.find().distinct('venueName')
    stads = [x for x in stads if x != None]
    for stadium in stads:
        scrape(stadium)