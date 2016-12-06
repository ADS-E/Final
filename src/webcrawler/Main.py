
import MongoHelper

def start():
    for index in range (0,mongocollectionsize) :
        mongodict = MongoHelper.getResultByIndex(index)
        url = mongodict["Url"]
        content = mongodict["Content"]
        result = UrlResult(url)
        spider = Spider(url, content, result)
        result = spider.process()
        print(result)


