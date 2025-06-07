import os
import hashlib


def md5_hash(filename):
    if not os.path.isfile(filename):
        return False
    try:
        with open(filename, 'rb') as f:
            m = hashlib.md5()
            while True:
                data = f.read(8096)
                if not data:
                    break
                m.update(data)
            return m.hexdigest()
    except:
        return False
