#!/usr/bin/env python3

import random
try:
    import xmlrpclib
except ImportError:
    import xmlrpc.client as xmlrpclib

from bs4 import BeautifulSoup
from urllib import request

PYPI_URL = 'https://pypi.python.org/pypi'
PYPI_RANKING_URL = 'http://pypi-ranking.info/alltime?page={0}'
RANKING_PAGES_NUM = 1683


def most_downloaded(n=100):
    produced = 0
    for page in range(1, RANKING_PAGES_NUM + 1):
        if produced >= n:
            return
        url_response = request.urlopen(PYPI_RANKING_URL.format(page))
        soup = BeautifulSoup(url_response.read(), 'html.parser')
        module_list = soup.select('td.description')
        number_of_modules = len(module_list)
        if produced + number_of_modules <= n:
            produced += number_of_modules
        else:
            module_list = module_list[:n - produced]
            produced = n
        for name in [x.a.contents[1].string for x in module_list]:
            yield name


def random_packages(n=100):
    client = xmlrpclib.ServerProxy(PYPI_URL)
    all_packages = client.list_packages()
    for num in random.sample(range(len(all_packages)), n):
        yield all_packages[num]


if __name__ == '__main__':
    with open('test_set2', 'w') as fo:
        for pkg in most_downloaded(500):
            fo.write("{0}\n".format(pkg))

   # l = list(most_downloaded(150)) + list(random_packages(150))
   # print(len(l))
   # print(l)
