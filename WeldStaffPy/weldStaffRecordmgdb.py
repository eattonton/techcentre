# -*- coding: utf-8 -*-
import os, sys
import multiprocessing
import json
import time
import pymongo
import threading
from django.http import HttpResponse, HttpResponseBadRequest

class mgdbWeldStaffRecord():
    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.client.WeldStaffdb
        self.table = self.db.WSExamRecordtb
 
    def getMaxId(self, tb):
        count2 = tb.find({}, {'_id': 1}).count()
        if count2 > 0:
            obj1 = tb.find({}, {'_id': 1}).sort("_id", pymongo.ASCENDING).skip(count2 - 1)
            return int(obj1[0]['_id'])
        else:
            return 0

    def recorddate(self, item):
        item2= {}
        item2["考试批次"] = item[u"考试批次"]
        item2["考试批次2"] = item[u"考试批次2"]
        item2["考试日期"] = item[u"考试日期"]
        item2["考试时间"] = item[u"考试时间"]
        item2["焊接考试"] = [item[u"_id"]]
        item2["船级社"] = item[u"船级社"]
        item3 = self.getBySeq( {u"考试批次2": item2["考试批次2"]})
        if item3 != None:
            if u"焊接考试" in item3:
                self.table.update({'_id': item3["_id"]}, {'$push': {u'焊接考试': item2["焊接考试"][0]}}, multi=False)
            else:
                self.insert(item2)
        else:
            self.insert(item2)
        return item

    def canceldate(self,item):
        query = {'考试批次2': item["考试批次2"]}
        item = self.table.update(query, {'$pull': {"焊接考试":item["_id"]}}, multi=False)
        item1 = self.table.find_one(query)
        if item1 and len(item1["焊接考试"]) == 0:
            self.table.remove(query)
        return item


    def insert(self, item):
        if item.get('_id', 0) == 0:
            item['_id'] = self.getMaxId(self.table) + 1
            self.table.insert_one(item)
        return item

    def update(self, item):
        sid = item['_id']
        tableNow = self.table
        status = item.get(u'status', 1)
        obj1 = tableNow.find_one({'_id': sid})
        if obj1 != None:
            sres = tableNow.update({'_id': sid}, {'$set': item}, multi=False)
            return tableNow.find_one({'_id': sid})
        return obj1

    def remove(self, item):
        sid = item['_id']
        item['status'] = -1
        return self.update(item)

    def clear(self):
        self.table.remove({})

    def get(self, sfilter={}):
        lst1 = []
        items = self.table.find(sfilter).sort(u"_id", pymongo.DESCENDING)
        for item in items:
            lst1.append(item)
        return lst1

    def getBySeq(self, seq):
        item = self.table.find_one(seq)
        if item != None:
            return item
        return None
 
if __name__ == '__main__':
    mdb = mgdbWeldStaffRecord()
    #item={}
    #item["考试批次"]="20180916"
    #mdb.record(item)
    #res = mdb.get({'职务': {'$in':['检验员','项目主管','管理员']}})
    print(mdb.get())
