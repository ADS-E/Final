from helpers import MongoHelper
from list import Specialized
from list.Crawler import Crawler

""""Class used to scan sites that have datasets about exisitng webshops in the Netherlands.
This data can be uses to see if a website is a webshop if it is found in that site"""


class Listing:
    def __init__(self, check_scope):
        self.check_scope = check_scope

    """"For all the entries in MongoDB get the name of the website and run in through the scannable sites.
    If the name is found set the 'list' parameter of the entry in MongoDB to true"""

    def start(self):
        print("---------- Listing Starting Scope: %s ----------" % self.check_scope)

        # Loop though all the found items in MongoDB
        for id in MongoHelper.get_all_Ids():
            site = MongoHelper.get_result_by_id(id)

            if site is not None:
                # Get the sites that have to be checked on listing depending on
                #  if Website vs Webshop or Scope vs no-Scope needs to be checked.
                url = site["url"]
                sitename = take_sitename(url)
                csv_file = '../list/csv/scope_certain.csv' if self.check_scope else '../list/csv/webshop_certain.csv'

                # Start the crawling process
                result = Crawler(sitename, csv_file).run()

                if self.check_scope:
                    result.set_found(Specialized.check_dagaanbiedingen(sitename))
                else:
                    result.set_found(Specialized.check_winkelsnederland(sitename))

                value = result.get_found()
                site["list"] = value

                print("Listing: %s is: %s" % (url, value))

                # Save the result to MongoDB
                MongoHelper.update_value(site, 'list')

        self.end()

    """"End the Listing part by starting ML or The Decider"""

    def end(self):
        print("---------- Listing Ending Scope: %s ----------" % self.check_scope)

        if self.check_scope:
            from ml.ML import ML

            ml = ML(True)
            ml.start()
        else:
            from decision.Decider import Decider

            decider = Decider(False)
            decider.start()


""""Get the stie name from the URL. So www.mediamarkt.nl becomes mediamarkt.nl"""


def take_sitename(url):
    s = url.split('.')
    x = s[len(s) - 2] + "." + s[len(s) - 1]

    if 'http://' in x:
        x = x[7:]
    if 'https://' in x:
        x = x[8:]

    return x
