import threading

lock = threading.Lock()


class UrlResult:
    def __init__(self, url):
        self._results = {}
        self._url = url
        self.word_count = 0
        self.page_count = 0

    def put(self, key, value):
        with lock:
            if key in self._results:
                self._results[key] += value
            else:
                self._results[key] = value
            return self

    def get(self, key):
        with lock:
            return self._results[key]

    def set_word_count(self, count):
        with lock:
            self.word_count += count

    def set_page_count(self, count):
        self.page_count = count

    def seturl(self, url):
        self._url = url

    def geturl(self):
        return self._url

    def all(self):
        return self._results

    def csv_format(self):
        values = []
        values.append(self._url)
        for key in sorted(self._results):
            values.append(self._results[key])

        values.append(self.word_count)
        values.append(self.page_count)
        return values
