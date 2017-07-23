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


@app.route('/api/v1/remind', methods=['POST'])
@check_header_wrapper('authorization')
@auth_wrapper
@check_req_body_wrapper('music_id', 'text', 'target_username',
                        'target_alarm_clock', 'start_time',
                        'end_time', 'from_nest')
def add_reminds(username):
    json_req_data = json.loads(request.data)
    try:
        # 新建
        keys = ['music_id', 'text', 'target_username',
                'target_alarm_clock', 'start_time',
                'end_time', 'from_nest']
        
        values = map(lambda key: json_req_data[key], keys)
        data_to_insert = dict(zip(keys, values))
        
        data_to_insert['music_id'] = bson.ObjectId(data_to_insert['music_id'])
        data_to_insert['target_alarm_clock'] = bson.ObjectId(data_to_insert['target_alarm_clock'])
        data_to_insert['from_nest'] = bson.ObjectId(data_to_insert['from_nest'])
        data_to_insert['start_time'] = datetime.datetime.fromtimestamp(data_to_insert['start_time'])
        data_to_insert['end_time'] = datetime.datetime.fromtimestamp(data_to_insert['end_time'])
        data_to_insert['created_time'] = datetime.datetime.utcnow()
        data_to_insert['owner'] = username
        
        db['_reminds'].insert_one(data_to_insert)
    
    except errors.DuplicateKeyError:
        return json.dumps({
            'error': 'Remind already exists!'
        }), 400, regular_req_headers
    
    # 处理其他所有错误
    except:
        return _bad_request, 400, regular_req_headers
    
    # 无错误
    return json.dumps(data_to_insert, default=oid_handler), 200, regular_req_headers



