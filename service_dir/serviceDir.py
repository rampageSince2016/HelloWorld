from pymongo import MongoClient
from pprint import pprint
from treelib import Tree

import os
import csv

DB_INFO = {
        'MONGO_HOST': 'localhost',
        'MONGO_PORT': 27019,
        'DB_NAME': 'COP'
}

class Const:
    DATA_IN = './importDir'
    DATA_OUT = './exportDir'
    FACT_SERVICE = {'tabName': 'FACT_SERVICE', 'foreignKey': 'service_dir_id'}
    FACT_SCENE = {'tabName': 'FACT_SCENE', 'foreignKey': 'service_id'}
    FACT_ATTR_SET = {'tabName': 'FACT_ATTR_SET', 'foreignKey': 'scene_id'}
    FACT_ATTR = {'tabName': 'FACT_ATTR', 'foreignKey': 'attr_set_id'}
    FACT_SERVICE_DIR = {'tabName': 'FACT_SERVICE_DIR', 'foreignKey': None}
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


class ServiceDir:
    client = None
    db = None

    def connectMongo(self):
        self.client = MongoClient(DB_INFO['MONGO_HOST'], DB_INFO['MONGO_PORT'])
        self.db = self.client[DB_INFO['DB_NAME']]

    def close(self):
        try:
           self.client.close()
        except:
            raise

    def find(self, table, match=None, project=None, nosql=None):
        if match:
            rs = list(self.db[table].find(match, project))
        elif nosql:
            rs = list(self.db[table].aggregate(nosql))
        return rs

    def createIdx(self):
        self.db[Const.FACT_SERVICE['tabName']].ensure_index(Const.FACT_SERVICE['foreignKey'])
        self.db[Const.FACT_SCENE['tabName']].ensure_index(Const.FACT_SCENE['foreignKey'])
        self.db[Const.FACT_ATTR_SET['tabName']].ensure_index(Const.FACT_ATTR_SET['foreignKey'])
        self.db[Const.FACT_ATTR['tabName']].ensure_index(Const.FACT_ATTR['foreignKey'])

        
    def exportTab(self):
        pass
        

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
                            self.db[f].update({
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
        L_SERVICE = {'$lookup':{
            'from': 'FACT_SERVICE',
            'localField': '_id',
            'foreignField': Const.FACT_SERVICE['foreignKey'],
            'as': 'service'
        }}
        U_SERVICE = {'$unwind': {'path': '$service'}}
        L_SCENE = {'$lookup':{
            'from': 'FACT_SCENE',
            'localField': 'service._id',
            'foreignField':Const.FACT_SCENE['foreignKey'],
            'as': 'scene'
        }}
        U_SCENE = {'$unwind': {'path': '$scene'}}
        nosql = [L_SERVICE, U_SERVICE, L_SCENE, U_SCENE]
        return nosql

    def generate_dir_tree(self, treeList):
        t = FlexTree()
        t.create_node('root', 'root', data='root')
        if len(treeList) < 1:
            return 
        for item in treeList:
            treePath = [
                    item.get('name'), 
                    item.get('service', {}).get('name'),
                    item.get('scene', {}).get('name')
            ]
            idPath = [
                    str(item.get('_id')),
                    str(item.get('service', {}).get('_id')),
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
                    t.create_node(node_name, treePathLink, parent=parent_path, data=treeIdPath)
        return t
            

    def get_tree(self,to_dict=True):
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


    def del_branch(self, tree_index):
        self.connectMongo()
        try:
            tree = self.get_tree(to_dict=False)
            nodes = set(list(tree.nodes.values()))
            leaves = set(tree.leaves())
            nodeList = list(nodes)
            node_leaf_set = nodes | leaves
            to_be_del = filter(lambda x: x.data.startswith(tree_index), node_leaf_set)
            for item in to_be_del:
                node_values = [int(i) for i in item.data.split(os.path.sep) if i != 'root' ]
                key_values = tuple(zip([y['foreignKey'] for y in Const.SEQ], node_values))
                if len(key_values) < 1:
                    raise Exception('传入的tree_index解析出错')
                last_one = key_values[-1]
                match = {last_one[0]: last_one[1]}
                table = list(filter(lambda z: z['foreignKey'] == last_one[0], Const.SEQ))[0]['tabName']
                self.db[table].remove(match)
        finally:
            self.close()


    def create_branch(self, parent_id, node_name):
        self.connectMongo()
        try:
            ids = [int(i) for i in parent_id.split(os.path.sep) if i != 'root']
            key_values = tuple(zip([y['foreignKey'] for y in Const.sep], ids))
            last_one = key_values[-1]
            match = {last_one[0]: last_one[1]}
            if len(key_values) == len(Const.SEQ):
                raise Exception('叶子上加不了节点')
            table = Const.SEQ[len(key_values)]['tabName']
            
        finally:
            self.close()
                
