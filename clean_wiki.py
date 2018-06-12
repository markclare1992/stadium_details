from pymongo import MongoClient
import googlemaps, numpy, wikipedia, wptools, re, html, config
from googlemaps import convert
from bs4 import BeautifulSoup, NavigableString

#make everything lower case when comparing
unit_strings = ['m', 'metres', 'y', 'yards', 'yds', 'yd', 'ft', 'feet']
client = MongoClient()
if client:
    matches = client.whoscored.matches
    stadiums = client.whoscored.stadiums
    wiki = client.whoscored.wiki

def strip_html(src):
    p = BeautifulSoup(src, 'lxml')
    text = p.findall(text=lambda text:isinstance(text, NavigableString))
    return u" ".join(text)


def clean_dimensions(dimension_string):
    return


def clean_surface(surface_string):
    return


def clean_wiki_data(wiki_data):
    return
