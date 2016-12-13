import googlemaps
import pandas as pd
import re
import MongoHelper

from googlemaps import places


class Maps:
    def __init__(self):
        self.client = googlemaps.Client(key="AIzaSyCuBnzZ6K_wHln6EFY4VuJ-Jw03yNeL38c")
        self.allresults = {}
        self.url_address = ""

    def start(self):
        print("---------- Maps Starting ----------")

        for index in range(0, MongoHelper.getAvailableId() - 1):
            site = MongoHelper.getResultByIndex(index)
            if site is not None:
                results = self.scan_url(site["URL"])
                inscope = self.determine_scope(results)
                results = [url_address] + [inscope] + results
                self.allresults[site["URL"]] = results
                url_address = ""
                site["maps"] = inscope
                MongoHelper.updateInfo(site["id"], site)

    def end(self):
        print("---------- Maps Starting ----------")

        from list.Listing import Listing

        listing = Listing(True)
        listing.start()

    def get_urls(self, file):
        data = pd.read_csv(file, engine="python")
        urllink = data["URL"]
        return urllink

    def extract_from_url(self, url):
        m = re.search('www.([^.]+).+', url)
        if m is None:
            m = re.search('\/.([^.]+).+', url)
        return m.group(1)

    def json_import(self, filename):
        with open(filename, 'r') as myfile:
            data = myfile.read().replace('\n', '')
        return data

    def json_result(self, result):
        if result["status"] != "ZERO_RESULTS":
            try:
                result = result["results"][:5:]
            except KeyError:
                print("No types, getting name")
            return result

    def check_details(self, url, placeid):
        details = places.place(self.client, placeid)
        result = details["result"]
        try:
            result_website = result["website"]
            if result_website is not None:
                currentUrl = url
                if "www" in currentUrl:
                    currentUrl = self.extract_from_url(currentUrl)
                if currentUrl == self.extract_from_url(result_website):
                    result_address = result["formatted_address"]
                    return result_address
            return None
        except KeyError:
            return None

    def get_types(self, url, dict):
        address = self.check_details(url, dict["place_id"])
        if address is not None:
            global url_address
            url_address = address
            try:
                result = dict["types"]
            except KeyError:
                print("No types, getting name..")
                result = dict["name"]
            return result

    def scan_url(self, url):
        jsonstring = places.places(self.client, url, location=(52.388041, 5.403560), radius=50000)
        results = self.json_result(jsonstring)
        resultList = []
        if results is not None:
            for result in results:
                resultList = resultList + [self.get_types(url, result)]
        if "www" in url:
            resultList = resultList + self.scan_url(self.extract_from_url(url))
        return resultList

    def determine_scope(self, results):
        for result in results:
            if result != None:
                for record in result:
                    if record == "store":
                        if "department_store" in result:
                            return 1
                        return 0
                    elif record == "car_rental" or record == "lodging":
                        return 0
                if "point_of_interest" in results or "establishment" in results:
                    return 1
        return -1
