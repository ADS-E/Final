from top import Specialized
from top.Crawler import Crawler


def start():
    for url in CsvHelper.read_file('webshops.csv'):
        sitename = take_sitename(url)

        result = Crawler(sitename, 'csv/webshop_certain.csv').run()
        result.set_found(Specialized.check_winkelsnederland(sitename))
        result.set_found(Specialized.check_dagaanbiedingen(sitename))


        print(result.get_found())

        print("Done")

def take_sitename(url):
    splitter = url.split('.')[0]
    return splitter[len(splitter) - 2]

#def end():
    #ml
