#!/usr/bin/env python3

from pathlib import Path
import pyotp
import requests
import base64
import json
import os
import sys

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


data = input("Please enter QR Code value manually: ")


#The QR Code is in the format: XXXXXXXXXX-YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
#storing 'XXXXXXXXXX' part in "code"
code = data.split("-")[0]

#decode YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY - decoded format should look like: api-XXXXX.duosecurity.com
b64host = data.split("-")[1]
# add missing base64 padding for successful base64 decode: https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding
b64hostpadding = b64host + '=' * (-len(b64host) % 4)
# decode base64 and convert to string
host = base64.b64decode(b64hostpadding).decode('utf-8')

print("Code: "+code)
print("Host: "+host)

#host = 'api-XXXXX.duosecurity.com'
#code = 'XXXXXXXXXX'

url = 'https://{host}/push/v2/activation/{code}?customer_protocol=1'.format(host=host, code=code)
headers = {'User-Agent': 'okhttp/2.7.5'}
data = {'jailbroken': 'false',
        'architecture': 'arm64',
        'region': 'US',
        'app_id': 'com.duosecurity.duomobile',
        'full_disk_encryption': 'true',
        'passcode_status': 'true',
        'platform': 'Android',
        'app_version': '4.13.0',
        'app_build_number': '413000',
        'version': '12',
        'manufacturer': 'Google',
        'language': 'en',
        'model': 'Pixel 7a',
        'security_patch_level': '2022-04-01'}

r = requests.post(url, headers=headers, data=data)
response = json.loads(r.text)

try:
  secret = base64.b32encode(response['response']['hotp_secret'].encode())
except KeyError:
  print(response)
  sys.exit(1)

print("secret", secret)

print("10 Next OneTime Passwords!")
# Generate 10 Otps!
hotp = pyotp.HOTP(secret)
for _ in range(10):
    print(hotp.at(_))

fn_hotp = os.path.join(getConfDir(), 'duotoken.hotp')
with open(fn_hotp, 'w') as f:
    f.write(secret.decode() + "\n")
    f.write("0")

fn_response = os.path.join(getConfDir(), 'response.json')
with open(fn_response, 'w') as resp:
    resp.write(r.text)
