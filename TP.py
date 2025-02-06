import io
import os
import time
import PIL.Image as Image
from pymemcache.client.base import Client
import pickle

client = Client(('localhost', 11211))

class FS:

    @staticmethod
    def list(path: str):
        return os.listdir(path)

    @staticmethod
    def create(path: str):
        os.mkdir(path)

    @staticmethod
    def read(key: str):
        with open(key, 'rb') as f:
            img = f.read()
        return img

    @staticmethod
    def write(key: str, value: bytes):
        with open(key, 'wb') as f:
            f.write(value)
        pass

    @staticmethod
    def delete(key: str):
        os.remove(key)


class Mem:
    @staticmethod
    def write(key: str, value: bytes):
        lock = pickle.loads(client.get("Lock"))
        while lock is not None:
            time.sleep(1)
            lock = pickle.loads(client.get("Lock"))
        client.set("Lock", pickle.dumps("LRU is mine !"), expire=10)
        LRU = pickle.loads(client.get("LRU"))
        to_delete = LRU.write(key, value)
        for key in to_delete:
            LRU.delete(key)
        client.set("LRU", pickle.dumps(LRU))
        client.delete("Lock")
        return

    @staticmethod
    def read(key: str):
        lock = pickle.loads(client.get("Lock"))
        while lock is not None:
            time.sleep(1)
            lock = pickle.loads(client.get("Lock"))
        client.set("Lock", pickle.dumps("LRU is mine !"), expire=10)
        LRU = pickle.loads(client.get("LRU"))
        T = LRU.read(key)
        client.set("LRU", pickle.dumps(LRU))
        client.delete("Lock")
        return T

    @staticmethod
    def delete(key: str):
        lock = pickle.loads(client.get("Lock"))
        while lock is not None:
            time.sleep(1)
            lock = pickle.loads(client.get("Lock"))
        client.set("Lock", pickle.dumps("LRU is mine !"), expire=10)
        LRU = pickle.loads(client.get("LRU"))
        LRU.delete(key)
        client.set("LRU", pickle.dumps(LRU))
        client.delete("Lock")
        return


class LRU:

    def __init__(self, size_max=5, m=3):
        self.queue = []
        self.size_max = size_max
        self.m = m
        assert m < size_max, "Tu peux pas supprimer plus d'éléments que le nombre d'éléments"

    def read(self, key: str):
        if key not in self.queue:
            return None
        cached_result = client.get(key)
        self.queue.remove(key)
        self.queue.append(key)
        return cached_result

    def write(self, key: str, value: bytes):
        if key in self.queue:
            return False
        self.queue.append(key)
        client.set(str(key), pickle.dumps(value))
        if len(self.queue) > self.size_max:
            return self.queue[0:self.m]
        return []

    def delete(self, key: str):
        if key in self.queue:
            self.queue.remove(key)
            client.delete(key)
            return True
        return False


class CacheFS:
    @staticmethod
    def initial(size_max=5, size_init=3):
        lru = pickle.loads(client.get("LRU"))
        if lru is None:
            lru = LRU(size_max, size_init)
            client.set("LRU", pickle.dumps(lru))
        return

    @staticmethod
    def read(key: str):
        T = Mem.read(key)
        if T is None:
            T = FS.read(key)
            if T is None:
                return False
        Mem.write(key, T)
        T = Image.open(io.BytesIO(T))
        T.show()
        return T

    @staticmethod
    def write(key: str, value: bytes):
        FS.write(key, value)

    @staticmethod
    def delete(key: str):
        Mem.delete(key)
        FS.delete(key)

