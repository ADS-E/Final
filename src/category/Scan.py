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
    def __init__(self):
        self.mapping = CsvHelper.get_classification_names()

    """Count for every word that needs to be checked the amount of times it's found in the page content.
      Add this result to the UrlResult as a key and value pair."""
    def start(self):
        print("---------- Category Determination Starting ----------")

        plk = 'category.pkl'

        if os.path.isfile(plk):
            clf = joblib.load(plk)
        else:
            clf = self.build_classifier()

        print("Number of items to analyse: %s" % MongoHelper.count())
        for id in MongoHelper.get_all_Ids():
            site = MongoHelper.get_result_by_id(id)
            url = site['url']
            content = site['content']

            spider = Spider(url, content, '../category/csv/words.csv')
            result = spider.process()

            if result is not None:
                result.set_page_count(1)

                list = MLHelper.remove_columns(result.csv_format())
                data = np.reshape(list, (1, -1))
                predicted = self.get_label_text(clf.predict(data)[0])

                print("%s predicted for %s" % (predicted, url))

                site['category'] = predicted
                MongoHelper.update_value(site, 'category')


    def build_classifier(self):
        data = MLHelper.get_classify_data()

        X_train, X_test, y_train, y_test = SetsHelper.create_sets(data)

        clf = GaussianNB()
        clf.fit(X_train, y_train)

        return clf

    def get_label_text(self, label):
        label = str(label)
        return self.mapping[label]



