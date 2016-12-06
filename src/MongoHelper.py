from pymongo import MongoClient
from urllib.request import urlopen

client = MongoClient("mongodb://145.93.174.51:27017/")
db = client["webshops"]
collection = client["information"]
posts = db.information

def insertURLInfo2(url, content, year):
    post = {"URL": url, "content": content, "year": year}
    try:
        posts.insert_one(post)
    except:
        print("Failed, server error")


def insertURLInfo(url, content, webshop, inscope, category, meta, address, year):
    post = {"URL": url, "content": content, "webshop": webshop, "inscope": inscope, "category": category, "meta": meta,
            "address": address, "year": year}
    try:
        posts.insert_one(post)
    except:
        print("Failed, server error")


def getResultByURL(url):
    return posts.find_one({"URL": url})
