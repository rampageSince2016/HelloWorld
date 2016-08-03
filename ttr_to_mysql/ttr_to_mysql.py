from mysql import connector
from io import BytesIO
from pprint import pprint

import os, datetime, traceback, sys
import msgpack, snappy

#msql配置信息
mysql_cfg = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'COP',
    'buffered': True
    }

#ttr的文件目录定义
BPC_TTR_DIR = '/home/csxxf/work/ttr'

#这个目录下的ttr最后要保存到COP数据库里的表名,可根据不同组件定义到不同表
TABLE_NAME = 'HALL'

#这个表需要保存的字段, 不够可自行增加
FIELD_LIST = [
        {'field':'Host', 'length': 255},
        {'field':'Referer','length': 1000},
        {'field':'SrcIp','length': 255},
        {'field':'DestIp','length': 255},
        {'field':'SrcPort','length': 255},
        {'field':'DestPort','length': 255},
        {'field':'TransType','length': 255},
        {'field':'Uri','length': 1000},
        {'field':'UriPath','length': 1000},
        {'field':'Url','length': 1000},
        {'field':'UrlPath','length': 1000},
        {'field':'action','length': 255},
        {'field':'menuId','length': 255},
        {'field':'trans_type','length': 255},
        {'field':'ret_code','length': 255},
        ]

#默认包含的字段, 由于req和resp合并，以下字段不能在FIELD_LIST中定义
DEFAULT_FIELD = ['ts', 'RRA']


TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class FileMgr:
    def list_dir(self, dir_name):
        def numerial_order(x):
            parts = x.split('.')
            return (parts[0], int(parts[1]))

        if os.path.exists(dir_name):
            file_list = sorted([i for i in os.listdir(dir_name) if i.endswith('spz')], key = lambda x: numerial_order(x))
            file_path_list = list(map(lambda f: os.path.sep.join([dir_name, f]), file_list))
            return file_path_list
        raise Exception('dir not found')

    def filter_list_dir(self, file_list, rule):
        pass

class MysqlMgr:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.__check_database()
        self.__check_table()

    def connect(self,  cfg = mysql_cfg):
        self.conn = connector.Connect(**cfg)
        self.cursor = self.conn.cursor()

    def __check_database(self):
        config = mysql_cfg.copy()
        config.pop('database')
        self.connect(cfg = config)
        try:
            self.cursor.execute('create database if not exists {} DEFAULT CHARSET utf8 COLLATE utf8_general_ci'.format(mysql_cfg['database']))
        finally:
            self.close()

    def __check_table(self):
        self.connect()
        try:
            self.cursor.execute('select 1 from {}'.format(TABLE_NAME))
        except:
            L = list()
            for x in FIELD_LIST:
                L.append(' '.join([x['field'], 'varchar(' + str(x['length']) + ')']))
            fields = '(id int(11) AUTO_INCREMENT PRIMARY KEY, ' + ','.join(L) + ', req_time datetime, res_time datetime)'
            sql = 'create table {} {} engine=INNODB default charset=utf8'.format(TABLE_NAME, fields)
            self.cursor.execute(sql)
        finally:
            self.close()

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        except:
            raise

    def insertData(self, dataList):
        keyList = [i['field'] for i in FIELD_LIST] + ['req_time', 'res_time']
        D = dict()
        for subItem in dataList:
            if not subItem.get('RRA'):
                continue
            if subItem.get('RRA').lower() == 'req':
                D['req_time'] = datetime.datetime.fromtimestamp(float(subItem['ts']))
            if subItem.get('RRA').lower() == 'resp':
                D['res_time'] = datetime.datetime.fromtimestamp(float(subItem['ts']))
            for fieldItem in FIELD_LIST:
                if not D.get(fieldItem['field']):
                    D[fieldItem['field']] = subItem.get(fieldItem['field'])
        pos_vals = ','.join(['%s' for i in range(len(keyList))])
        pos_fields = '(id, ' + ','.join(keyList) + ')'
        L = list()
        for key in keyList:
            L.append(D.get(key))
        sql = 'insert into {} {} values (null, {})'.format(TABLE_NAME, pos_fields, pos_vals)
        self.cursor.execute(sql, tuple(L))
        self.conn.commit()


class DataMgr:
    def __init__(self):
        self.fMgr = FileMgr()
        self.sqlMgr = MysqlMgr()

    def snappy_unpack(self, file_name):
        print('unpacking', file_name, '...')
        if not os.path.exists(file_name):
            raise Exception('snappy file not found!')
        out = BytesIO()
        try:
            with open(file_name, 'rb') as f:
                decompressor = snappy.StreamDecompressor()
                while True:
                    buf = f.read(65536)
                    if not buf: 
                        break
                    buf = decompressor.decompress(buf)
                    if buf:
                        out.write(buf)
                decompressor.flush()
            tell = out.tell()
            print(tell)
            if tell == 0:
                return []
            out.seek(0)
            unpacker = msgpack.Unpacker(out, encoding='utf-8')
            rs = [i for i in unpacker]
            return rs
        except UnicodeDecodeError:
            print('an UnicodeDecodeError occur in the file, so this file can not be parsed!')
            return []
        finally:
            out.close()

    def start_tasks(self):
        tasklist = self.fMgr.list_dir(BPC_TTR_DIR)
        self.sqlMgr.connect()
        try:
            for file_name in tasklist:
                for item in self.snappy_unpack(file_name):
                    raw_record = item.get('_raw_records')
                    if raw_record:
                        self.sqlMgr.insertData(raw_record)
        except:
            print(traceback.format_exc())
        finally:
            self.sqlMgr.close()
                

class InteractiveMsg(DataMgr):
    def diplay_pack(self, in_file):
        rs = self.snappy_unpack(in_file)
        for i in rs:
            pprint(i)
            input('按任意键继续...')


def distinct_from_default():
    global FIELD_LIST
    FIELD_LIST = list(filter(lambda x: x['field'] not in DEFAULT_FIELD, FIELD_LIST))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        distinct_from_default()
        dm = DataMgr()
        dm.start_tasks()
    elif len(sys.argv) == 2:
        im = InteractiveMsg()
        im.diplay_pack(sys.argv[1])
    else:
        raise Exception('未知参数')
        
