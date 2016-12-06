import threading

lock = threading.Lock()


class UrlResult:
    def __init__(self, sitename):
        self._results = {}
        self.sitename = sitename
        self.found = False

    def set_found(self, found):
        with lock:
            if not self.found:
                self.found = found

    def get_found(self):
        return self.found

    def seturl(self, url):
        self._url = url

    def geturl(self):
        return self._url

    def get_sitename(self):
        return self.sitename