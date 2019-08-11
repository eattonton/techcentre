# -*- coding: utf-8 -*-
import os, sys
sys.path.append('./tcpy')
sys.path.append('../')
import multiprocessing
import json
import pymongo
import threading
from django.http import HttpResponse, HttpResponseBadRequest
import annotation
from base import BaseControl
import recorditem
from collections import defaultdict, OrderedDict

class ProjList(BaseControl):
    def __init__(self):
        BaseControl.__init__(self)
        self.table = self.db.TaskListtb
        self.recordTable = recorditem.RecordItem()

    def html(self, request, fun1=''):
        return BaseControl.html(self, request, fun1)

    # 批量插入
    def insertBath(self, items):
        items2 = []
        for item in items:
            recItems = []
            id2 = item["_id"]
            if "日期工时s" in item:
                recItems = item.pop("日期工时s")
            item2 = self.insert(item)
            item2["_id2"] = id2    #记录原始id用于更新客户端
            items2.append(item2)
            for rItem2 in recItems:
                item3 = {}
                item3["任务id"] = item2["_id"]
                item3["周日期"] = item2.get("周日期","")
                item3["登记人"] = item2.get("登记人","")
                item3["日期"] = list(rItem2.keys())[0]
                item3["工时"] = list(rItem2.values())[0]
                self.recordTable.insert(item3)
        return items2

    def updateOne(self,item):
        sid = item['_id']
        item2 = self.table.find_one({'_id': sid})
        if item2 is not None:
            self.table.update({'_id': sid}, {'$set': item}, multi=False)
            return item2
        return None

    def updateBath(self, items):
        items2 = []
        for item in items:
            recItems = []
            if "日期工时s" in item:
                recItems = item.pop("日期工时s")
            sid = item['_id']
            item2 = self.updateOne(item)
            if item2 is not None:
                items2.append(item2)
                for rItem2 in recItems:
                    obj2=None
                    item3 = {}
                    item3["任务id"] = item2['_id']
                    item3["日期"] = list(rItem2.keys())[0]
                    item3["工时"] = list(rItem2.values())[0]   #传入的值
                    item3["周日期"] = item2.get("周日期","")
                    item3["登记人"] = item2.get("登记人","")
                    self.recordTable.updateByTask(item3)
        return items2

    def get(self, sfilter={}):
        arr1 = []
        items = self.table.find(sfilter).sort("_id", pymongo.ASCENDING)
        for item in items:
            sfilter2 = {"任务id":item["_id"]}
            items2 = self.recordTable.get({"filter":sfilter2})
            for item2 in items2:
                item[item2["日期"]] = item2["工时"]
            arr1.append(item)
        return arr1

    def delete(self,item):
        sid = item.get("_id",-1)
        obj1 = self.table.find_one({'_id': sid})
        if obj1 is not None:
            if self.table.delete_one({'_id': sid}):
                self.recordTable.deleteByTask(sid)
                return obj1
        return None

    def getWithTimeRecord(self, data={}):
        sfilter =   data.get("filter", {})
        filterLookup = {"localField":"_id","from":"TimeItemtb","foreignField":"任务id","as":"times"}
        filterLookup2 = {"localField":"登记人","from":"Usertb","foreignField":"英文名","as":"user"}
        filterMatch = {"times.日期":sfilter["日期"]}
        items = self.table.aggregate([{"$lookup":filterLookup},{"$lookup":filterLookup2},{"$match":filterMatch},{"$sort":{"_id":1,"登记人":1}}])
        #arr0 = [cell for cell in items]
        #print(arr0)
        recArr = self.recordTable.getTimeRecordIds(sfilter)
        print(recArr)
        obj1 = OrderedDict()
        for item1 in items:
            skey1 = item1["工作任务"]+"_"+item1["登记人"]+"_"+item1["工时代码"]+"_"+item1["船号"]
            if skey1 not in obj1:
                obj2 = {}
                obj2["工作任务"] = item1["工作任务"]
                obj2["登记人"] = item1["登记人"]
                obj2["姓名"] = item1["user"][0]["姓名"]
                obj2["工号"] = item1["user"][0]["工号"]
                obj2["工时代码"] = item1["工时代码"]
                obj2["船号"] = item1["船号"]
                obj2["合计工时"] = 0
                obj1[skey1] = obj2
            for item2 in item1["times"]:
                if item2["_id"] in recArr:
                    skey2 = item2["日期"]
                    if skey2 in obj1[skey1]:
                        obj1[skey1][skey2] = obj1[skey1][skey2] + item2["工时"]
                    else:
                        obj1[skey1][skey2] = item2["工时"]
                    obj1[skey1]["合计工时"] = obj1[skey1]["合计工时"] + item2["工时"]
            print(obj1)
        arr1 = list(obj1.values())
        return arr1

if __name__ == '__main__':
    mdb = ProjList()
    res = mdb.getWithTimeRecord({"filter":{"日期":{"$gte":"2019-08-06","$lte":"2019-08-08"}}})
    print(res)
