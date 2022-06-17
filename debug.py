# This module contains some debug functions
import time


def speed(func):
    def check_speed(*args, **kwargs):
        before = time.perf_counter()
        val = func(*args, **kwargs)
        print(f"Function {func.__name__} took: {time.perf_counter() - before} seconds")
        return val

    return check_speed
