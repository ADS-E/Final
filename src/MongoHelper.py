from pymongo import MongoClient
from urllib.request import urlopen

client = MongoClient("mongodb://192.168.10.26:27017/")
db = client["webshops"]
collection = client["information"]
posts = db.information

def insertURLInfo(url, content, year):
    post = {"URL": url, "content": content, "year": year}
    try:
        posts.insert_one(post)
    except:
        print("Failed, server error")


def insertURLInfo(url, content, webshop, inscope, category, meta, address, year):
    id = getAvailableId()
    print(id)
    post = {"id":id, "URL": url, "content": content, "webshop": webshop, "inscope": inscope, "category": category, "meta": meta,
            "address": address, "year": year}
    try:
        posts.insert_one(post)
    except:
        print("Failed, server error")

def getResultByIndex(index):
    return posts.find_one({"id":index})

def getAvailableId():
    return posts.find_one(sort=[("id", -1)])["id"]+1

def getResultByURL(url):
    return posts.find_one({"URL": url})

insertURLInfo("http://www.mediamarkt.", "blabl", "True","True", "none","none","none", 2016)
print(getResultByURL("http://www.mediamarkt"))