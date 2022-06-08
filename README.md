# EBomb - Email(s) bomber

> pip install [EBomb](https://pypi.org/project/EBomb/) --upgrade

```python
# EBomb/__init__.py
class EBomb:
    def __init__(self,
                 targets: list[str],
                 threads_count: int = None,
                 proxy: bool = True,
                 forever: bool = True,
                 verbose: bool = True): ...
```

```python
# EBomb/services.py
class Service:
    __slots__ = ('url', 'method', 'netloc')

    def __init__(self, url: str, method: str): ...

    def __repr__(self): ...

    def request(self, mail: str, proxies: EasyProxies.ProxyDescriptor = None) -> requests.Response: ...


services: list[Service] = [...]
```

## Ebomb/services.json

```json
[
  {
    "url": "...",
    "method": "..."
  }
]
```

### CLI

> python -m Ebomb -h
