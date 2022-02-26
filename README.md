#### Documentation in Russian

# EBomb - Спам на почту/ы

> pip install [EBomb](https://pypi.org/project/EBomb/)

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

### CLI
> python -m Ebomb -h