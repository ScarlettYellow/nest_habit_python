import json
import bson
import datetime

from flask_init import app
from flask_init import request

from database import db
from database import errors

from common import _bad_request
from common import regular_req_headers

from common import auth_wrapper
from common import check_req_body_wrapper
from common import check_header_wrapper
from common import oid_handler




@app.route('/api/v1/punch', methods=['POST'])
@check_header_wrapper('authorization')
@auth_wrapper
@check_req_body_wrapper('target_nest')
def punch(username):
    # 今天凌晨的时间戳
    # start_timestamp = math.floor(datetime.datetime.timestamp(datetime.datetime.utcnow()) / 24 / 3600)
    # start = datetime.datetime.fromtimestamp(start_timestamp)
    
    # 明天凌晨的时间戳
    # end_timestamp = math.floor(time.time() / 24 / 3600) + 1
    # end = datetime.datetime.fromtimestamp(end_timestamp)
    
    
    
    # cursor = db['_punches'].find(
    #     {
    #         'operate_time': {
    #             '$gte': start,
    #             '$lt': end
    #         }
    #     }
    # )
    #
    # length = len(list(cursor))
    
    # if length > 0:
    #     return json.dumps({
    #         'error': 'Do not repeat the operation!'
    #     }), 400, regular_req_headers
    
    json_data = json.loads(request.data)
    
    data_to_insert = {
        'target_nest': bson.ObjectId(json_data['target_nest']),
        'operate_time': datetime.datetime.utcnow(),
        'username': username,
        'day': datetime.datetime.utcnow().strftime('%Y%m%d')
    }
    
    try:
        insert_id = db['_punches'].insert_one(
            data_to_insert
        ).inserted_id
    
    except(errors.DuplicateKeyError):
        return json.dumps({
            'error': 'Do not repeat the operation!'
        }), 400, regular_req_headers
    
    except:
        return _bad_request, 400, regular_req_headers
    
    data_to_insert['_id'] = insert_id
    
    return json.dumps(data_to_insert, default = oid_handler), 200, regular_req_headers
