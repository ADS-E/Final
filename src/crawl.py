import requests
import argparse
import time
import json
import io
import gzip
import csv
import codecs
import pymongo
from urllib.parse import urlparse

from bs4 import BeautifulSoup

import sys
import imp

imp.reload(sys)
# sys.setdefaultencoding('utf8')

domain = '.nl'

# list of available indices
index_list = ["2015-27"]


#
# Searches the Common Crawl Index for a domain.
#
def search_domain(domain):
    record_list = set()

    print("[*] Trying target domain: %s" % domain)

    for index in index_list:

        print("[*] Trying index %s" % index)

        cc_url = "http://index.commoncrawl.org/CC-MAIN-%s-index?" % index
        cc_url += "url=%s&matchType=domain&output=json" % domain

        response = requests.get(cc_url)

        if response.status_code == 200:
            records = response.content.decode('utf-8').splitlines()

            for record in records:
                rec = json.loads(record)
                url = get_base_url(rec)

                record_list.add(url)

            print("[*] Added %d results." % len(records))

    print("[*] Found a total of %d hits." % len(record_list))

    return record_list


#
# Downloads a page from Common Crawl - adapted graciously from @Smerity - thanks man!
# https://gist.github.com/Smerity/56bc6f21a8adec920ebf
#
def download_page(url, index):
    record = get_record(url, index)
    resp = get_response(record)

    if resp.status_code == 404:
        fixed = get_fixed_base_url(url)
        record = get_record(fixed, index)

        resp = get_response(record)

    # The page is stored compressed (gzip) to save space
    # We can extract it using the GZIP library
    raw_data = io.BytesIO(resp.content)
    f = gzip.GzipFile(fileobj=raw_data)

    # What we have now is just the WARC response, formatted:
    data = f.read()

    response = ""

    if len(data):
        warc, header, response = data.decode().split('\r\n\r\n', 2)

    return response


#
# Extract links from the HTML
#
def extract_external_links(url, html_content):
    parser = BeautifulSoup(html_content)

    links = parser.find_all("a")
    link_list = []

    if links:
        for link in links:
            href = link.attrs.get("href")

            if href is not None:

                if url in href:
                    if href.startswith("http"):
                        print("[*] Discovered link: %s" % href)

                        record = get_record(href, index_list[0])
                        if record is not None:
                            print("[/] Discovered urll: %s" % record['url'])
                            if href == record['url']:
                                print('lelelel: %s' % href)

                        link_list.append(href)

    return link_list


def get_base_url(record):
    url = record['url']
    location = 'http://' + urlparse(url).netloc

    return location


def get_fixed_base_url(url):
    request = requests.get(url)
    return request.url


def get_record(url, index):
    cc_url = "http://index.commoncrawl.org/CC-MAIN-%s-index?" % index
    cc_url += "url=%s&matchType=domain&output=json" % url

    response = requests.get(cc_url)

    if response.status_code == 200:
        records = response.content.decode('utf-8').splitlines()
        record = records[0]
        return json.loads(record)

    return None


def get_response(record):
    offset, length = int(record['offset']), int(record['length'])
    offset_end = offset + length - 1

    # We'll get the file via HTTPS so we don't need to worry about S3 credentials
    # Getting the file on S3 is equivalent however - you can request a Range
    prefix = 'https://commoncrawl.s3.amazonaws.com/'

    # We can then use the Range header to ask for just this set of bytes
    resp = requests.get(prefix + record['filename'], headers={'Range': 'bytes={}-{}'.format(offset, offset_end)})

    return resp


record_list = search_domain(domain)
link_list = []

for link in record_list:
    html_content = download_page(link, index_list[0])

    # print(html_content)

    print("[*] Retrieved %d bytes for %s" % (len(html_content), link))
    print(html_content)

    link_list = extract_external_links(link, html_content)

print("[*] Total external links discovered: %d" % len(link_list))

with codecs.open("%s-links.csv" % domain, "wb", encoding="utf-8") as output:
    fields = ["URL"]

    logger = csv.DictWriter(output, fieldnames=fields)
    logger.writeheader()

    for link in link_list:
        logger.writerow({"URL": link})
