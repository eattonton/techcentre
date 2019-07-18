# -*- coding: utf-8 -*-
import os, sys
sys.path.append('./tcpy')
import multiprocessing
import json
import pymongo
import threading
from django.http import HttpResponse, HttpResponseBadRequest
import annotation
from base import BaseControl

class User(BaseControl):
    def __init__(self):
        BaseControl.__init__(self)
        self.table = self.db.Usertb
        self.userlst = []

    def html(self, request, fun1=''):
        return BaseControl.html(self, request, fun1)

    def getMaxId(self, tableNow):
        count2 = tableNow.find({}, {'_id': 1}).count()
        if count2 > 0:
            obj1 = tableNow.find({}, {'_id': 1}).sort("_id", pymongo.ASCENDING).skip(count2 - 1)
            return int(obj1[0]['_id'])
        else:
            return 0
 
    def get(self, sfilter={}):
        self.userlst = []
        # items = self.table.find({}).sort("名",pymongo.ASCENDING)
        items = self.table.find(sfilter).sort("英文名", pymongo.ASCENDING)
        for item in items:
            self.userlst.append(item)
        return self.userlst

    def update(self, item):
        id1 = item.get('_id', -1)
        self.table.update({'_id': id1}, {'$set': item}, multi=False)
        item2 = self.table.find_one({'_id': id1})
        return item2

    def clear(self):
        self.table.remove({})

    def find(self, item):
        name = item.get('name', '')
        password = item.get('pass', '')
        if name == '' or password == '':
            return 0
        return self.findName(name, password)

    def findName(self, name, password=''):
        str1 = self.get()
        for obj2 in self.userlst:
            if (name == obj2.get(u'工号', '')) or (name == obj2.get(u'名', '')) or (
                name.lower() == obj2.get(u'英文名', '').lower()):
                if password == obj2.get(u'密码', '123456'):
                    if u'密码' not in obj2:
                        obj2[u'密码'] = '123456'
                    return obj2
                else:
                    return 1
        return 0

    def findName2(self, name):
        str1 = self.get()
        for obj2 in self.userlst:
            if (name == obj2.get(u'工号', '')) or (name == obj2.get(u'名', '')) or (
                name.lower() == obj2.get(u'英文名', '').lower()):
                return obj2
        return 0

        # 程序直接的数据调用

    def getByName(self, name):
        obj1 = {"英文名": {"$regex": '^' + name + '$', '$options': 'i'}}
        item = self.table.find_one(obj1)
        if item != None:
            return item
        return None

    def getByName2(self, name):
        obj1 = {"名": name}
        item = self.table.find_one(obj1)
        if item != None:
            return item
        return None

    def getByWorkNo(self, name):
        obj1 = {"工号": name}
        item = self.table.find_one(obj1)
        if item != None:
            return item
        return None


#if __name__ == '__main__':
    #mdb = mgdbUser()
    #res = mdb.get({'英文名': 'lezhoutong'})
    #res = mdb.get({'职务': {'$in':['检验员','项目主管','管理员']}})
    #print(res)
