import multiprocessing
import time
from queue import Queue

from helpers import FileHelper
from list.Result import UrlResult
from list.Spider import Spider

threads = []

""""Class responsible for crawling urls concurrently.
    A file with all the Listing websites needed to be scanned and the website name to be found are given."""


class Crawler:
    """"Assign all the sites in the file to the queue and create an UrlResult to save the data to"""

    def __init__(self, sitename, file):
        self.queue = Queue()
        [self.queue.put(url) for url in FileHelper.read_file(file)]

        self.result = UrlResult(sitename)

    """ Create the necessary threads.
    Wait until the queue is empty and join all the running threads."""

    def run(self):
        self.create_threads()

        while not self.queue.empty():
            time.sleep(0)
            pass
        for t in threads:
            t.join()

        return self.result

    """"Create a number of threads based on the host available amount of threads.
    These threads run an instance of the Spider class"""

    def create_threads(self):
        # Creates threads and add them to a list.
        for i in range(1, multiprocessing.cpu_count()):
            name = "Thread-%s" % i
            thread = Spider(name, self.queue, self.result)
            thread.start()
            threads.append(thread)
