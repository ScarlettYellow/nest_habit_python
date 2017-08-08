# -*- coding: utf-8 -*-

import json
import math
import datetime
import time
import random
import mimetypes
import bson

from flask_init import app
from flask_init import request

from qingstor.sdk.service.qingstor import QingStor
from qingstor.sdk.config import Config

from database import db
from database import errors
from database import ReturnDocument

# import common data from common package
from common import pc
from common import _unauthorized_body
from common import _bad_request
from common import _no_user_named_xxx
from common import regular_req_headers

from common import auth_wrapper
from common import check_header_wrapper
from common import check_req_body_wrapper
from common import oid_handler

from settings import client_id
from settings import client_secret
from settings import qy_access_key
from settings import qy_secret_access_key


# 使用@装饰器来修饰接口
@app.route('/api/v1/user/<username>/session', methods=['POST'])
@check_req_body_wrapper('password', 'client_id', 'client_secret')  # 请求体json中必须包含的字段， 下同
def login(username):
    # 检查client_id, client_secret的正确性
    json_req_data = json.loads(request.data)
    if client_id == json_req_data['client_id'] and client_secret == json_req_data['client_secret']:
        pass
    else:
        return _unauthorized_body, 401, regular_req_headers
    
    # 检查通过，开始查询尝试登陆
    password = json_req_data['password']
    result = db['_users'].find_one({'username': username, 'password': password})
    if result != None:
        return json.dumps({
            'msg': 'Logged in successfully!',
            'Authorization': pc.encrypt('%s %s %s' % (username, str(math.floor(time.time())), client_id))
        }), 200, regular_req_headers
    else:
        return _no_user_named_xxx, 400, regular_req_headers


@app.route('/api/v1/user/<username>/session', methods=['DELETE'])
@check_header_wrapper('authorization')  # 必须的请求头，不分大小写，下同
@auth_wrapper  # 说明需要登录
def logout(username):
    # 先做个假的吧，不会有人知道的
    return json.dumps({
        'msg': 'Logged out successfully!'
    }), 200, regular_req_headers


@app.route('/api/v1/user/<username>/info', methods=['GET'])
@check_header_wrapper('authorization')
@auth_wrapper
def get_user_info(username):
    # auth pass
    
    # query user info
    result = db['_users'].find_one({'username': username})
    if result == None:
        return _no_user_named_xxx, 400, regular_req_headers
    
    # generate response
    keys = list(filter(lambda key: key not in ['_id', 'password', 'created_time'], result.keys()))
    values = list(map(lambda key: result[key], keys))
    return json.dumps(dict(zip(keys, values)), default=oid_handler), 200, regular_req_headers


@app.route('/api/v1/user', methods=['POST'])
@check_req_body_wrapper('username', 'password')
def new_user():
    try:
        # 可以保证解析不会出错
        json_req_data = json.loads(request.data)
        
        # 防止插入一些奇怪的数据
        user_data = {
            'username': json_req_data['username'],
            'password': json_req_data['password'],
        }
        user_data['created_time'] = datetime.datetime.utcnow()
        user_data['joined_nests'] = []
        user_data['uploaded_musics'] = []
        user_data['alarm_clocks'] = []
        user_data['avatar'] = ''
        user_data['nickname'] = ''
        
        db['_users'].insert_one(user_data)
    
    # 处理用户名已存在的错误
    except errors.DuplicateKeyError:
        return json.dumps({
            'error': 'Username already exists!'
        }), 400, regular_req_headers
    # 处理其他所有错误
    except:
        return _bad_request, 400, regular_req_headers
    
    # 无错误
    print(user_data)
    return json.dumps(user_data, default=oid_handler), 200, regular_req_headers


@app.route('/api/v1/user/<username>', methods=['PUT'])
@check_header_wrapper('authorization')
@auth_wrapper
def edit_user(username):
    # edit start
    # 防止用户名被更改
    update_data = json.loads(request.data)
    if 'alarmClocks' in update_data \
            or 'joinedNests' in update_data \
            or 'uploadedMusics' in update_data \
            or 'username' in update_data:
        return json.dumps({
            'error': 'You can\'t change <Array> or username!'
        }), 400, regular_req_headers
    
    update_data['username'] = username
    
    # 更新并得到最新数据
    result = db['_users'].find_one_and_update(
        {'username': username},
        {'$set': update_data},
        return_document=ReturnDocument.AFTER
    )
    
    if result == None:
        return _no_user_named_xxx, 400, regular_req_headers
    
    # all ok!， 生成待返回数据，
    keys = list(filter(lambda key: key not in ['_id', 'password', 'created_time'], result.keys()))
    values = list(map(lambda key: result[key], keys))
    return json.dumps(dict(zip(keys, values)), default=oid_handler), 200, regular_req_headers


