from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import base64
import sys
import os


BLOCK_SIZE = 16     # the block size for the cipher object; must be 16 per FIPS-197
PADDING = '{'
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING        # pad text to be encrypted
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))            # encrypt with AES
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)


def swap(file_name, destroy):
    data = []
    for line in open(file_name, 'r').readlines():
        data.append(line.replace('\n', ''))
    if destroy:
        os.remove(file_name)
    return data


def cmd(command):
    os.system('%s >> cmd.txt' % command)
    return swap('cmd.txt', True)


def crawl_dir(file_path, doHash):
    directory = {'dir': [], 'file': []}
    hashes = {}
    folders = [file_path]
    while len(folders) > 0:
        direct = folders.pop()
        for item in os.listdir(direct):
            if os.path.isfile(direct + '/' + item):
                file_name = direct + '/' + item
                directory['file'].append(file_name)
                if doHash:
                    sha_hash = cmd('sha256sum %s' % file_name).pop().split(' ')[0]
                    sha_hash[file_name] = sha_hash
            else:
                directory['dir'].append(direct + item)
                folders.append(direct + item)
    return directory, hashes


