import time
from pymemcache.client.base import Client
import pickle
import random
from multiprocessing import Pool

client = Client(('localhost', 11211))

def f(x):
    time.sleep(3)
    return x**2


def fc(x):
    cache_key = f"f({x})"
    cached_result = client.get(cache_key)

    if cached_result is not None:
        return pickle.loads(cached_result)

    result = f(x)
    client.set(cache_key, pickle.dumps(result), expire=10)
    return result

def calc_fc(n):
    for i in range(n):
        #rand = random.randint(0, 100)
        #print(f"f({rand}) = {f(rand)}")
        rand = random.randint(0, 100)
        print(f"fc({rand}) = {fc(rand)}")


if __name__ == '__main__':
    n = 49

    with Pool(n) as p:
        print(p.map(calc_fc, [n for _ in range(n)]))
