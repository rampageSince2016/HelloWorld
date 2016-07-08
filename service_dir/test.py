from unittest import TestCase
from pymongo import MongoClient
from csv import DictReader, DictWriter
from pprint import pprint

import shutil
import os

from serviceDir import ServiceDir as sd
from serviceDir import Const, DB_INFO

client = None
db = None
SD = None

def setUp():
    global client, SD, db
    client = MongoClient(DB_INFO['MONGO_HOST'], DB_INFO['MONGO_PORT'])
    db = client[DB_INFO['DB_NAME']]
    SD = sd()
    os.system('rm -rf importDir')
    shutil.copytree('importDirBak','importDir')

def tearDown():
    global client
    client.close()

class ServiceDirTest(TestCase):
    '''
    创建数据库表结构
    '''
    def test_importTab(self):
        #先检查表，如果都没有则直接创建
        client.drop_database(DB_INFO['DB_NAME'])
        SD.importTab()
        self.assertIn('FACT_ATTR', db.collection_names())
        self.assertIn('FACT_SERVICE', db.collection_names())
        self.assertIn('FACT_ATTR_SET', db.collection_names())
        self.assertIn('FACT_SCENE', db.collection_names())

        #如果有,先检查id如果不存在则增加，否则update
        L = list()
        table = 'FACT_ATTR'
        filepath = os.path.sep.join([os.path.abspath(Const.DATA_IN), table])
        with open(filepath, 'r') as f:
            dReader = DictReader(f)
            L = [i for i in dReader]
        L[-1]['attr_set_id'] = 1
        L[-1]['value'] = 'rampage'
        L.append({'_id': 4, 'name': 'attr4', 'type_id':6, 'value': 'test', 'attr_set_id': 2})
        with open(filepath, 'w') as f:
            titles = L[-1].keys()
            dwriter = DictWriter(f, titles)
            header = dict(zip(titles, titles))
            dwriter.writerow(header)
            dwriter.writerows(L)

        SD.importTab()
        #这里顺便把查询也一起测了
        match = {'_id': {'$in': [3,4]}}
        rs = SD.find(table, match = match)
        self.assertEqual(len(rs), 2)
        self.assertEqual(rs[-2]['attr_set_id'], 1)
        self.assertEqual(rs[-2]['value'], 'rampage')

    def test_get_tree(self):
        rs = SD.get_tree()
        #self.assertTrue(rs is None)
        self.assertTrue(isinstance(rs, dict))
        self.assertTrue(len(rs['children']) > 0)
        #self.assertTrue(False)

    def test_del_branch(self):
        #删除一个大目录 
        tree = SD.get_tree(to_dict=False)
        tree.show()
        rs = SD.del_branch('root/2')
        tree = SD.get_tree(to_dict=False)
        tree.show()
        self.assertNotIn('root/2', tree.nodes)

        #删除叶子
        rs = SD.del_branch('root/1/1/1')
        tree = SD.get_tree(to_dict=False)
        tree.show()
        self.assertNotIn('root/1/1/1', tree.nodes)
        self.assertTrue(False)

