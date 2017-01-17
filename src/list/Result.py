import threading

lock = threading.Lock()

""""Class to save data about a webshop listing scan.
The website name and if it was found are saved."""


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

    def get_sitename(self):
        return self.sitename
