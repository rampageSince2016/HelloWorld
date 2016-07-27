from pymongo import MongoClient
from pprint import pprint
from treelib import Tree

import msgpack
import json
import os, shutil
import csv

DB_INFO = {
        'MONGO_HOST': 'localhost',
        'MONGO_PORT': 27019,
        'DB_NAME': 'COP',
        'CACHE_DB_NAME': 'CACHE_COP'
}

BCP_TTR_DIRS = {
        'INTF': ''
}

class Const:
    DATA_IN = './importDir'
    DATA_OUT = './exportDir'
    TTR_IN = '/home/csxxf/work/ttr'
    DIM_TYPE = {'tabName': 'DIM_TYPE'}
    FACT_SERVICE = {'tabName': 'FACT_SERVICE', '_id': '_id'}
    FACT_SCENE = {'tabName': 'FACT_SCENE', 'foreignKey': 'service_id', '_id': '_id'}
    FACT_ATTR_SET = {'tabName': 'FACT_ATTR_SET', 'foreignKey': 'scene_id', '_id': '_id'}
    FACT_ATTR = {'tabName': 'FACT_ATTR', 'foreignKey': 'attr_set_id', '_id': '_id'}
    SEQ = [
            FACT_SERVICE,
            FACT_SCENE,
            FACT_ATTR_SET,
            FACT_ATTR
    ]


class FlexTree(Tree):
    def to_dict(self, nid=None, key=None, sort=True, reverse=False, with_data=False):

        def get_children(tree_dict, ntag):
            for k in tree_dict:
                if tree_dict[k] == ntag:
                    return tree_dict['children']

        nid = self.root if (nid is None) else nid
        ntag = self[nid].tag
        tree_dict = {'text': ntag, "children": []}

        if with_data:
            tree_dict["index"] = self[nid].data

        if self[nid].expanded:
            queue = [self[i] for i in self[nid].fpointer]
            key = (lambda x: x) if (key is None) else key
            if sort:
                queue.sort(key=key, reverse=reverse)

            for elem in queue:
                children = get_children(tree_dict, ntag)
                children.append(
                    self.to_dict(elem.identifier, with_data=with_data, sort=sort, reverse=reverse))
            ch = get_children(tree_dict, ntag)
            if len(ch) == 0:
                tree_dict = {'text': self[nid].tag} if not with_data else \
                        {'text': ntag, "index":self[nid].data}
            return tree_dict


class MongoBase:
    def __init__(self):
        self.client = None
        self.db = None
        self.baseDb = None

    def connectMongo(self):
        self.client = MongoClient(DB_INFO['MONGO_HOST'], DB_INFO['MONGO_PORT'])
        self.db = self.client[DB_INFO['CACHE_DB_NAME']]
        self.baseDb = self.client[DB_INFO['DB_NAME']]

    def close(self):
        try:
           self.client.close()
        except:
            raise

    def find(self, table, match=None, project=None, nosql=None):
        if nosql:
            rs = list(self.db[table].aggregate(nosql))
        else:
            rs = list(self.db[table].find(match, project))
        return rs


class Authority:
    def __init__(self):
        pass

    def check_write(self, user):
        if os.path.exists('dir_service_lock'):
            return False
        return True

class MongoTransaction(MongoBase):
    def __init__(self):
        super().__init__()

    def check_cache(self, user):
        self.connectMongo()
        try:
            pass
        finally:
            self.close()

    def commit(self, user):
        pass

    def acquired(self, user):
        pass

    def release(self, user):
        pass

    def save(self, user, data):
        pass


