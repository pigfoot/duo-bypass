#!/usr/bin/env python3

import pyotp
import os
import sys

if len(sys.argv) == 2:
    file = sys.argv[1]
else:
    file = "duotoken.hotp"

# get $XDG_DATA_HOME/duo-bypass or $HOME/.local/share/duo-bypass
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

fn_hotp = os.path.join(getConfDir(), 'duotoken.hotp')
with open(fn_hotp, "r+") as f:
  secret = f.readline()[0:-1]
  offset = f.tell()
  count = int(f.readline())

  print("secret", secret)
  print("count", count)

  hotp = pyotp.HOTP(secret)
  print("Code:", hotp.at(count))

  f.seek(offset)
  f.write(str(count + 1))
  f.close()
