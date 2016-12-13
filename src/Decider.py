import MongoHelper


class Decider:
    def __init__(self, decide_scope):
        self.decide_scope = decide_scope

    def start(self):
        for index in range(0, MongoHelper.getAvailableId() - 1):
            site = MongoHelper.getResultByIndex(index)
            value = False
            if self.decide_scope:
                site['scope'] = self.decide_scope(site)
                value = site['scope']
            else:
                site['webshop'] = self.decide_webshop(site)
                value = site['scope']

            if value is True:
                MongoHelper.updateInfo(site)
            else:
                MongoHelper.removeByIndex(site["id"])


    # def end(self):


    def decide_scope(self, site):
        if site is not None:
            list = site['list']
            maps = site['maps']
            ml = site['ml']

            if list is True:
                return True
            else:
                if maps is -1:
                    return ml
                else:
                    return True if maps is 1 else False

    def decide_webshop(self, site):
        if site is not None:
            list = site['list']
            maps = site['maps']
            ml = site['ml']

            if list is True:
                return True
            else:
                return ml