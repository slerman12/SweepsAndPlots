# Copyright (c) AGI.__init__. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# MIT_LICENSE file in the root directory of this source tree.
import getpass
import os

from cryptography.fernet import Fernet

from pexpect import spawn


def get_pass(kind='pass'):
    # Get password, encrypt, and save for reuse
    if os.path.exists(f'.{kind}'):
        with open(f'.{kind}', 'r') as file:
            key, encoded = file.readlines()
            password = Fernet(key).decrypt(bytes(encoded, 'utf-8'))
    else:
        password, key = getpass.getpass(f'Enter {kind} pass:'), Fernet.generate_key()
        encoded = Fernet(key).encrypt(bytes(password, 'utf-8'))
        with open(f'.{kind}', 'w') as file:
            file.writelines([key.decode('utf-8') + '\n', encoded.decode('utf-8')])
        os.system(f'attrib +h .{kind}')  # Make hidden
    return password


def connect_vpn(username='slerman'):
    def _connect_vpn():
        try:
            password = get_pass()
            p = spawn('/opt/cisco/anyconnect/bin/vpn connect vpnconnect.rochester.edu')
            p.expect('Username: ')
            p.sendline('')
            p.expect('Password: ')
            p.sendline(password)
            p.expect('Second Password: ')
            p.sendline('push')
            p.expect('VPN>')
            print(f'Connected to VPN\nFor Bluehive:\nssh {username}@bluehive.circ.rochester.edu')
        except Exception:
            pass
    return _connect_vpn


def disconnect_vpn():
    p = spawn('/opt/cisco/anyconnect/bin/vpn disconnect')
    p.expect('b')


if __name__ == '__main__':
    connect_vpn()()
