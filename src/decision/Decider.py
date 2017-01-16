import multiprocessing
from queue import Queue

import MongoHelper
from decision.Processor import Processor

"""""Class responsible for looking at the results of all analysing methods
and according to this data deciding what should happen to the scanned sites."""


class Decider:
    def __init__(self, check_scope):
        # Defines if the decider will work on deciding between website/webshop or in/outscope.
        self.check_scope = check_scope
        self.queue = Queue()
        self.threads = []

    def start(self):
        print("---------- Decider Starting Scope: %s ----------" % self.check_scope)

        # Loop through all currently present id's in MongoDB and add them to a queue for the threads to read from.
        [self.queue.put(id) for id in MongoHelper.get_all_Ids()]

        # Create the threads and wait for them to finish
        self.create_threads()

        for t in self.threads:
            t.join()

        self.end()

    """"Create a number of threads based on the host available amount of threads.
    These threads run an instance of the Downloader class"""

    def create_threads(self):
        # Creates threads and add them to a list.
        for i in range(1, multiprocessing.cpu_count()):
            name = "Thread-%s" % i
            thread = Processor(name, self.queue, self.check_scope)
            thread.start()
            self.threads.append(thread)

    def end(self):
        print("---------- Decider Ending Scope: %s ----------" % self.check_scope)

        if not self.check_scope:
            # If done with checking website/webshop continue with Maps
            from maps.Maps import Maps

            maps = Maps()
            maps.start()
