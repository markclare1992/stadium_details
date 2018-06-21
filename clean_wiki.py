from pymongo import MongoClient
import googlemaps, numpy, wikipedia, wptools, re, html, config
from googlemaps import convert
from bs4 import BeautifulSoup, NavigableString
from settings import matches, stadiums, wiki, gmaps

# make everything lower case when comparing
unit_strings = ['m', 'ms', 'metres', 'y', 'yards', 'yds', 'yd', 'ft', 'feet']

mapping = {
    "m": "metres",
    "ms": "metres",
    "metres": "metres",
    "y": "yards",
    "yards": "yards",
    "yds": "yards",
    "yd": "yards",
    "ft": "feet",
    "feet": "feet",
    "unknown": "unknown"
}

mapping_surface = {
    "artificial": "artificial",
    "grassmaster": "grassmaster",
    "bermuda": "grass",
    "playmaster": "playmaster",
    "fieldturf": "artificial",
    "natural": "grass",
    "kentucky bluegrass": "grass",
    "astro": "artifical",
    "hybrid": "grass",
    "synthetic": "artificial"
}


def strip_html(src):
    p = BeautifulSoup(src, 'lxml')
    text = p.findAll(text=lambda text:isinstance(text, NavigableString))
    return u" ".join(text)


def convert_to_metres(measurement, unit):
    measurement = float(measurement)
    if unit == "yards":
        return measurement*.9144
    if unit == 'feet':
        return measurement*.3048
    if unit == 'metres':
        return measurement
    if unit == 'unknown':
        return measurement


def clean_dimensions(dimension_string):
    # some strings use comma as decimal point
    dimension_string = re.sub(",", ".", dimension_string)
    # Save first 2 numbers matching pattern below for width and length
    dims = re.findall("(\d+\.?\d*)", dimension_string)
    # Remove excess characters from string
    dimension_string = re.sub("[^a-z]+", " ", dimension_string.lower()).split(" ")
    dimension = next((x for x in dimension_string if x in unit_strings), 'unknown')
    # If original dimension is unknown should add original string to an unknown dictionary to further clean later on
    dimension = mapping[dimension]
    if len(dims) > 1:
        extracted = {'original_dimension': dimension, 'length': convert_to_metres(dims[0], dimension),
                     'width': convert_to_metres(dims[1], dimension)}
        return extracted


def clean_surface(surface_string):
    surface_string = strip_html(surface_string)
    surface_string = re.sub("\\[|\\]","",surface_string.lower())
    return surface_string


def surface_explore():
    surfaces = {}
    for stad in wiki.find({"wiki_data.surface": {"$exists": True}}):
        sf = clean_surface(stad['wiki_data']['surface'])
        if sf not in surfaces:
            surfaces[sf] = 1
        else:
            surfaces[sf] += 1
    return sorted(surfaces.items(), key=lambda item: -item[1])


def clean_wiki_data():
    for stad in wiki.find():
        if stad['wiki_data']['dimensions']:
            stad['dimensions'] = clean_dimensions(stad['wiki_data']['dimensions'])
        wiki.save(stad)
    return


pipeline = [
    {"$project": {"venueName": 1, "dimensions_length": "$dimensions.length", "dimensions_width": "$dimensions.width",
                  "dimensions": "$dimensions.original_dimension"}},
    {"$lookup": {
        "from": "stadium_matchId",
        "localField": "venueName",
        "foreignField": "venueName",
        "as": "details"}},
    {"$project": {"venueName": 1, "dimensions_length": 1, "dimensions_width": 1, "dimensions": 1,
                  "matchId": {"$arrayElemAt": ["$details.matchId", 0]}}},
    {"$lookup": {
        "from": "matchheaders",
        "localField": "matchId",
        "foreignField": "matchId",
        "as": "details"}},
    {"$project": {"matchId": 1, "venueName": 1,
                  "dimensions_length": 1, "dimensions_width": 1, "dimensions": 1,
                  "tournamentId": {"$arrayElemAt": ["$details.tournamentId", 0]}}},
    {"$lookup": {
        "from": "tournaments",
        "localField": "tournamentId",
        "foreignField": "tournamentId",
        "as": "tournament"}},
    {"$project": {"matchId": 1, "venueName": 1, "tournamentId": 1,
                  "dimensions_length": 1, "dimensions_width": 1, "dimensions": 1,
                  "tournament": {"$arrayElemAt": ["$tournament.name",0]}}},
    {"$out": "stadium_dims"}
]

print(surface_explore())