from flask_init import app

import json
import sys

import user
import nest

# @app.errorhandler(500)
# def internal_server_err(e):
#   return json.dumps({
#     'error': 'Unexpected error!',
#     # 'msg': dir(sys.exc_info()[0])
#     'msg': str(e)
#   }), 500, { 'content-type': 'application/json' }

if __name__ == '__main__':
  app.run(host = '127.0.0.1', port = '8081')

