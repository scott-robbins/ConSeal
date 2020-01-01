from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import base64
import utils
import time
import sys
import os

tic = time.time()
DEBUG = False


def destroy_files(directory):
    contents = utils.crawl_dir(directory, False)
    for file_name in contents['file']:
        os.remove(file_name)
    for dir in contents['dir']:
        os.rmdir(dir)
    os.rmdir(directory)
    print '[*] %s Has Been \033[1mDestroyed\033[0m' % directory


def check_args():
    if len(sys.argv) < 3:
        print '\033[31m\033[1mIncorrect Usage!\033[0m'
        print '$ python seal.py <File Path>'
        exit()
    elif '-e' in sys.argv:
        return 'encrypt', sys.argv[2]
    elif '-d' in sys.argv:
        return 'decrypt', sys.argv[2]


def encrypt_archive(b, destroy):
    print "[*] CONSEAL'ing %s" % b
    print '[*] PLAINTEXT_ARCHIVE SHA-256 SUM:'
    os.system('tar -c %s | gzip -r -9 > archive.tar.gz' % b)
    os.system('sha256sum archive.tar.gz')
    key = get_random_bytes(32)
    cipher = AES.new(key)
    compressed_content = open('archive.tar.gz', 'rb').read()
    if destroy:
        os.remove('archive.tar.gz')
    encrypted_content = utils.EncodeAES(cipher, compressed_content)
    sealed_file_name = 'archive.tar.gz'.split('.tar.gz')[0]+'.sealed'
    open(sealed_file_name, 'wb').write(encrypted_content)
    open('archive.tar.gz'.split('.tar.gz')[0]+'.key', 'wb').write(base64.b64encode(key))
    os.system('sudo rm -r %s' % b)
    return sealed_file_name, base64.b64encode(key)


def decrypt_archive(key_file, archive_file):
    print '[*] Decrypting CONSEALd Archive'
    print '[*] PLAINTEXT ARCHIVE-SHA256 SUM:'
    decomp = 'gunzip < archive.tar.gz | tar -x'
    key = base64.b64decode(open(key_file, 'rb').read())
    encrypted_data = open(archive_file, 'rb').read()
    decrypted_data = utils.DecodeAES(AES.new(key), encrypted_data)
    open('archive.tar.gz', 'wb').write(decrypted_data)
    os.system('sha256sum archive.tar.gz')
    os.system(decomp)
    os.remove('archive.tar.gz')
    os.remove(key_file)
    os.remove(archive_file)


action, base_path = check_args()
if action == 'encrypt':
    sealed_archive, secret = encrypt_archive(base_path, destroy=True)
if action == 'decrypt':
    print '[*] Decrypting CONSEALd Archive %s' % base_path
    decrypt_archive(base_path+'.key', base_path+'.sealed')


print "[*] FINISHED CONSEAL'ing %s [%ss Elapsed]" % (base_path, str(time.time() - tic))