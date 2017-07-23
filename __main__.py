from flask_init import app

import json
import sys

import user
import nest
import alarmclock

@app.errorhandler(500)
def internal_server_err(e):
  return json.dumps({
    'error': 'Unexpected error! Maybe the back-end programmer is the one who to be blame.',
  }), 500, { 'content-type': 'application/json' }

@app.errorhandler(405)
def methods_not_allowed(e):
  return json.dumps({
    'error': 'Method not allowed!',
  }), 405, {'content-type': 'application/json'}

@app.errorhandler(404)
def methods_not_allowed(e):
  return json.dumps({
    'error': 'Not Found!',
  }), 404, {'content-type': 'application/json'}



if __name__ == '__main__':
  app.run(host = '127.0.0.1', port = '8081')

