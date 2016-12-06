import googlemaps
from urllib.parse import urlparse
import pandas as pd
import re
import json as js
import time
from googlemaps import places
import UrlInfo
import csv

client = googlemaps.Client(key="AIzaSyCuBnzZ6K_wHln6EFY4VuJ-Jw03yNeL38c")
allresults = {}
url_address = ""

def getUrls(file):
    data = pd.read_csv(file,engine="python")
    urllink = data["URL"]
    return urllink

def extractFromUrl(url):
    m = re.search('www.([^.]+).+', url)
    if m is None:
        m = re.search('\/.([^.]+).+', url)
    return m.group(1)

def jsonImport(filename):
    with open(filename, 'r') as myfile:
        data=myfile.read().replace('\n', '')
    return data

def jsonResult(result):
    if result["status"] != "ZERO_RESULTS" :
        try:
            result = result["results"][:5:]
        except KeyError:
            print("No types, getting name")
        return result

def checkDetails(url,placeid):
    details = places.place(client, placeid)
    result = details["result"]
    try:
        result_website = result["website"]
        if result_website is not None:
            currentUrl = url
            if "www" in currentUrl:
                currentUrl = extractFromUrl(currentUrl)
            if currentUrl == extractFromUrl(result_website):
                result_address = result["formatted_address"]
                return result_address
        return None
    except KeyError:
        return None

def getTypes(url,dict):
    address = checkDetails(url,dict["place_id"])
    if address is not None:
        global url_address
        url_address = address
        try:
            result = dict["types"]
        except KeyError:
            print("No types, getting name..")
            result = dict["name"]
        return result

def scanURL(url):
    jsonstring = places.places(client,url,location=(52.388041, 5.403560),radius=50000)
    results = jsonResult(jsonstring)
    resultList = []
    if results is not None:
        for result in results:
            resultList = resultList + [getTypes(url,result)]
    if "www" in url:
        resultList = resultList + scanURL(extractFromUrl(url))
    return resultList

def determineScope(results):
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

urlList = getUrls("withinscope_new.csv")
for url in urlList:
    results = scanURL(url)
    inscope = determineScope(results)
    print(url)
    print(url_address)
    print(results)
    print(inscope)
    results = [url_address] + [inscope] + results
    print(results)
    allresults[url] = results
    url_address = ""

with open('resultsWithinScopeAddress.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["URL", "Address", "In-scope", "Types"])
    for key, value in allresults.items():
        writer.writerow([key, value[0],value[1], value[2::]])