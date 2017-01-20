import re
import threading

import lxml.html
from lxml import etree

""""Class used for scanning urls on containing certain words."""


class Spider(threading.Thread):
    def __init__(self, name, queue, result):
        threading.Thread.__init__(self)
        self.name = name
        self.sitename = result.get_sitename()
        self.queue = queue
        self.result = result

    """"Get an url from the queue, process the url and notify the queue the task on the retrieved item is done.
         Continue this process while the queue has items"""

    def run(self):
        while not self.queue.empty():
            url = self.queue.get()

            self.process(url)
            self.queue.task_done()

    """Count for every word that needs to be checked the amount of times it's found in the page content.
    Add this result to the UrlResult as a key and value pair. The page content is stored locally
    and thus retrieved with a path to a file"""

    def process(self, url):
        try:
            file = open('../list/data/' + url, 'r')

            html = file.read()
            document = lxml.html.document_fromstring(html)
            content = "\n".join(etree.XPath("//text()")(document))

            # Count the amount of times the sitename is found
            count = len(re.findall(re.compile(self.sitename, re.IGNORECASE), content))
            found = count != 0

            self.result.set_found(found)
        except Exception as e:
            print(e)
