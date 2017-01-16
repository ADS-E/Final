import googlemaps
import pandas as pd
import re
import MongoHelper

from googlemaps import places


class Maps:
    def __init__(self):
        # This is needed to connect with the Google Maps API. The key is a generated key by Google specific for this application.
        self.client = googlemaps.Client(key="AIzaSyCuBnzZ6K_wHln6EFY4VuJ-Jw03yNeL38c")

    def start(self):
        print("---------- Maps Starting ----------")
        # Looping through all currently present id's in MongoDB
        for id in MongoHelper.getAllIds():
            # Getting a document with the given id
            site = MongoHelper.getResultById(id)
            if site is not None:
                # Scanning for the type of building connected to a given URL
                results = self.scan_url(site["url"])
                # Determining if the website is within or out of scope given the type of building it returned
                inscope = self.determine_scope(results)
                # Grouping all results together
                results = [self.url_address] + [inscope] + results

                printable = "Empty" if inscope == -1 else bool(inscope)
                print("Maps: %s is: %s" % (site['url'], printable))
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
                MongoHelper.updateInfo(site)
        self.end()

    def end(self):
        print("---------- Maps Ending ----------")

        from ml.ML import ML

        ml = ML(True)
        ml.start()

        # from list.Listing import Listing
        # # Starts the Listing part of the application that predicts in or out of scope
        # listing = Listing(True)
        # listing.start()

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
            # Gets the website from the results
            result_website = None
            if("website" in result):
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
        address = self.check_details(url, dict["place_id"],resultCount)
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
