# -*- coding: utf-8 -*-
import os, sys
import multiprocessing
import json
import pymongo
import threading
from django.http import HttpResponse, HttpResponseBadRequest

#返回的结果集合
def Result(data, flag=True):
    obj1={}
    obj1["data"] = data
    obj1["state"] = flag
    return obj1

class mgdbWSUser():
    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.client.WeldStaffdb
        self.table = self.db.usertb
        self.userlst = []

    def html(self, request, stype=''):
        data = {}
        str1 = request.GET.get('data', None) or request.POST.get('data', None)
        if str1:
            data = json.loads(str1)
        call = getattr(self, stype)
        obj1 = {}
        if call is None:
            return Result(u"请求方法有误" + stype, False)
        else:
            obj1 = Result(call(data))
        str2 = json.dumps(obj1, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        response =  HttpResponse(str2, content_type="application/json")
        if stype == 'get':
            response["Access-Control-Allow-Origin"] = "*" 
            response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
            response["Access-Control-Max-Age"] = "1000"
            response["Access-Control-Allow-Headers"] = "*"
        return response

    def getMaxId(self, tableNow):
        count2 = tableNow.find({}, {'_id': 1}).count()
        if count2 > 0:
            obj1 = tableNow.find({}, {'_id': 1}).sort("_id", pymongo.ASCENDING).skip(count2 - 1)
            return int(obj1[0]['_id'])
        else:
            return 0

    def insert(self, item):
        if item.get('_id', 0) == 0:
            item['_id'] = self.getMaxId(self.table) + 1
            self.table.insert_one(item)
        return item

    def get(self, sfilter={}):
        self.userlst = []
        # items = self.table.find({}).sort("名",pymongo.ASCENDING)
        items = self.table.find(sfilter).sort("英文名", pymongo.ASCENDING)
        for item in items:
            self.userlst.append(item)
        return self.userlst

    def remove(self, item):
        self.table.remove({'_id': item.get('_id', -1)})
        item['_id'] = -1
        return item

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


if __name__ == '__main__':
    mdb = mgdbUser()
    #res = mdb.get({'英文名': 'lezhoutong'})
    res = mdb.get({'职务': {'$in':['检验员','项目主管','管理员']}})
    print(res)
