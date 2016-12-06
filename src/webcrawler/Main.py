def start():
    #for index
    #mongo
    result = UrlResult()
    spider = Spider(url, content, result);

    result  = spider.process()


