import MongoHelper
from list import Specialized
from list.Crawler import Crawler


class Listing:
    def __init__(self, check_scope):
        self.check_scope = check_scope

    def start(self):
        print("---------- Listing Starting Scope: %s ----------" % self.check_scope)

        for id in MongoHelper.getAllIds():
            site = MongoHelper.getResultById(id)

            if site is not None:
                url = site["url"]
                sitename = take_sitename(url)
                csv_file = '../list/csv/scope_certain.csv' if self.check_scope else '../list/csv/webshop_certain.csv'

                result = Crawler(sitename, csv_file).run()

                if self.check_scope:
                    result.set_found(Specialized.check_dagaanbiedingen(sitename))
                else:
                    result.set_found(Specialized.check_winkelsnederland(sitename))

                value = result.get_found()
                site["list"] = value

                print("Listing: %s is: %s" % (url, value))

                MongoHelper.updateInfo(site)

        self.end()

    def end(self):
        print("---------- Listing Ending Scope: %s ----------" % self.check_scope)

        if self.check_scope:
            from ml.ML import ML

            ml = ML(True)
            ml.start()
        else:
            from Decider import Decider

            decider = Decider(False)
            decider.start()


def take_sitename(url):
    return url.split('.')[1]
