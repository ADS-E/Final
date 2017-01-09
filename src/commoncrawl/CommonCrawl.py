import multiprocessing
from queue import Queue

import requests
import json
import sys
import imp
import zlib

from urllib.parse import urlparse

from commoncrawl.Downloader import Downloader
from helpers import CsvHelper

INDEX = "2016-07"
BASEURL = 'https://aws-publicdatasets.s3.amazonaws.com/'
INDEXURL = 'common-crawl/cc-index/collections/CC-MAIN-%s/indexes/' % INDEX


class CommonCrawl:
    def __init__(self):
        imp.reload(sys)
        self.domain = '.nl'
        self.threads = []
        self.queue = Queue()

    def start(self):
        print("---------- CommonCrawl Starting ----------")

        self.search_domain()
        self.download_domain()

        # self.end()

    def end(self):
        print("---------- CommonCrawl Ending ----------")

        from ml.ML import ML

        ml = ML(False)
        ml.start()

    """Searches the Common Crawl Index for a specified domain."""

    def search_domain(self):
        record_list = set()

        for j in range(1):
            unconsumed_text = ''
            filename = 'cdx-%05d.gz' % 260
            cc_url = BASEURL + INDEXURL + filename

            print("[*] Trying %s" % cc_url)
            # CsvHelper.write_index(cc_url)

            response = requests.get(cc_url, stream=True)
            decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)

            # iterations = int(int(response.headers['content-length'].strip()) / 2048)
            # print("NUMBER: %s" % j)

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

                            if url.endswith('.nl') and url not in record_list:
                                print(url)
                                record_list.add(url)
                        except:
                            print('JSON load failed: ')
                            assert False

            print("Done searching, found %d urls" % len(record_list))
            CsvHelper.write_file('urls.txt', record_list)
            print("Done writing to file")

    def download_domain(self):
        self.queue = Queue()
        for url in CsvHelper.read_file('urls.txt'):
            self.queue.put(url)

        self.create_threads()

        for t in self.threads:
            t.exit()
        for t in self.threads:
            t.join()

    def create_threads(self):
        """Create, start and add threads to a list. Threads run an instance of Spider.
        The amount of threads created depends on the amount of cores found in the system."""

        for i in range(1, multiprocessing.cpu_count()):
            name = "Thread-%s" % i
            thread = Downloader(name, INDEX, self.queue)
            thread.start()
            self.threads.append(thread)


""""Get the base URL from the record"""


def get_base_url(record):
    url = record['url']
    location = 'http://' + urlparse(url).netloc

    return location


""""Get the Commoncrawl record for the given URL and the given Commoncrawl index"""

""""Start the program"""
cc = CommonCrawl()
cc.start()
