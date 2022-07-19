from __future__ import annotations

import json
import pathlib
import sys
import urllib.request
from http.client import HTTPResponse
from urllib.parse import urlparse

from requests import Response, Session

from EBomb.ua import random_ua

__all__ = ('Service', 'services', 'UNIQUE_NETLOC', 'JSON_DB_FILE_PATH')

try:
    _wfp = pathlib.Path(__file__)
except NameError:  # executable file
    _wfp = pathlib.Path(sys.argv[0]).absolute()

JSON_DB_FILE_PATH = _wfp.parent / 'services.json'


class Service:
    __slots__ = ('url', 'method', 'netloc')

    def __init__(self, method: str, url: str):
        url = url.removesuffix('/')
        self.netloc = urlparse(url).netloc or ''
        self.url = url
        self.method = method.upper()

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.netloc!r}, {self.method!r})>'

    def request(self, mail: str, proxies: str = None) -> Response:
        if proxies is not None:
            proxies = f'socks5://{proxies}'
            proxies = {'http': proxies, 'https': proxies}

        for ua_n in ('user-agent', 'User-Agent'):
            with Session() as session:
                resp = session.request(self.method,
                                       self.url.replace('%s', mail),
                                       headers={ua_n: random_ua()},
                                       proxies=proxies, timeout=10)
            if resp.status_code != 403:
                break

        return resp


def _get_services_from_json() -> tuple[dict[str, str]]:
    if not (JSON_DB_FILE_PATH.is_file() and JSON_DB_FILE_PATH.stat().st_size):
        download: HTTPResponse
        with urllib.request.urlopen('https://github.com/NIKDISSV-Forever/EBomb/blob/main/EBomb/services.json'
                                    '?raw=true') as download:
            JSON_DB_FILE_PATH.write_bytes(download.read())
    with open(JSON_DB_FILE_PATH, 'rb') as to_load:
        return *(json.load(to_load)),


_DB = _get_services_from_json()
services = [Service(*serv) for serv in _DB]
UNIQUE_NETLOC = len({urllib.parse.urlparse(url).netloc for _, url in _DB})
del _DB