@app.route('/api/v1/user/<username>/joined_nests', methods=['POST'])
@check_header_wrapper('authorization')
@auth_wrapper
@check_req_body_wrapper('nests')
def user_join_nests(username):
    # auth 通过， 防止重复加入
    nests = json.loads(request.data)['nests']
    nests = list(map(lambda id: bson.ObjectId(id), nests))
    
    cursor = db['_nests'].find(
        {
            '_id': {
                '$in': nests
            }
        }
    )
    c_length = len(list((c for c in cursor)))
    
    if c_length != len(nests):
        return json.dumps({
            'error': 'Given nest(s) not exist!'
        }), 400, regular_req_headers
    
    result = db['_users'].find_one(
        {
            'username': username,
            'joined_nests._id': {
                '$in': nests
            }
        }
    )
    if result != None:
        return json.dumps({
            'error': 'Given nest(s) already joined！'
        }), 400, regular_req_headers
    
    # 更新并判断用户是否存在
    result = db['_users'].find_one_and_update(
        {'username': username},
        {
            '$push': {
                'joined_nests': {
                    '$each': list(map(lambda nest: {'_id': nest, 'kept_days': 0}, nests))
                }
            }
        },
        return_document=ReturnDocument.AFTER
    )
    if result == None:
        return _no_user_named_xxx, 400, regular_req_headers
    
    db['_nests'].update_many(
        {
            '_id': {
                '$in': nests
            }
        },
        {
            '$inc': {
                'members_amount': 1
            }
        }
    )
    
    # 用户存在 all ok!， 生成待返回数据，
    keys = list(filter(lambda key: key not in ['_id', 'password', 'created_time'], result.keys()))
    values = list(map(lambda key: result[key], keys))
    return json.dumps(dict(zip(keys, values)), default=oid_handler), 200, regular_req_headers


@app.route('/api/v1/user/<username>/joined_nests', methods=['DELETE'])
@check_header_wrapper('authorization')
@auth_wrapper
@check_req_body_wrapper('nests')
def user_quit_nests(username):
    # 认证成功
    nests = json.loads(request.data)['nests']
    nests = list(map(lambda id: bson.ObjectId(id), nests))
    result = db['_users'].find_one_and_update(
        {
            'username': username,
            'joined_nests._id':
                {
                    '$in': nests
                }
        },
        {
            '$pull': {
                'joined_nests': {
                    '_id': {
                        '$in': nests
                    }
                }
            }
        },
        return_document=ReturnDocument.AFTER
    )
    
    db['_nests'].update_many(
        {
            '_id': {
                '$in': nests
            }
        },
        {
            '$inc': {
                'members_amount': -1
            }
        }
    )
    
    if result == None:
        return json.dumps({
            'error': 'No user or nest matched!'
        }), 400, regular_req_headers
    
    # # 更新成功，生成响应
    # keys = list(filter(lambda key: key not in ['_id', 'password', 'created_time'], result.keys()))
    # values = list(map(lambda key: result[key], keys))
    # return json.dumps(dict(zip(keys, values)), default = oid_handler), 200, regular_req_headers
    
    joined_nests = result['joined_nests']
    
    cursor = db['_nests'].find(
        {
            '_id': {
                '$in': list(map(lambda nest: bson.ObjectId(nest['_id']), joined_nests))
            }
        }
    )
    
    result = {
        'joined_nests': list((c for c in cursor))
    }
    
    return json.dumps(result, default=oid_handler), 200, regular_req_headers


@app.route('/api/v1/user/<username>/joined_nests', methods=['GET'])
@check_header_wrapper('authorization')
@auth_wrapper
def get_all_user_nests(username):
    result = db['_users'].find_one({'username': username})
    if result == None:
        return _no_user_named_xxx, 400, regular_req_headers
    
    joined_nests = result['joined_nests']
    
    cursor = db['_nests'].find(
        {
            '_id': {
                '$in': list(map(lambda nest: bson.ObjectId(nest['_id']), joined_nests))
            }
        }
    )
    
    result = {
        'joined_nests': list((c for c in cursor))
    }
    
    return json.dumps(result, default=oid_handler), 200, regular_req_headers


@app.route('/api/v1/user/<username>/alarm_clocks', methods=['GET'])
@check_header_wrapper('authorization')
@auth_wrapper
def get_all_user_alarm_clock(username):
    result = db['_users'].find_one({'username': username})
    if result == None:
        return _no_user_named_xxx, 400, regular_req_headers
    
    alarm_clocks = result['alarm_clocks']
    
    cursor = db['_alarm_clocks'].find(
        {
            '_id': {
                '$in': alarm_clocks
            }
        }
    )
    
    result = {
        'alarm_clocks': list((c for c in cursor))
    }
    return json.dumps(result, default=oid_handler), 200, regular_req_headers


