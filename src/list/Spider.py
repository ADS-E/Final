import re
import threading
import pickle

import lxml.html
import requests
from lxml import etree


class Spider(threading.Thread):
    """"Class used for scanning urls on containing certain words."""

    def __init__(self, name, queue, result):
        threading.Thread.__init__(self)
        self.name = name
        self.sitename = result.get_sitename()
        self.queue = queue
        self.result = result

    def run(self):
        """"Get an url from the queue, process the url and notify the queue the task on the retrieved item is done.
        Continue this process while the queue has items"""
        #print("%s running" % self.name)

        while not self.queue.empty():
            listUrl = self.queue.get()

            self.process(listUrl)
            self.queue.task_done()

    def process(self, listUrl):
        """Count for every word that needs to be checked the amount of times it's found in the page content.
        Add this result to the UrlResult as a key and value pair."""

        try:
            file = open('../list/data/' + listUrl, 'r')

            html = file.read()
            document = lxml.html.document_fromstring(html)
            content = "\n".join(etree.XPath("//text()")(document))

            count = len(re.findall(re.compile(self.sitename, re.IGNORECASE), content))
            found = count != 0

            self.result.set_found(found)
        except Exception as e:
            print(e)

def take_sitename(url):
    s = url.split('.')
    x = s[len(s) - 2] + "." + s[len(s) - 1]

    if 'http://' in x:
        x = x[7:]
    if 'https://' in x:
        x = x[8:]


    return x.split('/')[0].split('.')[0]



