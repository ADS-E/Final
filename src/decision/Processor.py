import threading

import MongoHelper


class Processor(threading.Thread):
    """"Class used for scanning urls on containing certain words."""

    def __init__(self, name, queue, check_scope):
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue
        self.check_scope = check_scope

    def run(self):
        """"Get an url from the queue, process the url and notify the queue the task on the retrieved item is done.
        Continue this process while the queue has items"""

        while not self.queue.empty():
            id = self.queue.get()

            self.process(id)
            self.queue.task_done()

        print("%s done" % self.name)

    def process(self, id):
        site = MongoHelper.getResultById(id)

        if self.check_scope:
            # Determines if the website is in or out of scope
            value = decide_scope(site)
            # Edits the dictionary with the new value
            site['scope'] = value
        else:
            # Determines if the website is a webshop or not
            value = decide_webshop(site)
            # Edits the dictionary with the new value
            site['webshop'] = value

        print("Decided: %s is: %s" % (site['url'], value))
        if value is True:
            # If the website it in our scope or is a webshop update the info in MongoDB
            if self.check_scope:
                MongoHelper.updateValue(site, 'scope')
            else:
                MongoHelper.updateValue(site, 'webshop')
        else:
            # If the website is out of our scope or not a webshop remove the document from MongoDB
            MongoHelper.removeByIndex(site["id"])


def decide_scope(site):
    # Decides if the webshop is in or out of scope
    if site is not None:
        # Gets all the results from the analysis
        list = site['list']
        maps = site['maps']
        ml = site['ml']

        # The List analysis is about 100% accurate if it found anything, if it did not we continue with the other methods
        if list is True:
            return True
        else:
            # If the result from Maps return -1 (not found) we decide by the result from Machine Learning
            if maps is -1:
                return ml
            else:
                # If the Maps found something we decide by that value
                return True if maps is 1 else False


def decide_webshop(site):
    if site is not None:
        list = site['list']
        ml = site['ml']

        # The List analysis is about 100% accurate if it found anything, if it did not we decide by the result of Machine Learning
        if list is True:
            return True
        else:
            return ml
