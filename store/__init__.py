from qingstor.sdk.service.qingstor import QingStor
from qingstor.sdk.config import Config

from settings import qy_access_key
from settings import qy_secret_access_key

# config = Config(qy_access_key, qy_secret_access_key)
# service = QingStor(config)
# output = service.list_buckets()

nesthabit = {}
# 如果是全新的服务器，初始化它
# if output['count'] <= 0:
#   nesthabit = service.Bucket('nesthabit', 'pek3a')
#   nesthabit.put()
# else:
#   if 'nesthabit' not in list(map(lambda bucket: bucket['name'], output['buckets'])):
#     nesthabit = service.Bucket('nesthabit', 'pek3a')
#     nesthabit.put()
#   else:
#     nesthabit = service.Bucket('nesthabit', 'pek3a')
# 初始化完毕


