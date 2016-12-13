from sklearn.externals import joblib
from sklearn.naive_bayes import MultinomialNB

import MongoHelper
from helpers import MLHelper
from list.Listing import Listing
from ml import SetsHelper
from webcrawler.Spider import Spider


class ML:
    def __init__(self, check_scope):
        self.check_scope = check_scope

    def start(self):
        print("---------- ML Starting Scope: %s ----------" % self.check_scope)

        plk = 'scope.pkl' if self.check_scope else 'webshop.pkl'
        clf = joblib.load(plk)

        if clf is None:
            clf = self.build_classifier()

        for index in range(0, MongoHelper.getAvailableId() - 1):
            site = MongoHelper.getResultByIndex(index)
            url = site['url']
            content = site['content']

            spider = Spider(url, content)
            result = spider.process()

            list = MLHelper.divide_one('PageCount', result.csv_format())

            value = clf.predict(list)
            print(value)

            if self.check_scope:
                site['webshop'] = value
            else:
                site['inscope'] = value

            MongoHelper.updateInfo(site)
            self.end()

    def end(self):
        print("---------- ML Ending Scope: %s ----------" % self.check_scope)

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
