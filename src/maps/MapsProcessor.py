import threading
import re

from googlemaps import places

import MongoHelper

""""Class inheriting a thread responsible for downloading and storing the content found for a url."""


class MapsProcessor(threading.Thread):
    def __init__(self, name, client, queue):
        threading.Thread.__init__(self)
        self.name = name
        self.client = client
        self.queue = queue

    """"Get an url from the queue, process the url and notify the queue the task on the retrieved item is done.
         Continue this process while the queue has items"""

    def run(self):
        while not self.queue.empty():
            id = self.queue.get()

            self.process(id)
            self.queue.task_done()

        print("%s done" % self.name)

    """"Download the url content in html form and save it to MongoDB"""

    def process(self, id):
        site = MongoHelper.get_result_by_id(id)
        # Scanning for the type of building connected to a given URL
        results = self.scan_url(site["url"])
        # Determining if the website is within or out of scope given the type of building it returned
        inscope = self.determine_scope(results)

        printable = "Empty" if inscope == -1 else bool(inscope)
        print("Thread-%s: Maps: %s is: %s with lat: %s / long: %s" % (
        self.name, site['url'], printable, self.lat, self.lng))

        # Changing the maps value to the result given in the previous scan.
        site["maps"] = inscope
        site["address"] = self.url_address
        site["lat"] = self.lat
        site["lng"] = self.lng

        # Resetting the url address
        self.url_address = ""
        self.lat = 0
        self.lng = 0

        # Updating the result in MongoDB
        MongoHelper.update_info(site)

    def extract_from_url(self, url):
        # Uses a regex method to extract the hostname from the URL
        m = re.search('www.([^.]+).+', url)
        if m is None:
            m = re.search('\/.([^.]+).+', url)
        return m.group(1)

    def json_result(self, result):
        if result["status"] != "ZERO_RESULTS":
            try:
                # Gets the top 5 results of the scan
                result = result["results"][:5:]
            except KeyError:
                print("No types, getting name")
            return result

    def check_details(self, url, placeid, resultCount):
        # Performs another API call to get more details
        details = places.place(self.client, placeid)
        result = details["result"]
        try:
            address_component = result["address_components"]
            for x in range(0, len(address_component)):
                if "country" in address_component[x]["types"]:
                    test = address_component[x]["short_name"]
                    if test != "NL":
                        return None
            # Gets the website from the results
            result_website = None
            if "website" in result:
                result_website = result["website"]
            if result_website is not None:
                currentUrl = url
                if "www" in currentUrl:
                    # Extracts hostname from URL
                    currentUrl = self.extract_from_url(currentUrl)
                # Checks if the website in the results is equal to the website we are looking for
                if currentUrl == self.extract_from_url(result_website):
                    # Gets the adress of the result and returns it
                    result_address = result["formatted_address"]
                    self.lat = result["geometry"]["location"]["lat"]
                    self.lng = result["geometry"]["location"]["lng"]
                    return result_address
            elif resultCount == 1:
                self.lat = result["geometry"]["location"]["lat"]
                self.lng = result["geometry"]["location"]["lng"]
                return result["formatted_address"]
            return None
        except KeyError:
            return None

    def get_types(self, url, dict, resultCount):
        # Gets address for a specific webshop
        address = self.check_details(url, dict["place_id"], resultCount)
        if address is not None:
            self.url_address = address
            try:
                # Gets types of buildings of a specific webshop
                result = dict["types"]
            except KeyError:
                print("No types, getting name..")
                result = dict["name"]
            return result

    def scan_url(self, url):
        # Sends a Google API call to search for buildings given a URL or company name. Also only searches in the region of the Netherlands.
        jsonstring = places.places(self.client, url, location=(52.388041, 5.403560), radius=50000)
        # Parses the JSON result
        results = self.json_result(jsonstring)
        resultList = []
        if results is not None:
            # Loops through the results and adds all the types of buildings to a list
            for result in results:
                resultList = resultList + [self.get_types(url, result, len(results))]
        if "www" in url or "http" in url:
            # Performs another API call but only with the company name
            resultList = resultList + self.scan_url(self.extract_from_url(url))
        return resultList

    def determine_scope(self, results):
        # Determines if the result makes the website in or out of scope
        for result in results:
            if result is not None:
                for record in result:
                    # Checks if any of the results are a store, if it is it's out of scope
                    if record == "store":
                        # A department store is a exception, so it will still be inscope
                        if "department_store" in result:
                            return 1
                        return 0
                    # Car rentals and lodging are not stores but still out of scope
                    elif record == "car_rental" or record == "lodging":
                        return 0
                # If none of the previous types are found, it does a final check
                if "point_of_interest" in result or "establishment" in result:
                    return 1
        # If there are no results
        return -1
