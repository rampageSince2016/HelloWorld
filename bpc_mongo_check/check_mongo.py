from pymongo import MongoClient
from datetime import datetime
import sys

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
now = datetime.now().strftime(DATE_FORMAT)

if len(sys.argv) != 2:
    print('请按照如下格式输入命令:\n\t python3 ./check_mongo.py "{}"'.format(now))
    exit(0)

input_time = sys.argv[1]
query_time = datetime.strptime(input_time, DATE_FORMAT)

client = MongoClient('10.252.21.115', 27019)
ex = client.BUSI_MONITOR.EX_BUSINESS
rs = ex.count({
    'M_QB_status': {'$exists': True},
    'end_time': {'$gt': query_time}
})
print('从{}往后已经跑了{}条数据'.format(input_time,rs))
