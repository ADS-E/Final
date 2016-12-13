from pymongo import MongoClient
from urllib.request import urlopen

client = MongoClient("mongodb://192.168.10.26:27017/")
db = client["webshops"]
collection = client["information"]
posts = db.information


def insertURLInfo(url, content, year):
    id = getAvailableId()
    print(id)
    post = {"id": id, "url": url, "content": content, "webshop": False, "scope": False, "category": '',
            "meta": '',
            "address": '', "year": year, "maps": 0, "list": False, "ml": False}
    try:
        posts.insert_one(post)
    except:
        print("Failed, server error")


def updateInfo(update):
    id = update['id']
    posts.update({"id": id}, update)


def getResultById(id):
    return posts.find_one({"id": id})


def getAvailableId():
    if posts.find().count() > 0:
        return posts.find_one(sort=[("id", -1)])["id"] + 1
    else:
        return 1

def getAllIds():
    ids = []
    for x in posts.find({}, {"_id": 0, "id": 1}):
        ids.append(x['id'])

    return ids

def removeByIndex(index):
    posts.remove({"id": index})

def getResultByURL(url):
    return posts.find_one({"url": url})


def count():
    return posts.find().count()
