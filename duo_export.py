#!/usr/bin/env python3

import pyotp
import pyqrcode
import json
import base64
import os
import sys

def getConfDir():
  pkg_name = 'duo-bypass'

  _home = os.path.expanduser('~')

  # os.path.join(_home, '.local', 'share')
  xdg_data_home = os.environ.get('XDG_DATA_HOME')
  if xdg_data_home is not None:
    _path = os.path.join(xdg_data_home, pkg_name)
    if not os.path.isdir(_path):
      os.makedirs(_path)

    return _path

  # os.path.join(_home, '.config')
  xdg_config_home = os.environ.get('XDG_CONFIG_HOME') or \
    os.path.join(_home, '.config')

  _path = os.path.join(xdg_config_home, pkg_name)
  if not os.path.isdir(_path):
    os.makedirs(_path)

  return _path

fn_response = os.path.join(getConfDir(), 'response.json')
with open(fn_response, "r") as f:
  response = json.loads(f.read())['response']

fn_hotp = os.path.join(getConfDir(), 'duotoken.hotp')
with open(fn_hotp, "r") as f:
  counter = int(f.readlines()[1])

label = response['customer_name']
issuer = 'Duo'
# base32 encoded hotp secret, with the padding ("=") stripped.
secret = base64.b32encode(bytes(response['hotp_secret'], 'utf-8')).decode('utf-8').replace('=', '')
qrdata = 'otpauth://hotp/{label}?secret={secret}&issuer={issuer}&counter={counter}'.format(label=label, secret=secret, issuer=issuer, counter=counter)
qrcode = pyqrcode.create(qrdata)
print(qrcode.terminal(quiet_zone=1))
print(qrdata)
