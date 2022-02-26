import json
import os.path
import urllib.request
from typing import Optional
from urllib.parse import urlparse

import EasyProxies
from requests import Response, request

from EBomb.ua import random_ua

__all__ = ('Service', 'services', 'JSON_DB_FILE_PATH')

JSON_DB_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services.json')


class Service:
    __slots__ = ('url', 'method', 'netloc')

    def __init__(self, url: str, method: str):
        self.netloc = urlparse(url).netloc
        self.url = url
        self.method = method.upper()

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.netloc}..., {self.method})>'

    def request(self, mail: str, proxies: Optional[EasyProxies.ProxyDescriptor] = None) -> Response:
        for ua_n in ('user-agent', 'User-Agent'):
            resp = request(self.method, self.url.replace('%s', mail), headers={ua_n: random_ua()},
                           proxies=proxies.as_requests_proxy if proxies else None)
            if resp.status_code == 403: continue
            break
        return resp


def _get_services_from_json():
    if not os.path.isfile(JSON_DB_FILE_PATH):
        download = urllib.request.urlopen('https://github.com/NIKDISSV-Forever/EBomb/blob/main/EBomb/services.json'
                                          '?raw=true')
        with open(JSON_DB_FILE_PATH, 'wb') as f:
            f.write(download.read())
    with open(JSON_DB_FILE_PATH, 'rb') as to_load:
        return json.load(to_load)


services = [Service(**serv) for serv in _get_services_from_json()]
