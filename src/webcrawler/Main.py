import CsvHelper
from Crawler import Crawler
from LinkFinder import LinkFinder


def start():
    #for index
    #mongo
    result = UrlResult()
    spider = Spider(url, content, result);

    result  = spider.process()


