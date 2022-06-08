from fake_useragent import UserAgent

__all__ = ('random_ua',)
_ua = UserAgent()


def random_ua() -> str:
    return _ua.random
