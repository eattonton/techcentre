# -*- coding: utf-8 -*-
import os,sys
import multiprocessing  
import json
import pymongo
from pymongo import MongoClient
import threading

class mgdbItemIndices():
    def __init__(self,coll1):
        self.table = coll1 
        self.lock = multiprocessing.Lock()
        self.dict_id = {}

    def lockNoParam(self,cb):
        res = None
        self.lock.acquire(10)  
        try: 
            res = cb()
        finally:  
            self.lock.release()
        return res

    def lockParam(self,cb,*arg):
        res = None
        self.lock.acquire(10)  
        try: 
            res = cb(*arg)
        finally:  
            self.lock.release()
        return res

     #创建集合
    def __inseritem(self,start=0):
        lst1 = []
        for i in range(10):
            obj1 = {'_id':start + i,'状态':0}
            lst1.append(obj1)
        res1 = self.table.insert_many(lst1)

    def __addrows(self):
        count = self.table.find({'状态':0}).count()
        if count == 0:
            self.__inseritem()
        elif count <= 5:
            count2 =  self.table.find().count()
            obj1 = self.table.find().skip(count2 - 1)
            self.__inseritem(obj1[0]['_id']+1)

    def askValidLine(self):
        self.__addrows()
        sres = self.table.update({'状态':0},{'$set':{'状态':1}},multi=False)
        if sres['ok'] == 1:
            obj1 = self.table.find({'状态':1}).sort([{'_id',-1}]).limit(1)
            return obj1[0]
        else:
            return None

if __name__ == '__main__':
    #连接mongodb数据库
    client = MongoClient('127.0.0.1',27017 )
    #指定数据库名称
    db = client.itemindices
    
    idxdb = mgdbItemIndices(db.index1)

    def func1():
        obj1 = idxdb.lockNoParam(idxdb.askValidLine)
        print(obj1)

    threads = []
    for i in range(2):
        t1 = threading.Thread(target=func1)
        threads.append(t1)
    
    for t in threads:
        t.start()

    