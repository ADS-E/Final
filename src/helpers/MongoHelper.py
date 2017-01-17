from pymongo import MongoClient
from urllib.request import urlopen

""""Class responsible for handling the MongoDB connection"""

# Creates a client to connect to the MongoDB with the given IP and port
client = MongoClient("mongodb://192.168.10.26:27017/")
# Defines the database we will use
db = client["webshops"]
# Defines the collection we will use
posts = db.information

"""Inserts a document into MongoDB using the given data"""


def insert_URL_info(url, content, year):
    # Checks for an available id
    id = get_available_id()
    print(id)
    # Creates a dictionary with the data
    post = {"id": id, "url": url, "content": content, "webshop": False, "scope": False, "category": '',
            "meta": '',
            "address": '', "year": year, "maps": 0, "list": False, "ml": False}
    try:
        # Inserts the data into MongoDB
        posts.insert_one(post)
    except:
        print("Failed, server error")


"""Updates a document in MongoDB"""


def update_info(update):
    id = update['id']
    # Updates a specific document with the new data
    posts.update({"id": id}, update)


"""Update only one attribute of a document in MongoDB"""


def update_value(update, value):
    id = update['id']
    # Updates a specific document with the new data
    posts.update({'id': id}, {'$set': {value: update[value]}})


"""Get one document by the id"""


def get_result_by_id(id):
    # Gets a document given an id
    return posts.find_one({"id": id})


"""Get the next id available"""


def get_available_id():
    if posts.find().count() > 0:
        # Sorts the id's in mongodb from high to low, get the top results, adds 1 to it and returns it
        return posts.find_one(sort=[("id", -1)])["id"] + 1
    else:
        # If there are no documents returns 1
        return 1


"""Get all ids that are currently present in the database"""


def get_all_Ids():
    ids = []
    # Find all id's in MongoDB
    for x in posts.find({}, {"_id": 0, "id": 1}):
        ids.append(x['id'])

    return ids


"""Remove document by id"""


def remove_by_id(index):
    # Removes a post given a id
    posts.remove({"id": index})


"""Count the amount of documents in MongoDB"""


def count():
    return posts.find().count()
