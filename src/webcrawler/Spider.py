import re
import threading

import lxml.html
from lxml import etree

from helpers import CsvHelper
from webcrawler.UrlResult import UrlResult

""""Class used for scanning urls on containing certain words."""


class Spider:
    """"Retrieves the words to look for from a file with the given file path"""

    def __init__(self, url, content, path):
        self.url = url
        self.content = content
        self.result = UrlResult(url)
        self.words = CsvHelper.read_file(path)

    """Count for every word that needs to be checked the amount of times it's found in the page content.
       Add this result to the UrlResult as a key and value pair."""

    def process(self):

        try:
            html = self.content
            if html.isspace():
                return None
            else:
                document = lxml.html.document_fromstring(html)
                content = "\n".join(etree.XPath("//text()")(document))

                word_count = len(content.split())
                self.result.set_word_count(word_count)

                # For every word count the occurrences
                for word in self.words:
                    count = len(re.findall(re.compile(word, re.IGNORECASE), content))
                    self.result.put(word, count)

                return self.result
        except Exception as e:
            print(e)
