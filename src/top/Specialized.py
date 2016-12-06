from lxml import html
import requests


def check_winkelsnederland(sitename):
    page = requests.get('http://www.winkels-nederland.nl/')
    tree = html.fromstring(page.content)
    stores = []

    options = tree.xpath('//select[@id="winkel_select"]/option')
    for option in options:
        stores.append(option.text)

    return sitename.upper() in (name.upper() for name in stores)


def check_dagaanbiedingen(sitename):
    page = requests.get('http://www.dagaanbiedingen.nl/webwinkels.html')
    tree = html.fromstring(page.content)
    stores = []

    for link in tree.xpath('//a[@class="more"]'):
        s = link.get('href')
        stores.append(s[40:].split('.')[0])

    return sitename.upper() in (name.upper() for name in stores)