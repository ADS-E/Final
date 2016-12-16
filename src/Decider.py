import MongoHelper


class Decider:
    def __init__(self, check_scope):
        # Defines if the decider will work on deciding between website/webshop or in/outscope.
        self.check_scope = check_scope

    def start(self):
        print("---------- Decider Starting Scope: %s ----------" % self.check_scope)
        # Looping through all currently present id's in MongoDB
        for id in MongoHelper.getAllIds():
            # Getting a document with the given id
            site = MongoHelper.getResultById(id)

            if self.check_scope:
                # Determines if the website is in or out of scope
                value = self.decide_scope(site)
                # Edits the dictionary with the new value
                site['scope'] = value
            else:
                # Determines if the website is a webshop or not
                value = self.decide_webshop(site)
                # Edits the dictionary with the new value
                site['webshop'] = value

            print("Decided: %s is: %s" % (site['url'], value))
            if value is True:
                # If the website it in our scope or is a webshop update the info in MongoDB
                MongoHelper.updateInfo(site)
            else:
                # If the website is out of our scope or not a webshop remove the document from MongoDB
                MongoHelper.removeByIndex(site["id"])

        self.end()

    def end(self):
        print("---------- Decider Ending Scope: %s ----------" % self.check_scope)

        if not self.check_scope:
            # If we are done checking website/webshop continue with Maps
            from maps.Maps import Maps

            maps = Maps()
            maps.start()

    def decide_scope(self, site):
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

    def decide_webshop(self, site):
        if site is not None:
            list = site['list']
            ml = site['ml']

            # The List analysis is about 100% accurate if it found anything, if it did not we decide by the result of Machine Learning
            if list is True:
                return True
            else:
                return ml
