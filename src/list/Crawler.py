import multiprocessing
import time
from queue import Queue

from helpers import CsvHelper
from list.Result import UrlResult
from list.Spider import Spider

threads = []


class Crawler:
    """"Class responsible for crawling urls. Urls are provided to this class in a queue."""

    def __init__(self, sitename, file):
        """"Assign the queue and create an UrlResult to save the data to"""

        self.queue = Queue()
        for url in CsvHelper.read_file(file):
            self.queue.put(url)

        self.result = UrlResult(sitename)

    def run(self):
        """ Create the necessary threads. Check the amount of items still in the queue every second.
        Wait until the queue is empty and join all the running threads."""
        self.create_threads()

        start = time.clock()
        while not self.queue.empty():
            time.sleep(2)
            pass
        for t in threads:
            t.join()
        end = time.clock()

        print('Crawling took %s seconds' % (end - start))

        return self.result

    def create_threads(self):
        """Create, start and add threads to a list. Threads run an instance of Spider.
        The amount of threads created depends on the amount of cores found in the system."""

        for i in range(1, multiprocessing.cpu_count()):
            name = "Thread-%s" % i
            thread = Spider(name, self.queue, self.result)
            thread.start()
            threads.append(thread)
