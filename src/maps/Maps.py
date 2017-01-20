import multiprocessing
from queue import Queue

import googlemaps

from helpers import MongoHelper
from maps.MapsProcessor import MapsProcessor

""""Class used to look up found websites with the google maps api and find usefull data"""


class Maps:
    def __init__(self):
        # This is needed to connect with the Google Maps API. The key is a generated key by Google specific for this application.
        self.client = googlemaps.Client(key="AIzaSyCuBnzZ6K_wHln6EFY4VuJ-Jw03yNeL38c")
        self.queue = Queue()
        self.threads = []

    def start(self):
        print("---------- Maps Starting ----------")
        [self.queue.put(id) for id in MongoHelper.get_all_Ids()]

        self.create_threads()

        for t in self.threads:
            t.join()

        self.end()

    """"Create a number of threads based on the host available amount of threads.
     These threads run an instance of the MLProcessor class"""

    def create_threads(self):
        # Creates threads and add them to a list.
        for i in range(1, multiprocessing.cpu_count()):
            name = "Thread-%s" % i
            thread = MapsProcessor(name, self.client, self.queue)
            thread.start()
            self.threads.append(thread)

    def end(self):
        print("---------- Maps Ending ----------")

        from list.Listing import Listing
        # Starts the Listing part of the application that predicts in or out of scope
        listing = Listing(True)
        listing.start()
