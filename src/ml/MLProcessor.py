import threading

import numpy as np

from helpers import MLHelper, MongoHelper
from webcrawler.Spider import Spider

""""Class inheriting a thread responsible for running the machine learning process"""


class MLProcessor(threading.Thread):
    def __init__(self, name, clf, queue, check_scope):
        threading.Thread.__init__(self)
        self.name = name
        self.clf = clf
        self.queue = queue
        self.check_scope = check_scope

    """"Get an id from the queue, process the id and notify the queue the task on the retrieved item is done.
    Continue this process while the queue has items"""

    def run(self):
        while not self.queue.empty():
            id = self.queue.get()

            self.process(id)
            self.queue.task_done()

        print("%s done" % self.name)

    """Scan the item retrieved by the given id, run in through the machine learning algorithm and
    save the result"""

    def process(self, id):
        # Get from mongoDB
        site = MongoHelper.get_result_by_id(id)
        url = site['url']
        content = site['content']

        # Crawl the site content and count the words
        spider = Spider(url, content, '../webcrawler/csv/words.csv')
        result = spider.process()

        if result is not None:
            result.set_page_count(1)

            # Predictions
            list = MLHelper.remove_columns(result.csv_format())
            data = np.reshape(list, (1, -1))

            predicted = bool(np.asscalar(self.clf.predict(data)[0]))

            message = "Scope vs No-scope" if self.check_scope else "Website vs Webshop"
            print("%s predicted: %s for %s as %s" % (self.name, predicted, url, message))

            site['ml'] = predicted
            MongoHelper.update_value(site, 'ml')
