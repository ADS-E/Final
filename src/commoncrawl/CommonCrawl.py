import lxml.html
from lxml import etree

import requests
import json
import io
import gzip
import sys
import imp
import MongoHelper
import zlib

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

        amount = 0
        for link in record_list:

            try:
                html_content = download_page(link, self.index_list[0])

                if not html_content.isspace():
                    year = int(self.index_list[0][:4])
                    MongoHelper.insertURLInfo(link, html_content, year)

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

    """Searches the Common Crawl Index for a specified domain."""

    def search_domain(self):
        record_list = set()

        for j in range(300):
            unconsumed_text = ''
            filename = 'cdx-%05d.gz' % j
            cc_url = BASEURL + INDEX1 + filename

            print("[*] Trying %s" % cc_url)

            response = requests.get(cc_url, stream=True)
            decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)

            #iterations = int(int(response.headers['content-length'].strip()) / 2048)
            #print("NUMBER: %s" % j)

            i = 0
            for chunk in response.iter_content(chunk_size=2048):
                i += 1
                if i % 20000 == 0:
                    print("Iteration: %s" % i)
                if len(decompressor.unused_data) > 0:
                    # restart decompressor if end of a chunk
                    to_decompress = decompressor.unused_data + chunk
                    decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
                else:
                    to_decompress = decompressor.unconsumed_tail + chunk
                s = unconsumed_text + decompressor.decompress(to_decompress).decode('utf-8')
                unconsumed_text = ''

                for l in s.split('\n'):
                    pieces = l.split(' ')
                    if len(pieces) < 3 or l[-1] != '}':
                        unconsumed_text = l
                    else:
                        json_string = ' '.join(pieces[2:])
                        try:
                            rec = json.loads(json_string)
                            url = get_base_url(rec)

                            if '.nl' in url:
                                record_list.add(url)
                        except:
                            print('JSON load failed: ')
                            assert False

        print("Added %d results." % len(record_list))
        return record_list

"""Download a page retrieved by an URL from Common Crawl.
Strip all the html tags from the content to save space in MongoDB"""


def download_page(url, index):
    record = get_record(url, index)
    resp = get_response(record)

    if resp.status_code == 404:
        fixed = get_fixed_base_url(url)
        record = get_record(fixed, index)

        resp = get_response(record)

    """The page is stored compressed (gzip) to save space
    it can be extracted by using the GZIP library"""
    raw_data = io.BytesIO(resp.content)
    f = gzip.GzipFile(fileobj=raw_data)

    """What we have now is just the WARC response, formatted:"""
    data = f.read()

    response = ""

    if len(data):
        warc, header, response = data.decode('latin-1').split('\r\n\r\n', 2)

    document = lxml.html.document_fromstring(response)
    content = "\n".join(etree.XPath("//text()")(document))

    return content


""""Get the base URL from the record"""


def get_base_url(record):
    url = record['url']
    location = 'http://' + urlparse(url).netloc

    return location


""""Get the base URL from a given URL by loading the page and seeing
how the server redirects it to an adjusted URL. This is the fixed base URL"""


def get_fixed_base_url(url):
    request = requests.get(url)
    return request.url


""""Get the Commoncrawl record for the given URL and the given Commoncrawl index"""


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

    """Get the file via HTTPS so we don't need to worry about S3 credentials."""
    prefix = 'https://commoncrawl.s3.amazonaws.com/'

    """Use the Range header to ask for just this set of bytes"""
    resp = requests.get(prefix + record['filename'], headers={'Range': 'bytes={}-{}'.format(offset, offset_end)})

    return resp


BASEURL = 'https://aws-publicdatasets.s3.amazonaws.com/'
INDEX1 = 'common-crawl/cc-index/collections/CC-MAIN-2015-11/indexes/'

""""Start the program"""
cc = CommonCrawl()
cc.start()
