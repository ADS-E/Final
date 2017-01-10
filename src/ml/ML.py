from sklearn.externals import joblib
from sklearn.naive_bayes import MultinomialNB

import os.path
import numpy as np

import MongoHelper
from helpers import MLHelper
from ml import SetsHelper
from webcrawler.Spider import Spider

""""Class used to feed the found websites through the Machine Learning algorithms"""
class ML:
    def __init__(self, check_scope):
        self.check_scope = check_scope

    """Get the Naive Bayes classifier or if it doesn't exist create one.
    For all the entries in MongoDB get the html content. Run this content through the spider
    to get the word occurences. Feed this data through the algorithm and save the result to the
    'ml' parameter of the entry in MongoDB"""
    def start(self):
        print("---------- ML Starting Scope: %s ----------" % self.check_scope)

        plk = 'scope.pkl' if self.check_scope else 'webshop.pkl'

        if os.path.isfile(plk):
            clf = joblib.load(plk)
        else:
            clf = self.build_classifier()

        print("Nr of items: %s" % MongoHelper.count())
        for id in MongoHelper.getAllIds():
            site = MongoHelper.getResultById(id)
            url = site['url']
            content = site['content']

            spider = Spider(url, content)
            result = spider.process()
            predicted = False

            if result is not None:
                result.set_page_count(1)

                list = MLHelper.divide_one('PageCount', result.csv_format())
                data = np.reshape(list, (1, -1))

                predicted = bool(np.asscalar(clf.predict(data)[0]))

                print("%s predicted: %s" % (url, predicted))

            if self.check_scope:
                site['webshop'] = predicted
            else:
                site['scope'] = predicted

            MongoHelper.updateInfo(site)

        joblib.dump(clf, plk)
        self.end()

    """"End the Machine Learning by starting the Decider or the Listing"""
    def end(self):
        print("---------- ML Ending Scope: %s ----------" % self.check_scope)

        if self.check_scope:
            from Decider import Decider

            decider = Decider(True)
            decider.start()
        else:
            from list.Listing import Listing

            listing = Listing(False)
            listing.start()

    """"Create the classifier by getting the scope or the webshop
     data depending on what the machine learning has to decide. After that fit it with the data"""
    def build_classifier(self):
        if self.check_scope:
            data = MLHelper.get_scope_data()
        else:
            data = MLHelper.get_webshop_data()

        X_train, X_test, y_train, y_test = SetsHelper.create_sets(data)

        clf = GaussianNB()
        clf.fit(X_train, y_train)

        return clf

