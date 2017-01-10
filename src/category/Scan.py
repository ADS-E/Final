from sklearn.externals import joblib
from sklearn.naive_bayes import GaussianNB

import MongoHelper
from helpers import MLHelper
from ml import SetsHelper
from helpers import CsvHelper

import numpy as np
import os.path

from webcrawler.Spider import Spider

class Scan:

    """Count for every word that needs to be checked the amount of times it's found in the page content.
      Add this result to the UrlResult as a key and value pair."""
    def start(self):
        print("---------- Category Determination Starting ----------")

        plk = 'category.pkl'

        if os.path.isfile(plk):
            clf = joblib.load(plk)
        else:
            clf = self.build_classifier()

        for id in MongoHelper.getAllIds():
            site = MongoHelper.getResultById(id)
            url = site['url']
            content = site['content']

            spider = Spider(url, content, '../category/csv/words.csv')
            result = spider.process()

            if result is not None:
                result.set_page_count(1)

                list = MLHelper.divide_one('PageCount', result.csv_format())
                data = np.reshape(list, (1, -1))

            MongoHelper.updateInfo(site)


    def build_classifier(self):
        data = CsvHelper.classify_divide_by()

        X_train, X_test, y_train, y_test = SetsHelper.create_sets(data)

        clf = GaussianNB()
        clf.fit(X_train, y_train)

        return clf






