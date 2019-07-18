# -*- coding: utf-8 -*-
import os, sys
import multiprocessing
import json
import pymongo
import threading
from django.http import HttpResponse, HttpResponseBadRequest


class WeldStaffUser():
    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.client.WeldStaffdb
        self.table = self.db.WSExamUsertb
        self.userlst = []

    def html(self, request, stype=''):
        sdata = request.GET.get('data', '')
        jsonData = {}
        if sdata != '':
            jsonData = json.loads(sdata)
        obj1 = {}
        if stype == 'insert':
            obj1 = self.insert(jsonData)
        elif stype == 'get':
            sfilter = request.GET.get('filter', '')
            if sfilter != '':
                obj1 = self.get(json.loads(sfilter))
            else:
                obj1 = self.get()
        elif stype == 'del':
            obj1 = self.remove(jsonData)
        elif stype == 'update':
            obj1 = self.update(jsonData)
        elif stype == 'find':
            obj1 = self.find(jsonData)

        str2 = json.dumps(obj1, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        response = HttpResponse(str2, content_type="application/json")
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

    def insertUser(self, item):
        item2 = self.getByIDCard(item[u"身份证"])
        if item2 != None:
            if u"焊接考试" in item2:
                self.table.update({'_id': item2["_id"]}, {'$push': {u'焊接考试': item[u"焊接考试"][0]}}, multi=False)
            else:
                self.insert(item)
        else:
            self.insert(item)
        return item

    def insert(self, item):
        if item.get('_id', 0) == 0:
            item['_id'] = self.getMaxId(self.table) + 1
            self.table.insert_one(item)
        return item

    def get(self, sfilter={}):
        self.userlst = []
        # items = self.table.find({}).sort("名",pymongo.ASCENDING)
        items = self.table.find(sfilter).sort(u"英文名", pymongo.ASCENDING)
        for item in items:
            self.userlst.append(item)
        return self.userlst

    def remove(self, item):
        self.table.remove({'_id': item.get('_id', -1)})
        item['_id'] = -1
        return item

    def removeWeldTest(self,item):
        item = self.table.update({'身份证': item["身份证"]}, {'$pull': {"焊接考试":item["_id"]}}, multi=False)
        return item

    def update(self, item):
        id1 = item.get('_id', -1)
        self.table.update({'_id': id1}, {'$set': item}, multi=False)
        return item

    def clear(self):
        self.table.remove({})

    def find(self, item):
        name = item.get('name', '')
        password = item.get('pass', '')
        if name == '' or password == '':
            return 0
        return self.findName(name, password)

    def getByIDCard(self, soid):
        obj1 = {u"身份证": soid}
        item = self.table.find_one(obj1)
        if item != None:
            return item
        return None

    def getByName(self, name):
        obj1 = {u"英文名": {"$regex": '^' + name + '$', '$options': 'i'}}
        item = self.table.find_one(obj1)
        if item != None:
            return item
        return None

    def getByName2(self, name):
        obj1 = {u"名": name}
        item = self.table.find_one(obj1)
        if item != None:
            return item
        return None

    def getByWorkNo(self, name):
        obj1 = {u"工号": name}
        item = self.table.find_one(obj1)
        if item != None:
            return item
        return None


if __name__ == '__main__':
    mdb = WeldStaffUser()
    useritem = {}
    useritem[u"姓名"] = "ZLE"
    useritem[u"身份证号码"] = "2222"
    useritem[u"性别"] = "男"
    useritem[u"电话"] = "1111"
    useritem[u"地址"] = "地址1"
    # mdb.insert(useritem)
    useritem2 = mdb.getByIDCard("412725198908258299")
    if u"焊接考试" in useritem2:
        useritem2[u"焊接考试"].append(2)
    else:
        useritem2[u"焊接考试"] = [1]
    # res = mdb.get({'英文名': 'lezhoutong'})
    # res = mdb.get({'职务': {'$in':['检验员','项目主管','管理员']}})
    print(useritem2)
