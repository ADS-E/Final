import multiprocessing
import os.path
from queue import Queue

from sklearn.externals import joblib
from sklearn.naive_bayes import GaussianNB

from category.CategoryProcessor import CategoryProcessor
from helpers import FileHelper, SetsHelper
from helpers import MLHelper, MongoHelper
from ml import SetsHelper


class Scan:
    def __init__(self):
        self.mapping = FileHelper.get_classification_names()
        self.queue = Queue()
        self.threads = []
        self.clf = None

    """Count for every word that needs to be checked the amount of times it's found in the page content.
      Add this result to the UrlResult as a key and value pair."""

    def start(self):
        print("---------- Category Determination Starting ----------")

        plk = 'category.pkl'

        if os.path.isfile(plk):
            self.clf = joblib.load(plk)
        else:
            self.clf = build_classifier()
            joblib.dump(self.clf, plk)

        print("Number of items to analyse: %s" % MongoHelper.count())
        [self.queue.put(id) for id in MongoHelper.get_all_Ids()]

        self.create_threads()

        for t in self.threads:
            t.join()

    """"Create a number of threads based on the host available amount of threads.
       These threads run an instance of the MLProcessor class"""

    def create_threads(self):
        # Creates threads and add them to a list.
        for i in range(1, multiprocessing.cpu_count()):
            name = "Thread-%s" % i
            thread = CategoryProcessor(name, self.clf, self.queue, self.mapping)
            thread.start()
            self.threads.append(thread)


def build_classifier():
    data = MLHelper.get_classify_data()

    X_train, X_test, y_train, y_test = SetsHelper.create_sets(data)

    clf = GaussianNB()
    clf.fit(X_train, y_train)

    return clf
