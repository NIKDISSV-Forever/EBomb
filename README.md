# EBomb - Email(s) bomber

> pip install -U [EBomb](https://pypi.org/project/EBomb/)

# CLI

> python -m Ebomb -h


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

    def request(self, mail: str, proxies: str = None) -> Response: ...


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


# Install for Android / Linux

- Download [Termux](https://github.com/termux/termux-app/releases) _(Android)_
- Follow the steps from [the article](https://te.legra.ph/EBomb-06-08)
