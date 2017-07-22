from flask_init import request

from settings import aes_key
from settings import client_id

import json
import time
import bson
import datetime
import math

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from functools import wraps

def oid_handler(x):
  if isinstance(x, datetime.datetime):
    return math.floor(x.timestamp())
  elif isinstance(x, bson.ObjectId):
    return str(x)
  else:
    raise TypeError(x)


class Prpcrypt():
  def __init__(self, key):
    self.key = key
    self.mode = AES.MODE_CBC

  # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
  def encrypt(self, text):
    cryptor = AES.new(self.key, self.mode, self.key)
    # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
    length = 16
    count = len(text)
    add = length - (count % length)
    text = text + ('\0' * add)
    self.ciphertext = cryptor.encrypt(text)
    # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
    # 所以这里统一把加密后的字符串转化为16进制字符串
    return str(b2a_hex(self.ciphertext), 'utf-8')

  # 解密后，去掉补足的空格用strip() 去掉
  def decrypt(self, text):
    cryptor = AES.new(self.key, self.mode, self.key)
    plain_text = str(cryptor.decrypt(a2b_hex(text)), 'utf-8')
    return plain_text.rstrip('\0')

pc = Prpcrypt(aes_key)

# 初始化常见数据的类
_unauthorized_body = json.dumps({'error': 'Permission Denied!'})

_bad_request = json.dumps({'error': 'Your request is invalid!'})

_no_user_named_xxx = json.dumps({'error': 'No user matched!'})

regular_req_headers = {'content-type': 'application/json'}



# 检查是否包含给定的头
def check_headers(headers, *headers_key):
  for key in headers_key:
    if headers.get(key.lower()) != None:
      continue
    else:
      return False
  return True

# 根据请求头进行认证的函数

def auth_wrapper(fn):
  @wraps(fn)
  def wrapped(*args, **kwargs):
    if 'username' in kwargs:
      username = kwargs['username']
    else:
      username = None
    
    try:
      authorization = request.headers.get('authorization')
      decoded_auth = pc.decrypt(authorization)
    
      keys = ['username', 'timestamp', 'client_id']
      values = decoded_auth.split(' ')
      _dict = dict(zip(keys, values))
      if username != None and _dict['username'] != username:
        return _unauthorized_body, 401, regular_req_headers
      else:
        if int(_dict['timestamp']) - math.floor(time.time()) >= 3600 * 24 * 30:
          return _unauthorized_body, 401, regular_req_headers
        else:
          if _dict['client_id'] == client_id:
            pass
          else:
            return _unauthorized_body, 401, regular_req_headers
    except:
      return _bad_request, 400, regular_req_headers
    
    # auth pass!
    if 'username' in kwargs:
      return fn(*args, **kwargs)
    else:
      return fn(*args, **kwargs, username = _dict['username'])
  return wrapped


def check_header_wrapper(*headers):
  def dec(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
      # check if headers have key provided
      if not check_headers(request.headers, *headers):
        return _bad_request, 400, regular_req_headers
      return fn(*args, **kwargs)
    return wrapped
  return dec


def check_req_body_wrapper(*keys):
  def dec(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
      # check if headers have key provided
      try:
        decoded_req_data = json.loads(request.data)
        
        # 检查需要的key是否都在
        results = sum(map(lambda key: key in decoded_req_data, keys)) == len(list(keys))
        if results:
          return fn(*args, **kwargs)
        else:
          return _bad_request, 400, regular_req_headers
      except:
        return _bad_request, 400, regular_req_headers
    return wrapped
  return dec