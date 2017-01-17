import threading

import numpy as np

import MongoHelper
from helpers import MLHelper
from webcrawler.Spider import Spider

""""Class inheriting a thread responsible for running the machine learning process"""


class CategoryProcessor(threading.Thread):
    def __init__(self, name, clf, queue, mapping):
        threading.Thread.__init__(self)
        self.name = name
        self.clf = clf
        self.queue = queue
        self.mapping = mapping

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
        site = MongoHelper.get_result_by_id(id)
        url = site['url']
        content = site['content']

        spider = Spider(url, content, '../category/csv/words.csv')
        result = spider.process()

        if result is not None:
            result.set_page_count(1)

            list = MLHelper.remove_columns(result.csv_format())
            data = np.reshape(list, (1, -1))
            predicted = self.get_label_text(self.clf.predict(data)[0])

            print("%s predicted for %s" % (predicted, url))

            site['category'] = predicted
            MongoHelper.update_value(site, 'category')

    def get_label_text(self, label):
        label = str(label)
        return self.mapping[label]
