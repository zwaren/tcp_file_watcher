import hashlib
import os
import socket
import sys
import time

PATH, IP, PORT = sys.argv[1:]

def get_hash(file_path):
    BUF_SIZE = 65536
    file_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            fb = f.read(BUF_SIZE)
            if not fb:
                break
            file_hash.update(fb)
    return file_hash


def get_files(path):
    files = {}
    for dp, ds, fs in os.walk(path):
        for f in fs:
            file_path = '{}\\{}'.format(dp, f)
            files[file_path] = get_hash(file_path).hexdigest()
    return files


def compare_files(prev, new):
    added = [f for f in new if not f in prev]
    removed = [f for f in prev if not f in new]
    changed = [f for f in prev if not (
        f in added or f in removed) if new[f] != prev[f]]
    return added, removed, changed

if __name__ == '__main__':
    prev = {}
    sock = socket.socket()
    sock.connect(('localhost', 8080))
    while True:
        new = get_files(PATH)
        added, removed, changed = compare_files(prev, new)
        
        if added or removed or changed:
            added_str = '|'.join(['{}:{}b:{}'.format(f, os.stat(f).st_size, 'ADDED') for f in added])
            removed_str = '|'.join(['{}:{}b:{}'.format(f, os.stat(f).st_size, 'REMOVED') for f in removed])
            changed_str = '|'.join(['{}:{}b:{}'.format(f, os.stat(f).st_size, 'CHANGED') for f in changed])

            changes_bytes = bytearray('*'.join([added_str, removed_str, changed_str]), 'utf-8')
            l = len(changes_bytes)
            data = bytearray('SEND', 'utf-8')
            data.extend(l.to_bytes(2, 'big'))
            data.extend(changes_bytes)

            print(data)
            sock.send(data)

            prev = new
        time.sleep(2)
    sock.close()