class ServiceDir(MongoTransaction):
    def __init__(self):
        super().__init__()

    def createIdx(self):
        self.db[Const.FACT_SCENE['tabName']].ensure_index(Const.FACT_SCENE['foreignKey'])
        self.db[Const.FACT_ATTR_SET['tabName']].ensure_index(Const.FACT_ATTR_SET['foreignKey'])
        self.db[Const.FACT_ATTR['tabName']].ensure_index(Const.FACT_ATTR['foreignKey'])

        
    def exportTab(self):
        self.connectMongo()
        try:
            for tab in self.db.collection_names():
                fpath = os.path.sep.join([os.path.abspath(Const.DATA_OUT), tab])
                with open(fpath, 'w') as f_out:
                    pass
                list(self.find())
        finally:
            self.close()
        

    def importTab(self):
        self.connectMongo()
        try:
            for f in os.listdir(Const.DATA_IN):
                fpath = os.path.sep.join([os.path.abspath(Const.DATA_IN), f])
                with open(fpath, 'r') as f_in:
                    for row in csv.DictReader(f_in):
                        for k, v in row.items():
                            if k.find('id') > -1:
                                row[k] = int(v)
                        if self.find(f, match = {'_id': row['_id']}):
                            self.baseDb[f].update({
                                '_id' : row['_id']
                                }, {
                                    '$set': row
                                })
                        else:
                            self.db[f].insert(row)
            self.createIdx()
        finally:
            self.close()


    def all_tree_sql(self):
        L_SCENE = {'$lookup':{
            'from': 'FACT_SCENE',
            'localField': '_id',
            'foreignField':Const.FACT_SCENE['foreignKey'],
            'as': 'scene'
        }}
        U_SCENE = {'$unwind': {'path': '$scene', 'preserveNullAndEmptyArrays': True }}
        L_ATTR_SET = {'$lookup': {
            'from': 'FACT_ATTR_SET',
            'localField': 'scene._id',
            'foreignField': Const.FACT_ATTR_SET['foreignKey'],
            'as': 'attr_set'
        }}
        U_ATTR_SET = {'$unwind': {
            'path': '$attr_set',
            'preserveNullAndEmptyArrays': True
        }}
        L_ATTR = {'$lookup': {
            'from': 'FACT_ATTR',
            'localField': 'attr_set._id',
            'foreignField': Const.FACT_ATTR['foreignKey'],
            'as': 'attr'
        }}
        U_ATTR = {'$unwind': {
            'path'    : '$attr',
            'preserveNullAndEmptyArrays': True
        }}
        nosql = [L_SCENE, U_SCENE, L_ATTR_SET, U_ATTR_SET, L_ATTR, U_ATTR]
        return nosql


    def generate_dir_tree(self, treeList):
        t = FlexTree()
        t.create_node('root', 'root', data=('root', ))
        if len(treeList) < 1:
            return 
        for item in treeList:
            treePath = [
                    item.get('name'), 
                    item.get('scene', {}).get('name')
            ]
            idPath = [
                    str(item.get('_id')),
                    str(item.get('scene', {}).get('_id'))
            ]
            while None in treePath:
                treePath.remove(None)
            while None in idPath:
                idPath.remove(None)
            for i in range(1, len(treePath) + 1):
                treePathLink = os.path.sep.join(['root'] + treePath[:i])
                treeIdPath = os.path.sep.join(['root'] + idPath[:i])
                if not t.get_node(treePathLink):
                    parent_path, node_name = os.path.split(treePathLink)
                    t.create_node(node_name, treePathLink, parent=parent_path, data=(treeIdPath,item.get('value')))
        return t
            
    def generate_leaf_tree(self, treeList):
        t = FlexTree()
        t.create_node('root', 'root', data=('root',))
        if len(treeList) < 1:
            return 
        for item in treeList:
            treePath = [
                    item.get('name'), 
                    item.get('scene', {}).get('name'),
                    item.get('attr_set', {}).get('name'),
                    item.get('attr', {}).get('name')
            ]
            idPath = [
                    str(item.get('_id')),
                    str(item.get('scene', {}).get('_id')),
                    str(item.get('attr_set', {}).get('_id')),
                    str(item.get('attr', {}).get('_id'))
            ]
            while None in treePath:
                treePath.remove(None)
            while None in idPath:
                idPath.remove(None)
            for i in range(1, len(treePath) + 1):
                treePathLink = os.path.sep.join(['root'] + treePath[:i])
                treeIdPath = os.path.sep.join(['root'] + idPath[:i])
                if not t.get_node(treePathLink):
                    parent_path, node_name = os.path.split(treePathLink)
                    t.create_node(node_name, treePathLink, parent=parent_path, data=(treeIdPath, item.get('attr', {}).get('value')))
        return t

    def get_dir_tree(self,to_dict=True):
        self.connectMongo()
        try:
            nosql = self.all_tree_sql()
            rs = self.find(Const.FACT_SERVICE_DIR['tabName'], nosql = nosql)
            tree = self.generate_dir_tree(rs)
            if tree:
                if to_dict:
                    return tree.to_dict(with_data=True)
                else:
                    return tree
            else:
                return None
        finally:
            self.close()

    def get_tree(self,to_dict=True):
        self.connectMongo()
        try:
            nosql = self.all_tree_sql()
            rs = self.find(Const.FACT_SERVICE['tabName'], nosql = nosql)
            tree = self.generate_leaf_tree(rs)
            if tree:
                if to_dict:
                    return tree.to_dict(with_data=True)
                else:
                    return tree
            else:
                return None
        finally:
            self.close()


    def del_branch(self, tree_index):
        self.connectMongo()
        try:
            tree = self.get_tree(to_dict=False)
            nodes = set(list(tree.nodes.values()))
            leaves = set(tree.leaves())
            node_leaf_set = nodes | leaves
            to_be_del = filter(lambda x: x.data[0].startswith(tree_index), node_leaf_set)
            for item in to_be_del:
                node_values = [int(i) for i in item.data[0].split(os.path.sep) if i != 'root' ]
                key_values = tuple(zip([y['_id'] for y in Const.SEQ], node_values))
                if len(key_values) < 1:
                    raise Exception('传入的tree_index解析出错')
                last_one = key_values[-1]
                match = {last_one[0]: last_one[1]}
                table = Const.SEQ[len(key_values) - 1]['tabName']
                self.db[table].remove(match)
        finally:
            self.close()


    def create_branch(self, parent_id, node_name):
        self.connectMongo()
        try:
            ids = [int(i) for i in parent_id.split(os.path.sep) if i != 'root']
            if not ids:
                table = Const.SEQ[0]['tabName']
                idx = None
                nosql = [{'$group':{
                    '_id': None,
                    'id': {'$max': '$_id'}
                    }}]
                idxList = list(self.find(table, nosql = nosql))
                if len(idxList) < 1:
                    idx = 1
                else:
                    idx = idxList[0]['id'] + 1
                item = {'_id': idx, 'name': node_name}
                self.db[table].insert(item)
                return
            key_values = tuple(zip([y['_id'] for y in Const.SEQ], ids))
            last_one = key_values[-1]
            if len(key_values) >= len(Const.SEQ):
                raise Exception('叶子上加不了节点')
            table = Const.SEQ[len(key_values)]['tabName']
            foreignKey = Const.SEQ[len(key_values)]['foreignKey']
            idx = None
            nosql = [{'$group':{
                '_id': None,
                'id': {'$max': '$_id'}
                }}]
            idxList = list(self.find(table, nosql = nosql))
            if len(idxList) < 1:
                idx = 1
            else:
                idx = idxList[0]['id'] + 1
            item = {'_id': idx, foreignKey: last_one[1], 'name': node_name}
            self.db[table].insert(item)
        finally:
            self.close()


    def modify_branch(self, node_id, new_val_dict):
        self.connectMongo()
        try:
            ids = [int(i) for i in node_id.split(os.path.sep) if i != 'root']
            if ids:
                name_id_match = tuple(zip([y['_id'] for y in Const.SEQ], ids))
                last_one = name_id_match[-1]
                table = Const.SEQ[len(name_id_match) - 1]['tabName']
                new_val_dict['_id'] = ids[-1]
                self.db[table].update({
                    '_id': ids[-1]
                }, {    
                    '$set': new_val_dict
                })
            else:
                raise Exception('不能对root节点进行修改')
        except:
            self.close()

