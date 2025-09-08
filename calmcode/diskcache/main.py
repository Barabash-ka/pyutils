import requests as rq
from functools import lru_cache
import time
from diskcache import Cache

cache = Cache("local")

@cache.memoize()
def fetch_starwars_person(i):
    start = time.time()
    res = rq.get(f"https://swapi.dev/api/people/{i}/").json()
    return res, time.time() - start

for i in range(5):
    res, dur = fetch_starwars_person(1)
    print(f"fetched in {dur} time")
