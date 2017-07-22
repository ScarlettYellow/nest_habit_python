import json
import bson
import datetime

from functools import wraps

from flask_init import app
from flask_init import request

from database import db
from database import errors
from database import ReturnDocument

from common import _unauthorized_body
from common import _bad_request
from common import _no_user_named_xxx
from common import regular_req_headers

from common import auth_wrapper
from common import check_req_body_wrapper
from common import check_header_wrapper
from common import oid_handler

@app.route('/nest', methods = ['POST'])
@check_header_wrapper('authorization')
@auth_wrapper
@check_req_body_wrapper('name', 'desc', 'members_limit', 'start_time', 'challenge_days')
def add_nest(username):
  json_req_data = json.loads(request.data)
  try:
    # 新建
    keys = ['name', 'desc', 'members_limit', 'start_time', 'challenge_days']
    values = map(lambda key: json_req_data[key], keys)
    data_to_insert = dict(zip(keys, values))
    data_to_insert['start_time'] = datetime.datetime.fromtimestamp(int(data_to_insert['start_time']))
    data_to_insert['cover_image'] = ''
    data_to_insert['created_time'] = datetime.datetime.utcnow()
    data_to_insert['creator'] = username
    data_to_insert['owner'] = username
    data_to_insert['kept_days'] = 0
    inserted_id = db['_nests'].insert_one(data_to_insert).inserted_id
    
    # 添加到用户
    result = db['_users'].find_one_and_update(
      {'username': username},
      {
        '$push': {
          'joined_nests': {'$each': [ inserted_id ]}
        }
      },
      return_document=ReturnDocument.AFTER
    )
    if result == None:
      return _no_user_named_xxx, 400, regular_req_headers
    
  except errors.DuplicateKeyError:
    return json.dumps({
      'error': 'Nest name already exists!'
    }), 400, regular_req_headers

  # 处理其他所有错误
  except:
    return _bad_request, 400, regular_req_headers

  # 无错误
  return json.dumps(data_to_insert, default = oid_handler), 200, regular_req_headers


@app.route('/nest/<id>', methods = ['GET'])
@check_header_wrapper('authorization')
@auth_wrapper
def get_nest(id, username):
  # query user info
  result = db['_nests'].find_one({'_id': bson.ObjectId(id)})
  if result == None:
    return _no_user_named_xxx, 400, regular_req_headers

  list_members = request.values.get('list_members')
  if list_members:
    cursor = db['_users'].find(
      {
        'joined_nests': {
          '$in': [ bson.ObjectId(id) ]
        }
      },
      projection = {
        '_id': False,
        'created_time': False,
        'password': False
      }
    )
    result['members'] = list((c for c in cursor))
  
  return json.dumps(result, default = oid_handler), 200, regular_req_headers


@app.route('/nests', methods = ['GET'])
@check_header_wrapper('authorization')
@auth_wrapper
def filter_nest(username):
  list_members = request.values.get('list_members')
  name = request.values.get('name')
  _id = request.values.get('_id')
  desc = request.values.get('desc')
  
  print(copyright())
  
  pass