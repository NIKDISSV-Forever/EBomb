import urllib.request
from random import choice

from fake_useragent import UserAgent
from fake_useragent.errors import FakeUserAgentError

__all__ = 'random_ua',

try:
    _ua_list = UserAgent().data_randomize
except FakeUserAgentError:
    with urllib.request.urlopen(
            'https://gist.github.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1'
            '/user-agents.txt') as resp:
        _ua_list = resp.read().strip().decode().splitlines()
_ua_list = (*_ua_list,)


def random_ua() -> str:
    return choice(_ua_list)
