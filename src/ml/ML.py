import multiprocessing
import os.path
from queue import Queue

from sklearn.externals import joblib
from sklearn.naive_bayes import GaussianNB

from helpers import MLHelper, MongoHelper, SetsHelper
from ml.MLProcessor import MLProcessor

""""Class used to feed the found websites through the Machine Learning algorithms"""


class ML:
    def __init__(self, check_scope):
        self.check_scope = check_scope
        self.queue = Queue()
        self.threads = []
        self.clf = None

    """Get the Naive Bayes classifier or if it doesn't exist create one.
    For all the entries in MongoDB get the html content. Run this content through the spider
    to get the word occurrences. Feed this data through the algorithm and save the result to the
    'ml' parameter of the entry in MongoDB"""

    def start(self):
        print("---------- ML Starting Scope: %s ----------" % self.check_scope)

        plk = 'scope.pkl' if self.check_scope else 'webshop.pkl'

        if os.path.isfile(plk):
            self.clf = joblib.load(plk)
        else:
            self.clf = self.build_classifier()
            joblib.dump(self.clf, plk)

        print("Number of items to analyse: %s" % MongoHelper.count())
        [self.queue.put(id) for id in MongoHelper.get_all_Ids()]

        self.create_threads()

        for t in self.threads:
            t.join()

        self.end()

    """"Create a number of threads based on the host available amount of threads.
    These threads run an instance of the MLProcessor class"""

    def create_threads(self):
        # Creates threads and add them to a list.
        for i in range(1, multiprocessing.cpu_count()):
            name = "Thread-%s" % i
            thread = MLProcessor(name, self.clf, self.queue, self.check_scope)
            thread.start()
            self.threads.append(thread)

    """"End the Machine Learning by starting the Decider or the Listing"""

    def end(self):
        print("---------- ML Ending Scope: %s ----------" % self.check_scope)

        if self.check_scope:
            from decision.Decider import Decider

            decider = Decider(True)
            decider.start()
        else:
            from list.Listing import Listing

            listing = Listing(False)
            listing.start()

    """"Create the classifier by getting Website vs Webshop or Scope vs No-scope
     data depending on what the machine learning has to decide. After that fit it with the data"""

    def build_classifier(self):
        if self.check_scope:
            data = MLHelper.get_scope_data()
        else:
            data = MLHelper.get_webshop_data()

        # Create train test split
        X_train, X_test, y_train, y_test = SetsHelper.create_sets(data)

        clf = GaussianNB()
        clf.fit(X_train, y_train)

        return clf
