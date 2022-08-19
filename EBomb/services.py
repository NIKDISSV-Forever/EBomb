from __future__ import annotations

import sys
import urllib.request
from http.client import HTTPResponse
from pathlib import Path
from urllib.parse import urlparse

import httpx

from EBomb._ua import random_ua

__all__ = ('Service', 'services', 'UNIQUE_NETLOC', 'SERVICES_DB_FILE_PATH')

try:
    _wfp = Path(__file__)
except NameError:  # if executable file
    _wfp = Path(sys.argv[0]).absolute()

SERVICES_DB_FILE_PATH = _wfp.parent / 'services.txt'


class Service:
    __slots__ = ('url', 'method', 'netloc')

    def __init__(self, method: str, url: str):
        url = url.removesuffix('/')
        self.netloc = urlparse(url).netloc or ''
        self.url = url
        self.method = method.upper()

    def __str__(self):
        return f'{self.method}\n{self.url}'

    def __repr__(self):
        return f'<{self.__class__.__qualname__}({self.method!r}, {self.netloc!r})>'

    def request(self, mail: str, proxies: str = None) -> httpx.Response:
        if proxies is not None:
            proxies = f'socks5://{proxies}'
            proxies = {'http://': proxies, 'https://': proxies}

        with httpx.Client(proxies=proxies) as client:
            for ua_n in ('user-agent', 'User-Agent'):
                resp = client.send(
                    httpx.Request(self.method, self.url.replace('%s', mail),
                                  headers=((ua_n, random_ua()),)))
                if resp.status_code != 403:
                    break

        return resp


def _get_services_from_json() -> tuple[tuple[str, str]]:
    if not (SERVICES_DB_FILE_PATH.is_file() and SERVICES_DB_FILE_PATH.stat().st_size):
        download: HTTPResponse
        with urllib.request.urlopen('https://github.com/NIKDISSV-Forever/EBomb/blob/main/EBomb/services.txt'
                                    '?raw=true') as download:
            SERVICES_DB_FILE_PATH.write_bytes(download.read())
    with open(SERVICES_DB_FILE_PATH) as to_load:
        return *((*serv.splitlines(),) for serv in to_load.read().strip().split('\n\n')),


_DB = _get_services_from_json()
services = [Service(*serv) for serv in _DB]
UNIQUE_NETLOC = len({urllib.parse.urlparse(url).netloc for _, url in _DB})
del _DB
