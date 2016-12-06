from pymongo import MongoClient
from urllib.request import urlopen

client = MongoClient("mongodb://192.168.10.26:27017/")
db = client["webshops"]
collection = client["information"]
posts = db.information


def insertURLInfo(url, content, year):
    id = getAvailableId()
    print(id)
    post = {"id": id, "URL": url, "content": content, "webshop": False, "inscope": False, "category": '',
            "meta": '',
            "address": '', "year": year, "maps": 0, "list": False, "ml": False}
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


def getResultByURL(url):
    return posts.find_one({"URL": url})
