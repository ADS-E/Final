import lxml.html
from lxml import etree

import requests
import json
import io
import gzip
import sys
import imp
import MongoHelper

from urllib.parse import urlparse


class CommonCrawl:
    def __init__(self):
        imp.reload(sys)
        self.domain = '.nl'
        self.index_list = ["2015-27"]

    def start(self):
        print("---------- CommonCrawl Starting ----------")

        record_list = self.search_domain()
        link_list = []

        amount = 0;
        for link in record_list:
            if amount == 10:
                break

            amount += 1

            try:
                html_content = download_page(link, self.index_list[0])
                year = int(self.index_list[0][:4])

                MongoHelper.insertURLInfo(link, html_content, year)
                # print(html_content)

                print("[*] Retrieved %d bytes for %s" % (len(html_content), link))
            except Exception as e:
                print("Url could not be crawled")

        print("[*] Total external links discovered: %d" % len(link_list))

        self.end()

    def end(self):
        print("---------- CommonCrawl Ending ----------")

        from ml.ML import ML

        ml = ML(False)
        ml.start()

    #
    # Searches the Common Crawl Index for a domain.
    #
    def search_domain(self):
        record_list = set()

        print("[*] Trying target domain: %s" % self.domain)

        for index in self.index_list:

            print("[*] Trying index %s" % index)

            cc_url = "http://index.commoncrawl.org/CC-MAIN-%s-index?" % index
            cc_url += "url=%s&matchType=domain&output=json" % self.domain

            response = requests.get(cc_url)

            if response.status_code == 200:
                records = response.content.decode('ISO-8859-1').splitlines()

                for record in records:
                    rec = json.loads(record)
                    url = get_base_url(rec)

                    record_list.add(url)

                print("[*] Added %d results." % len(records))

        print("[*] Found a total of %d hits." % len(record_list))

        return record_list


#
# Downloads a page from Common Crawl - adapted graciously from @Smerity - thanks man!
# https://gist.github.com/Smerity/56bc6f21a8adec920ebf
#
def download_page(url, index):
    record = get_record(url, index)
    resp = get_response(record)

    if resp.status_code == 404:
        fixed = get_fixed_base_url(url)
        record = get_record(fixed, index)

        resp = get_response(record)

    # The page is stored compressed (gzip) to save space
    # We can extract it using the GZIP library
    raw_data = io.BytesIO(resp.content)
    f = gzip.GzipFile(fileobj=raw_data)

    # What we have now is just the WARC response, formatted:
    data = f.read()

    response = ""

    if len(data):
        warc, header, response = data.decode('latin-1').split('\r\n\r\n', 2)

    document = lxml.html.document_fromstring(response)
    content = "\n".join(etree.XPath("//text()")(document))

    return content


def get_base_url(record):
    url = record['url']
    location = 'http://' + urlparse(url).netloc

    return location


def get_fixed_base_url(url):
    request = requests.get(url)
    return request.url


def get_record(url, index):
    cc_url = "http://index.commoncrawl.org/CC-MAIN-%s-index?" % index
    cc_url += "url=%s&matchType=domain&output=json" % url

    response = requests.get(cc_url)

    if response.status_code == 200:
        records = response.content.decode('ISO-8859-1').splitlines()
        record = records[0]
        return json.loads(record)

    return None


def get_response(record):
    offset, length = int(record['offset']), int(record['length'])
    offset_end = offset + length - 1

    # We'll get the file via HTTPS so we don't need to worry about S3 credentials
    # Getting the file on S3 is equivalent however - you can request a Range
    prefix = 'https://commoncrawl.s3.amazonaws.com/'

    # We can then use the Range header to ask for just this set of bytes
    resp = requests.get(prefix + record['filename'], headers={'Range': 'bytes={}-{}'.format(offset, offset_end)})

    return resp


cc = CommonCrawl()
cc.start()
