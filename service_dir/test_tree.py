from unittest import TestCase
from pymongo import MongoClient
from csv import DictReader, DictWriter
from pprint import pprint
from multiprocessing import Process

import shutil
import os
import pickle

from serviceDir import ServiceDir as sd
from serviceDir import MongoTransaction
from serviceDir import Const, DB_INFO

client = None
db = None
SD = None
mt = None
baseSD = None

def setUp():
    global client, SD, db, mt, baseSD
    client = MongoClient(DB_INFO['MONGO_HOST'], DB_INFO['MONGO_PORT'])
    if DB_INFO['DB_NAME'] in client.database_names():
        client.drop_database(DB_INFO['DB_NAME'])
    if DB_INFO['CACHE_DB_NAME'] in client.database_names():
        client.drop_database(DB_INFO['CACHE_DB_NAME'])
    db = client[DB_INFO['DB_NAME']]
    cdb = client[DB_INFO['CACHE_DB_NAME']]
    SD = sd('tester')
    baseSD = sd('baseTester')
    os.system('rm -rf importDir')
    shutil.copytree('importDirBak','importDir')
    SD.connectMongo()
    baseSD.connectMongo()
    #mt = MongoTransaction('tester')
    #mt.connectMongo()

def tearDown():
    global client
    client.close()
    #mt.close()
    SD.close()
    baseSD.close()

class ServiceDirTest(TestCase):
    '''
    创建数据库表结构
    '''
    def test_01_importTab(self):
        #先检查表，如果都没有则直接创建
        #client.drop_database(DB_INFO['DB_NAME'])
        SD.importTab()
        SD.copy_table()
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
        rs = list(db[table].find(match))
        self.assertEqual(len(rs), 2)
        self.assertEqual(rs[-2]['attr_set_id'], 1)
        self.assertEqual(rs[-2]['value'], 'rampage')


    def test_10_get_tree(self):
        rs = SD.get_tree()
        #self.assertTrue(rs is None)
        self.assertTrue(isinstance(rs, dict))
        self.assertTrue(len(rs['children']) > 0)
        #self.assertTrue(False)

    def test_14_del_branch(self):
        #删除一个大目录 
        tree = SD.get_tree(to_dict=False)
        tree.show()
        rs = SD.del_branch('root/2')
        tree = SD.get_tree(to_dict=False)
        tree.show()
        pprint([i.data[1] for i in tree.nodes.values() if i.data[0] != 'root'])
        node_values = [i.data[1] for i in tree.nodes.values() if i.data[0] != 'root']
        self.assertNotIn('root/2', node_values)

        #删除叶子
        rs = SD.del_branch('root/1/1/1')
        tree = SD.get_tree(to_dict=False)
        tree.show()
        node_values = [i.data[1] for i in tree.nodes.values() if i.data[0] != 'root']
        self.assertNotIn('root/1/1/1', node_values)
        #self.assertTrue(False)

    def test_13_create_branch(self):
        #增加叶子
        print(client.CACHE_COP.tester_FACT_ATTR.count())
        SD.create_branch('root/1/1/1', 'test_leaf')
        print(client.CACHE_COP.tester_FACT_ATTR.count())
        print(list(client.CACHE_COP.tester_FACT_ATTR.find()))
        #check if data added to table or not
        t = SD.get_tree(to_dict=False)
        t.show()
        self.assertIn('root/服务1/scene1/attr_set1/test_leaf', [i for i in t.nodes])

        #增加中间节点
        SD.create_branch('root/1', 'test_service')
        t = SD.get_tree(to_dict=False)
        t.show()
        print([i for i in t.nodes])
        self.assertIn('root/服务1/test_service', [i for i in t.nodes])

        #增加最上层节点
        SD.create_branch('root', 'serviceX')
        t = SD.get_tree(to_dict=False)
        t.show()
        print([i for i in t.nodes])
        self.assertIn('root/serviceX', [i for i in t.nodes])

    def test_15_modify_branch(self):
        #这个函数是对节点进行测试，还需要另一个函数对属性进行测试 
        node_id = 'root/1'
        new_val_dict = {'_id': 1, 'name': '特殊服务1', 'service_dir_id': 1}
        SD.modify_branch(node_id, new_val_dict)
        t = SD.get_tree(to_dict=False)
        t.show()
        print([i for i in t.nodes])
        self.assertIn('root/特殊服务1', [i for i in t.nodes])

        #if the _id is changed by client which is not allowed
        new_val_dict = {'_id': 2, 'name': '特殊服务1', 'service_dir_id': 1}
        SD.modify_branch(node_id, new_val_dict)
        t = SD.get_tree(to_dict=False)
        t.show()
        print([i for i in t.nodes])
        self.assertIn('root/特殊服务1', [i for i in t.nodes])

        #change the parent directory
        new_val_dict = {'_id': 1, 'name': '特殊服务1', 'service_dir_id': 2}
        SD.modify_branch(node_id, new_val_dict)
        t = SD.get_tree(to_dict=False)
        t.show()
        print([i for i in t.nodes])
        self.assertIn('root/特殊服务1', [i for i in t.nodes])
        SD.save_tables()
        #出现saved_user_table_name的表，并且数据不为空
        saved_tables = list(filter(lambda x: x.startswith('saved'), client[DB_INFO['CACHE_DB_NAME']].collection_names()))
        self.assertTrue(len(saved_tables) > 0)
        for s_tab in saved_tables:
            self.assertGreater(client[DB_INFO['CACHE_DB_NAME']][s_tab].count(),0)


    def test_11_modify_attr(self):
        node_id = 'root/1/1/1/3'
        new_val_dict = {'_id': 1, 'name':'属性1', 'type_id': 1, 'value': 100,
                'attr_set_id': 3}
        SD.modify_branch(node_id, new_val_dict)
        t = SD.get_tree(to_dict=False)
        t.show()
        print([i for i in t.nodes])
        self.assertIn('root/服务1/scene1/attr_set3/属性1', [i for i in t.nodes])

        baseSD.copy_table()
        baseT = baseSD.get_tree()
        #print('baseT=======================================')
        #pprint(baseT)
        t1 = SD.get_tree()
        self.assertNotEqual(baseT, t1)
        commit_rs = SD.commit()        
        print(commit_rs)
        baseSD.refresh_cache()
        t2 = baseSD.get_tree()
        self.maxDiff = None
        self.assertEqual(t1, t2)
        #self.assertTrue(False)

    def test_20_commit_while_lock_exists(self):
        with open(SD.lock_file_name, 'w') as f:
            f.write('owner={}'.format('root'))
        rec1 = client[DB_INFO['DB_NAME']][Const.FACT_ATTR['tabName']].find_one()
        rec1['value'] = 10000
        SD.modify_from_client('FACT_ATTR', [rec1])
        self.assertTrue(not SD.commit())
        os.system('rm -f {}'.format(SD.lock_file_name))


