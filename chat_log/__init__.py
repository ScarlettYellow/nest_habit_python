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


@app.route('/api/v1/chat_log', methods=['POST'])
@check_header_wrapper('authorization')
@auth_wrapper
@check_req_body_wrapper('value', 'target_nest')
def add_chat(username):
    json_data = json.loads(request.data)
    
    json_data['time'] = datetime.datetime.utcnow()
    json_data['username'] = username
    json_data['target_nest'] = bson.ObjectId(json_data['target_nest'])
    
    db['_chat_log'].insert_one(json_data)
    
    return json.dumps(json_data, default = oid_handler), 200, regular_req_headers