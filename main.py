import argparse
import os
import shutil
import sys
from Cryptodome.PublicKey import RSA
import pyperclip
import os

ssh_path = os.path.join(os.path.expanduser('~'), '.ssh')


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def create_profile(profile_name):
    profile_path = os.path.join(ssh_path, 'profile_{}'.format(profile_name))
    active_profile_path = os.path.join(ssh_path, 'active_profile_{}'.format(profile_name))
    if os.path.exists(profile_path) or os.path.exists(active_profile_path):
        print('{}Profile already exist{}'.format(bcolors.FAIL, bcolors.ENDC))
        return

    os.makedirs(profile_path)
    key = RSA.generate(2048)
    f = open(os.path.join(profile_path, "id_rsa"), "wb")
    f.write(key.exportKey('PEM'))
    f.close()

    pubkey = key.publickey()
    f = open(os.path.join(profile_path, "id_rsa.pub"), "wb")
    f.write(pubkey.exportKey('OpenSSH'))
    f.close()

    print('Profile {} created'.format(profile_name))


def get_current_profile():
    for filename in os.listdir(ssh_path):
        f = os.path.join(ssh_path, filename)
        # checking if it is a file
        if not os.path.isfile(f) and filename.startswith('active'):
            print(filename.replace('active_profile_', ''))
            return

    print('Any active profile')


def list_profile():
    for filename in os.listdir(ssh_path):
        f = os.path.join(ssh_path, filename)
        # checking if it is a file
        if not os.path.isfile(f):
            if filename.startswith('profile'):
                print(filename.replace('profile_', ''))
            if filename.startswith('active'):
                print('{}{}{}'.format(bcolors.OKGREEN, filename.replace('active_profile_', ''), bcolors.ENDC))


def select_profile(profile):
    for filename in os.listdir(ssh_path):
        f = os.path.join(ssh_path, filename)
        # checking if it is a file
        if not os.path.isfile(f) and filename.startswith('active'):
            os.rename(f, os.path.join(ssh_path, filename.replace('active_', '')))

    if os.path.exists(os.path.join(ssh_path, 'profile_{}'.format(profile))):
        if os.path.exists(os.path.join(ssh_path, 'id_rsa')):
            os.remove(os.path.join(ssh_path, 'id_rsa'))
        if os.path.exists(os.path.join(ssh_path, 'id_rsa.pub')):
            os.remove(os.path.join(ssh_path, 'id_rsa.pub'))
        os.rename(os.path.join(ssh_path, 'profile_{}'.format(profile)),
                  os.path.join(ssh_path, 'active_profile_{}'.format(profile)))
        shutil.copyfile(os.path.join(ssh_path, 'active_profile_{}'.format(profile), 'id_rsa'),
                        os.path.join(ssh_path, 'id_rsa'))
        os.chmod(os.path.join(ssh_path, 'id_rsa'), 0o400)
        shutil.copyfile(os.path.join(ssh_path, 'active_profile_{}'.format(profile), 'id_rsa.pub'),
                        os.path.join(ssh_path, 'id_rsa.pub'))
        print('New profile {} selected'.format(profile))
    else:
        print('Profile not found or already active')


def copy_current_public_key():
    if os.path.exists(os.path.join(ssh_path, 'id_rsa.pub')):
        pyperclip.copy(open(os.path.join(ssh_path, 'id_rsa.pub')).read())
        print('{}Public key copied !{}'.format(bcolors.OKGREEN, bcolors.ENDC))
    else:
        print('{}Public key not found{}'.format(bcolors.FAIL, bcolors.ENDC))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SSH Profile management')
    parser.add_argument('-c', help='Create new profile', metavar='profile_name', type=str)
    parser.add_argument('-l', help='List profiles', action='store_true')
    parser.add_argument('-g', help='Get current profile', action='store_true')
    parser.add_argument('-pub', help='Copy current public key', action='store_true')
    parser.add_argument('-s', help='Select profile', metavar='profile_name', type=str)
    args = parser.parse_args()

    if args.c is not None:
        create_profile(args.c)
        exit(1)
    if args.l is True:
        list_profile()
        exit(1)
    if args.g is True:
        get_current_profile()
        exit(1)
    if args.pub is True:
        copy_current_public_key()
        exit(1)
    if args.s is not None:
        select_profile(args.s)
        exit(1)
