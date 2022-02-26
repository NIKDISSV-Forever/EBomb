from fake_useragent import UserAgent

__all__ = ('random_ua',)
_ua = UserAgent()
random_ua = lambda: _ua.random
