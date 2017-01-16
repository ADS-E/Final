import threading

import numpy as np
import time

import MongoHelper
from helpers import MLHelper
from webcrawler.Spider import Spider


class MLProcessor(threading.Thread):
    """"Class used for scanning urls on containing certain words."""

    def __init__(self, name, clf, queue, check_scope):
        threading.Thread.__init__(self)
        self.name = name
        self.clf = clf
        self.queue = queue
        self.check_scope = check_scope

    def run(self):
        """"Get an url from the queue, process the url and notify the queue the task on the retrieved item is done.
        Continue this process while the queue has items"""

        while not self.queue.empty():
            id = self.queue.get()

            self.process(id)
            self.queue.task_done()

        print("%s done" % self.name)

    def process(self, id):
        startTotal = time.process_time()

        site = MongoHelper.getResultById(id)
        url = site['url']
        content = site['content']

        spider = Spider(url, content, '../webcrawler/words.csv')
        result = spider.process()
        predicted = False

        if result is not None:
            result.set_page_count(1)

            list = MLHelper.remove_columns(result.csv_format())
            data = np.reshape(list, (1, -1))

            predicted = bool(np.asscalar(self.clf.predict(data)[0]))

            message = "Scope vs No-scope" if self.check_scope else "Website vs Webshop"
            print("%s predicted: %s for %s as %s" % (self.name, predicted, url, message))

        if self.check_scope:
            site['webshop'] = predicted
        else:
            site['scope'] = predicted

            #startMongo = time.process_time()
            MongoHelper.updateValue(site, 'ml')

            #endMongo = time.process_time()
            endTotal = time.process_time()

            #resultMongo = endMongo - startMongo
            resultTotal = endTotal - startTotal

           # print("Mongo: %s" % resultMongo)
            print("Total: %s" % resultTotal)
