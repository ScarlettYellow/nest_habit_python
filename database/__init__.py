
#
# conn = pymysql.connect(
#   host = '115.159.197.27',
#   port = 3306,
#   user = 'faraway',
#   password = 'hzylovelyl',
#   db = 'faraway'
# )
# cur = conn.cursor()


from pymongo import MongoClient
from pymongo import errors
from pymongo import ReturnDocument

client = MongoClient('139.198.11.28', 27017)

db = client['nesthabit']
