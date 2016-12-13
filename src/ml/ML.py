from sklearn.externals import joblib
from sklearn.naive_bayes import MultinomialNB

import os.path
import numpy as np

import MongoHelper
from helpers import MLHelper
from ml import SetsHelper
from webcrawler.Spider import Spider


class ML:
    def __init__(self, check_scope):
        self.check_scope = check_scope

    def start(self):
        print("asdf: %s" % MongoHelper.count())
        print("---------- ML Starting Scope: %s ----------" % self.check_scope)

        plk = 'scope.pkl' if self.check_scope else 'webshop.pkl'

        if os.path.isfile(plk):
            clf = joblib.load(plk)
        else:
            clf = self.build_classifier()

        nr_of_items = MongoHelper.count()
        print("Nr of items: %s" % nr_of_items)
        for id in range(1, nr_of_items):
            site = MongoHelper.getResultByIndex(id)
            url = site['url']
            content = site['content']

            spider = Spider(url, content)
            result = spider.process()
            result.set_page_count(1)

            list = MLHelper.divide_one('PageCount', result.csv_format())
            data = np.reshape(list, (1, -1))

            predicted = np.asscalar(clf.predict(data)[0])
            print("%s predicted: %s" % (url, predicted))

            if self.check_scope:
                site['webshop'] = predicted
            else:
                site['inscope'] = predicted

            MongoHelper.updateInfo(site)

        joblib.dump(clf, plk)
        self.end()

    def end(self):
        print("---------- ML Ending Scope: %s ----------" % self.check_scope)
        from list.Listing import Listing

        if not self.check_scope:
            listing = Listing(False)
            listing.start()

    def build_classifier(self):
        if self.check_scope:
            data = MLHelper.get_data()
        else:
            data = MLHelper.get_data()

        X_train, X_test, y_train, y_test = SetsHelper.create_sets(data)

        clf = MultinomialNB(alpha=0, fit_prior=False)
        clf.fit(X_train, y_train)

        return clf


ml = ML(False)
ml.start()
