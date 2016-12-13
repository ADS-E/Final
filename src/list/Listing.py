import MongoHelper
from list import Specialized
from list.Crawler import Crawler


class Listing:
    def __init__(self, check_scope):
        self.check_scope = check_scope

    def start(self):
        print("---------- Listing Starting Scope: %s ----------" % self.check_scope)

        for index in range(0, MongoHelper.getAvailableId() - 1):
            site = MongoHelper.getResultByIndex(index)

            if site is not None:
                url = site["url"]
                sitename = take_sitename(url)
                csv_file = 'csv/scope_certain.csv' if self.check_scope else 'csv/webshop_certain.csv'

                result = Crawler(sitename, csv_file).run()

                if self.check_scope:
                    result.set_found(Specialized.check_dagaanbiedingen(sitename))
                else:
                    result.set_found(Specialized.check_winkelsnederland(sitename))

                in_scope = result.get_found()
                site["list"] = in_scope

                MongoHelper.updateInfo(site)

        self.end()

    def end(self):
        print("---------- Listing Starting Scope: %s ----------" % self.check_scope)

        from ml.ML import ML
        from maps.Maps import Maps

        if self.check_scope:
            ml = ML(True)
            ml.start()
        else:
            maps = Maps()
            maps.start()


def take_sitename(url):
    splitter = url.split('.')[0]
    return splitter[len(splitter) - 2]
