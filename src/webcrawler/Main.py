import webcrawler
import MongoHelper
from maps import Maps

def start():
    for index in range(0,MongoHelper.getAvailableId()-1) :
        site = MongoHelper.getResultById(index)
        url = site["Url"]
        content = site["Content"]
        result = webcrawler.UrlResult(url)
        spider = webcrawler.Spider(url, content, result)
        result = spider.process()
        print(result)
    end()

def end():
    Maps.start()


