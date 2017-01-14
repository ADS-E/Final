import multiprocessing
from queue import Queue

import MongoHelper
from decision.Processor import Processor


class Decider:
    def __init__(self, check_scope):
        # Defines if the decider will work on deciding between website/webshop or in/outscope.
        self.check_scope = check_scope
        self.queue = Queue()
        self.threads = []

    def start(self):
        print("---------- Decider Starting Scope: %s ----------" % self.check_scope)

        # Looping through all currently present id's in MongoDB
        [self.queue.put(id) for id in MongoHelper.getAllIds()]

        self.create_threads()

        for t in self.threads:
            t.join()

        self.end()

    def create_threads(self):
        """Create, start and add threads to a list. Threads run an instance of Spider.
        The amount of threads created depends on the amount of cores found in the system."""

        for i in range(1, multiprocessing.cpu_count()):
            name = "Thread-%s" % i
            thread = Processor(name, self.queue, self.check_scope)
            thread.start()
            self.threads.append(thread)

    def end(self):
        print("---------- Decider Ending Scope: %s ----------" % self.check_scope)

        if not self.check_scope:
            # If we are done checking website/webshop continue with Maps
            from maps.Maps import Maps

            maps = Maps()
            maps.start()
