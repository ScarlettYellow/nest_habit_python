import json
import bson
import datetime

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


@app.route('/alarm_clock', methods = ['POST'])
@check_header_wrapper('authorization')
@auth_wrapper
@check_req_body_wrapper('title', 'time', 'repeat', 'music_id', 'duration_level',
                        'nap_level', 'volume_level', 'bind_to_nest', 'willing_music',
                        'willing_text')
def new_alarm_clock(username):
  json_req_data = json.loads(request.data)
  try:
    # 新建
    keys = ['title', 'time', 'repeat', 'music_id', 'duration_level',
            'nap_level', 'volume_level', 'bind_to_nest', 'willing_music',
            'willing_text']
    
    values = map(lambda key: json_req_data[key], keys)
    data_to_insert = dict(zip(keys, values))
    
    if data_to_insert['bind_to_nest']:
      data_to_insert['bind_to_nest'] = bson.ObjectId(data_to_insert['bind_to_nest'])
    else:
      data_to_insert['bind_to_nest'] = ''
    
    data_to_insert['created_time'] = datetime.datetime.utcnow()
    data_to_insert['owner'] = username
    
    inserted_id = db['_alarm_clocks'].insert_one(data_to_insert).inserted_id
    
    # 添加到用户
    result = db['_users'].find_one_and_update(
      {'username': username},
      {
        '$push': {
          'alarm_clocks': {
            '$each': [ inserted_id ]
          }
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


@app.route('/alarm_clock/<id>', methods = ['GET'])
@check_header_wrapper('authorization')
@auth_wrapper
def get_alarm_clock(id, username):
  
  result = db['_alarm_clocks'].find_one(
    {
      'owner': username,
      '_id': bson.ObjectId(id)
    }
  )
  
  if result == None:
    return json.dumps({
      'error': 'You own no alarm clock!'
    }), 400, regular_req_headers
  
  return json.dumps(result, default = oid_handler), 200, regular_req_headers

@app.route('/alarm_clock/<id>', methods = ['PUT', 'POST'])
@check_header_wrapper('authorization')
@auth_wrapper
def edit_alarm_clock(id, username):
  update_data = json.loads(request.data)
  
  if 'created_time' in update_data \
      or '_id' in update_data:
    return json.dumps({
      'error': 'You can\'t change some param you provide!'
    }), 400, regular_req_headers
  
  