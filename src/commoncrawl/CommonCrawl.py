import multiprocessing
from queue import Queue

import requests
import json
import sys
import imp
import zlib

from urllib.parse import urlparse

from commoncrawl.Downloader import Downloader
from helpers import FileHelper

INDEX = "2016-07"
BASEURL = 'https://aws-publicdatasets.s3.amazonaws.com/'
INDEXURL = 'common-crawl/cc-index/collections/CC-MAIN-%s/indexes/' % INDEX


# INDEX = sys.argv[0]

class CommonCrawl:
    def __init__(self):
        imp.reload(sys)
        self.domain = '.nl'
        self.threads = []
        self.queue = Queue()

    def start(self):
        print("---------- CommonCrawl Starting ----------")

        # self.search_commoncrawl()
        # self.download_found()

        self.end()

    def end(self):
        print("---------- CommonCrawl Ending ----------")

        from ml.ML import ML

        ml = ML(False)
        ml.start()

    """Searches the Common Crawl Index for a specified domain."""

    def search_commoncrawl(self):
        record_list = set()

        for j in range(1):
            unconsumed_text = ''
            filename = 'cdx-%05d.gz' % 260
            cc_url = BASEURL + INDEXURL + filename

            print("Trying archive %s" % cc_url)
            # CsvHelper.write_index(cc_url)

            response = requests.get(cc_url, stream=True)
            decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)

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
            FileHelper.write_file('urls.txt', sorted(record_list))
            print("Done writing to file")

    """"Downloading all the found urls"""

    def download_found(self):
        # Put all the found urls into a queue for the threads to read from
        self.queue = Queue()
        [self.queue.put(url) for url in FileHelper.read_file('urls.txt')]

        # Create the threads and wait for them to finish
        self.create_threads()

        for t in self.threads:
            t.join()

    """"Create a number of threads based on the host available amount of threads.
    These threads run an instance of the Downloader class"""

    def create_threads(self):
        # Creates threads and add them to a list.
        for i in range(1, multiprocessing.cpu_count()):
            name = "Thread-%s" % i
            thread = Downloader(name, INDEX, self.queue)
            thread.start()
            self.threads.append(thread)


"""Get the base URL from the record"""


def get_base_url(record):
    url = record['url']
    location = 'http://' + urlparse(url).netloc

    return location


""""Start the program"""
cc = CommonCrawl()
cc.start()