@app.route('/api/v1/user/<username>/reminds_on_me', methods=['GET'])
@check_header_wrapper('authorization')
@auth_wrapper
def get_all_reminds_on_me(username):
    cursor = db['_reminds'].find(
        {
            'target_username': username
        }
    )
    result = {
        'reminds': list((c for c in cursor))
    }
    return json.dumps(result, default = oid_handler), 200, regular_req_headers

@app.route('/api/v1/user/<username>/reminds_by_me', methods=['GET'])
@check_header_wrapper('authorization')
@auth_wrapper
def get_all_reminds_by_me(username):
    cursor = db['_reminds'].find(
        {
            'owner': username
        }
    )
    result = {
        'reminds': list((c for c in cursor))
    }
    
    return json.dumps(result, default=oid_handler), 200, regular_req_headers

@app.route('/api/v1/user/<username>/<type>/<music_name>', methods=['POST'])
@check_header_wrapper('authorization', 'x-mime-type')
@auth_wrapper
def add_assets(username, type, music_name):
    # 配置青云服务器
    config = Config(qy_access_key, qy_secret_access_key)
    service = QingStor(config)
    buckets = service.list_buckets('pek3a')['buckets']
    
    # 获取业务用 bucket
    [bucket_info] = filter(lambda bucket: bucket['name'] == 'nesthabit', buckets)
    bucket = service.Bucket('nesthabit', 'pek3a')
    
    # 随机一个文件名
    if type == 'uploaded_musics':
        base = 'music'
    elif type == 'avatar':
        base = 'image'
    else:
        return json.dumps({
            'error': 'Invalid operation!'
        }), 400, regular_req_headers
    filename = mimetypes.guess_extension(request.headers.get('x-mime-type'))
    filename = '/%s/%s%s' % (base, str(random.randint(1, 1E15)), filename)
    
    # 上传这个文件
    bucket.put_object(filename, body=request.data)
    
    # 组装 URL
    url = bucket_info['url'] + filename
    
    if type == 'uploaded_musics':
        # 更新数据库
        inserted_id = db['_musics'].insert_one({
            'url': url,
            'music_name': music_name,
            'created_time': datetime.datetime.utcnow(),
            'creator': username
        }).inserted_id
        
        result = db['_users'].find_one_and_update(
            {'username': username},
            {
                '$push': {
                    'uploaded_musics': inserted_id
                }
            },
            return_document=ReturnDocument.AFTER
        )
    elif type == 'avatar':
        result = db['_users'].find_one_and_update(
            {'username': username},
            {
                '$set': {
                    'avatar': url
                }
            },
            return_document=ReturnDocument.AFTER
        )
    else:
        return json.dumps({
            'error': 'Invalid operation!'
        }), 400, regular_req_headers
    
    if result == None:
        bucket.delete_object(filename)
        return _no_user_named_xxx, 400, regular_req_headers
    
    # 生成响应
    if type == 'uploaded_musics':
        result = {
            '_id': inserted_id,
            'name': music_name,
            'url': url
        }
        return json.dumps(result, default=oid_handler), 200, regular_req_headers
    
    keys = list(filter(lambda key: key not in ['_id', 'password', 'created_time'], result.keys()))
    values = list(map(lambda key: result[key], keys))
    return json.dumps(dict(zip(keys, values)), default=oid_handler), 200, regular_req_headers


@app.route('/api/v1/user/<username>/nest/<nest_id>/punches', methods=['GET'])
@check_header_wrapper('authorization')
@auth_wrapper
def get_punches(username, nest_id):
    
    cursor = db['_punches'].find(
        {
            'username': username,
            'target_nest': bson.ObjectId(nest_id)
        }
    )
    
    punches = list((c for c in cursor))
    
    days = list(map(lambda punch: punch['day'], punches))
    
    return json.dumps({
        'days': days
    }), 200, regular_req_headers


@app.route('/api/v1/test/speed_test')
@check_header_wrapper('authorization')
@auth_wrapper
def speed_test(username):
    pre_time = time.time()
    cursor = db['_users'].find({})
    
    ret = {
        "users": list(cursor),
        "time_cost": time.time() - pre_time
    }
    return json.dumps(ret, default=oid_handler), 200, regular_req_headers


@app.route('/api/v1/test/speed_test/no_db')
@check_header_wrapper('authorization')
@auth_wrapper
def speed_test_no_db(username):
    pre_time = time.time()
    ret = {
        "time_cost": time.time() - pre_time
    }
    return json.dumps(ret, default=oid_handler), 200, regular_req_headers