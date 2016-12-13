import MongoHelper


class Decider:
    def __init__(self, check_scope):
        self.check_scope = check_scope

    def start(self):
        print("---------- Decider Starting Scope: %s ----------" % self.check_scope)

        for id in MongoHelper.getAllIds():
            site = MongoHelper.getResultById(id)

            if self.check_scope:
                value = self.decide_scope(site)
                site['scope'] = value
            else:
                value = self.decide_webshop(site)
                site['webshop'] = value

            print("Decided: %s is: %s" % (site['url'], value))
            if value is True:
                MongoHelper.updateInfo(site)
            else:
                MongoHelper.removeByIndex(site["id"])

        self.end()

    def end(self):
        print("---------- Decider Ending Scope: %s ----------" % self.check_scope)

        if not self.check_scope:
            from maps.Maps import Maps

            maps = Maps()
            maps.start()

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
            ml = site['ml']

            if list is True:
                return True
            else:
                return ml
