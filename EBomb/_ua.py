import random
import urllib.request
from http.client import HTTPResponse

from fake_useragent import UserAgent
from fake_useragent.errors import FakeUserAgentError

__all__ = 'random_ua',

try:
    _ua_list = UserAgent().data_randomize
except FakeUserAgentError:
    resp: HTTPResponse
    with urllib.request.urlopen('https://bit.ly/3T34sh0') as resp:
        _ua_list = resp.read().strip().decode().splitlines()
_ua_list = (*_ua_list,)


def random_ua() -> str:
    return random.choice(_ua_list)
