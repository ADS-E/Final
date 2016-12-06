import MongoHelper


def dicide(url):
    for index in range(0, MongoHelper.getAvailableId() - 1):
        site = MongoHelper.getResultByIndex(index)

        if site is not None:
            url = site["Url"]
