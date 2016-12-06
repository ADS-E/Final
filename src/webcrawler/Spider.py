import re
from lxml import etree

import requests
import threading
import lxml.html

import CsvHelper


class Spider(threading.Thread):
    """"Class used for scanning urls on containing certain words."""

    def __init__(self, url, content, result):
        threading.Thread.__init__(self)
        self.url = url
        self.content = content
        self.result = result
        self.words = CsvHelper.read_file('words.csv')

    def process(self):
        """Count for every word that needs to be checked the amount of times it's found in the page content.
        Add this result to the UrlResult as a key and value pair."""

        try:
            html = self.content
            document = lxml.html.document_fromstring(html)
            content = "\n".join(etree.XPath("//text()")(document))

            word_count = len(content.split())
            self.result.set_word_count(word_count)

            for word in self.words:
                count = len(re.findall(re.compile(word, re.IGNORECASE), content))
                self.result.put(word, count)
        except Exception as e:
            print(e)


