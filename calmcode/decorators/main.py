import time
import random
from functools import wraps

def stopwatch(f):
    @wraps(f)
    def func(*args, **kwargs):
        tic = time.time()
        result = f(*args, **kwargs)
        print(f"function {f} took: {time.time() - tic}")
        return result
    return func

@stopwatch
def sleep_random(t=1):
    """this function sleeps at t seconds and them some more"""
    to_sleep = t + random.random()
    time.sleep(to_sleep/100)
    print(f"in sleep_random, after sleeping for {to_sleep}")
    return to_sleep

timed_sleep_random = stopwatch(sleep_random)

res = timed_sleep_random()
print(f"timed_sleep_random returned {res}")
def add(a, b):
    return a+b

def sub(a, b):
    return a-b

def apply(func, a, b):
    return func (a, b)

def power(n):
    def func(number):
        return number**n
    return func


res = sleep_random()
print(f"sleep_random returned {res}")
print(apply(add, 2, 3))
print(apply(sub, 2025, 1971))

pow2 = power(2)
pow3 = power(3)

print(pow2(3))
print(pow3(5))
print(power(5)(2))


def loggg(func_in=None, *, show_name=True, show_time=True):
    def stopwatch(f):
        @wraps(f)
        def func(*args, **kwargs):
            tic = time.time()
            result = f(*args, **kwargs)
            result = "call"
            if show_name:
                result = f"{result} {f.__name__}"
            if show_time:
                result = f"{result} time:{time.time() - tic}"
            return result
        return func

    # This is where the "magic" happens.
    if func_in is None:
        return stopwatch
    else:
        return stopwatch(func_in)

@loggg
def sleep_random2(s):
    """This function sleeps at least for `s` seconds."""
    return time.sleep(s + random.random()/100)

res = sleep_random2(1)
print(res)

