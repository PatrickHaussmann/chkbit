import hashlib


BLOCKSIZE = 2**10 * 128  # kb


def hashfile(path):
    sha512 = hashlib.sha512()
    with open(path, "rb") as f:
        while True:
            buf = f.read(BLOCKSIZE)
            if len(buf) <= 0:
                break
            sha512.update(buf)
    return sha512.hexdigest()


def hashtext(text):
    sha512 = hashlib.sha512()
    sha512.update(text.encode("utf-8"))
    return sha512.hexdigest()
