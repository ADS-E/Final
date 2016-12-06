import googlemaps
import pandas as pd
import re
import csv

from googlemaps import places

from list.List import List


class Maps:
    def __init__(self):
        self.client = googlemaps.Client(key="AIzaSyCuBnzZ6K_wHln6EFY4VuJ-Jw03yNeL38c")
        self.allresults = {}
        self.url_address = ""

    def start(self):
        urlList = self.get_urls("withinscope_new.csv")
        for url in urlList:
            results = self.scan_url(url)
            inscope = self.determine_scope(results)
            print(url)
            print(url_address)
            print(results)
            print(inscope)
            results = [url_address] + [inscope] + results
            print(results)
            self.allresults[url] = results
            url_address = ""

    def end(self):
        with open('resultsWithinScopeAddress.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["URL", "Address", "In-scope", "Types"])
            for key, value in self.allresults.items():
                writer.writerow([key, value[0], value[1], value[2::]])

        list = List(True)
        list.start()

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
        return 1
