from typing import Callable


def measure_time(func: Callable):
    from time import perf_counter

    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        print(perf_counter() - start)
        return result

    return wrapper
