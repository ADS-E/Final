from pymongo import MongoClient
from urllib.request import urlopen

client = MongoClient("mongodb://192.168.10.26:27017/")
db = client["webshops"]
collection = client["information"]
posts = db.information


def insertURLInfo(url, content, webshop, inscope, category, meta, address, year):
    id = getAvailableId()
    print(id)
    post = {"id": id, "URL": url, "content": content, "webshop": webshop, "inscope": inscope, "category": category,
            "meta": meta,
            "address": address, "year": year}
    try:
        posts.insert_one(post)
    except:
        print("Failed, server error")


def updateInfo(update):
    id = update['id']
    posts.update({"id": id}, update)


def getResultByIndex(index):
    return posts.find_one({"id": index})


def getAvailableId():
    if posts.find().count() > 0:
        return posts.find_one(sort=[("id", -1)])["id"]
    else:
        return 1

def removeByIndex(index):
    posts.remove({"id": index})

def getResultByURL(url):
    return posts.find_one({"URL": url})
