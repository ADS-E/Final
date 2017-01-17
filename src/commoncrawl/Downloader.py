import threading

import lxml.html
from lxml import etree

import requests
import json
import io
import gzip

import MongoHelper

""""Class inheriting a thread responsible for downloading and storing the content found for a url."""


class Downloader(threading.Thread):
    def __init__(self, name, index, queue):
        threading.Thread.__init__(self)
        self.name = name
        self.index = index
        self.queue = queue

    """"Get an url from the queue, process the url and notify the queue the task on the retrieved item is done.
         Continue this process while the queue has items"""

    def run(self):
        while not self.queue.empty():
            url = self.queue.get()

            self.save(url)
            self.queue.task_done()

        print("%s done" % self.name)

    """"Download the url content in html form and save it to MongoDB"""

    def save(self, url):
        try:
            # Download the content
            html_content = download_page(url, self.index)

            # If the content is not empty set the year of the commoncrawl archive the url was retrieved from
            if not html_content.isspace():
                year = int(self.index[:4])
                MongoHelper.insert_URL_info(url, html_content, year)

                print("%s retrieved %d bytes for %s" % (self.name, len(html_content), url))
        except Exception as e:
            print("%s: Url could not be crawled" % self.name)


"""Download a page retrieved by an URL from Common Crawl.
Strip all the html tags from the content to save space in MongoDB"""


def download_page(url, index):
    record = get_record(url, index)
    resp = get_response(record)

    # If the homepage is not found load the live website to automatically get
    # redirected to the home page and try again with this url.
    if resp.status_code == 404:
        fixed = get_fixed_base_url(url)
        record = get_record(fixed, index)

        resp = get_response(record)

    # he page is stored compressed (gzip) to save space
    # it can be extracted by using the GZIP library"""
    raw_data = io.BytesIO(resp.content)
    f = gzip.GzipFile(fileobj=raw_data)

    # What we have now is just the WARC response, formatted:
    data = f.read()

    response = ""

    if len(data):
        warc, header, response = data.decode('latin-1').split('\r\n\r\n', 2)

    # Remove the html elements form the file to only keep the text.
    document = lxml.html.document_fromstring(response)
    content = "\n".join(etree.XPath("//text()")(document))

    return content


""""Get the base URL from a given URL by loading the page and seeing
how the server redirects it to an adjusted URL. This is the fixed base URL"""


def get_fixed_base_url(url):
    request = requests.get(url)
    return request.url


"""""Get the Commoncrawl record from the url"""


def get_record(url, index):
    cc_url = "http://index.commoncrawl.org/CC-MAIN-%s-index?" % index
    cc_url += "url=%s&matchType=domain&output=json" % url

    response = requests.get(cc_url)

    if response.status_code == 200:
        records = response.content.decode('ISO-8859-1').splitlines()
        record = records[0]
        return json.loads(record)

    return None


""""Get the data from the Commoncrawl record"""


def get_response(record):
    offset, length = int(record['offset']), int(record['length'])
    offset_end = offset + length - 1

    # Get the file via HTTPS so we don't need to worry about S3 credentials.
    prefix = 'https://commoncrawl.s3.amazonaws.com/'

    # Use the Range header to ask for just this set of bytes
    resp = requests.get(prefix + record['filename'], headers={'Range': 'bytes={}-{}'.format(offset, offset_end)})

    return resp