class FileMgr:
    def list_dir(self, dir_name):
        if os.path.exists(dir_name):
            file_path_list = sorted(list(map(lambda f: os.path.sep.join([dir_name, f]), os.listdir(dir_name))))
            return file_path_list
        raise Exception('dir not found')

    def filter_list_dir(self, file_list, rule):
        pass

    def move_file(self, src, dst):
        if not os.path.isdir(dst):
            dst_dir = os.path.dirname(dst)
        else:
            dst_dir = dst
        if not os.path.exists(dst_dir):
            os.makedirs(dst)
        if os.path.exists(src):
            shutil.move(src, dst)

    def dir_split(self, file_name, step = 2):
        L = file_name.split(os.path.sep)
        if len(L) > 1:
            return os.path.sep.join(L[-2:])
        raise Exception('check if file path is valid')

class DataProvider:
    def __init__(self):
        self.fMgr = FileMgr()

    def get_ttr_paths(self):
        if len(ttrs) > 2:
            return ttrs[:-1]
        return None

    def switch_workspace(self, src_dir, dst_dir):
        file_list = self.fMgr.list_dir(src_dir)
        if len(file_list) > 2:
            file_list = file_list[:-1]
            for f in file_list:
                dst = os.path.seq.join([dst_dir, self.Mgr.dir_split(f)])
                self.fMgr.move_file(f, dst)
        

paramMap = dict()
def ajax_serviceDir_query():
    paramMap = {'level': 5}
    level = paramMap.get('level')
    if not level:
         raise Exception('没有传入目录列表的层次序号')
    sd = ServiceDir()
    tree = sd.get_tree(to_dict=False)
    tree.show()
    data = [(tree.level(i.identifier),i) for i in tree.nodes.values()]
    data = sorted(filter(lambda y: y[0] == int(level), data), key = lambda x: x[0])
    return [{'text': i[1].tag, '_id':i[1].data[0], 'value': i[1].data[1]} for i in data]

def ajax_serviceDir_modify():
    new_val_dict = {'_id': 1, 'name':'属性1', 'type_id': 1, 'value': 100, 'attr_set_id': 1}
    paramMap = {'_id': 'root/1/1/1/1', 'set_value': new_val_dict}
    sd = ServiceDir()
    _id = paramMap.get('_id')
    set_value = paramMap.get('set_value')
    if not _id or not set_value:
        raise Exception('输入参数为空')
    sd.modify_branch(_id, set_value)

def ajax_serviceDir_del():
    paramMap = {'_id': 'root/1/1/1'}
    _id = paramMap.get('_id')
    if not _id:
        raise Exception('输入参数为空')
    sd = ServiceDir()
    sd.del_branch(_id)

def ajax_serviceDir_create():
    paramMap = {'_id': 'root', 'node_name': '新增'}
    _id = paramMap['_id']
    node_name = paramMap['node_name']
    sd = ServiceDir()
    sd.create_branch(_id, node_name)

def ajax_serviceDir_Types():
    mb = MongoBase()
    mb.connectMongo()
    try:
        rs = mb.find(Const.DIM_TYPE['tabName'])
        return rs
    finally:
        mb.close()
    

if __name__ == '__main__':
    sd = ServiceDir()
    sd.connectMongo()
    sd.client.drop_database(DB_INFO['DB_NAME'])
    sd.importTab()
    #pprint(ajax_serviceDir_Types())
