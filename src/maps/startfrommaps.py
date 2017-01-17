import MongoHelper
from Maps import MapsProcessor
import googlemaps

client = googlemaps.Client(key="AIzaSyCuBnzZ6K_wHln6EFY4VuJ-Jw03yNeL38c")
maps = MapsProcessor("test",client,None)
maps.scan_url("http://www.heerlijkehuisjes.nl")