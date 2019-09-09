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
import projectlist
import datetime

class RecordItem(BaseControl):
    def __init__(self):
        BaseControl.__init__(self)
        self.table = self.db.TimeItemtb
 
    def html(self, request, fun1=''):
        return BaseControl.html(self, request, fun1)
 
    # 插入单个实例数据
    def insert(self, item={}):
        if len(item) == 0:
            return None
        filter1 = {}
        filter1["_id"] = item.get("_id",0)
        obj1 = self.table.find_one(filter1)
        if obj1 is not None:
            self.table.update({'_id': obj1["_id"]}, {'$set': item}, multi=False)
        else:
            max = self.getTableId(self.table)
            item["_id"] = max + 1
            self.table.insert(item)
        return item

    # 批量插入焊工信息,主要用于从模板导入数据
    def insertBath(self, items):
        titems = []
        for item in items:
            item2 = self.insert(item)
            titems.append(item2)
        return titems

    def delete(self,item):
        if item is not None:
            projid = item.get("任务id",0)
            if projid != 0:
                for k in item:
                    if self.verify_date_str_lawyer(k):
                        self.deleteOne(projid,k)
                return item
        return None

    def deleteOne(self, projid,sdate):
        obj1 = self.table.find_one({'任务id': projid,"日期":sdate})
        if obj1 is not None:
            if self.table.delete_one({'_id': obj1["_id"]}):
                return obj1
        return None

    def deleteByTask(self, taskID):
        self.table.delete_many({'任务id': taskID})

    def updateByTask(self,item):
        obj1 = self.table.find_one({'任务id': item.get("任务id",0),"日期":item.get("日期","")})
        if obj1 is not None:
            #如果存在 就更新
            self.table.update({'_id': obj1["_id"]}, {'$set': item}, multi=False)
        else:
            self.insert(item)

    def verify_date_str_lawyer(self,datetime_str):
        try:        
            datetime.datetime.strptime(datetime_str, '%Y-%m-%d')        
            return True    
        except ValueError:        
            return False

    def getSumWeeks(self,items):
        items2 = []
        for item in items:
            item2 = self.getSumWeek(item)
            items2.append(item2)
        return items2

    def getSumWeek(self,sfilter):
        items = self.get({"filter":sfilter})
        value1 = 0
        for item in items:
            value1 = value1 + item.get("工时",0)
        item2 = {}
        item2["合计工时"] = value1
        item2["周日期"] = sfilter.get("周日期","")
        return item2

    def getTaskIds(self,sfilter):
        items = self.table.find(sfilter).distinct("任务id")
        #items = self.table.find(sfilter)
        #return items
        return [cell for cell in items]

    def getTimeRecordIds(self,sfilter):
        items = self.table.find(sfilter).distinct("_id")
        #items = self.table.find(sfilter)
        #return items
        return [cell for cell in items]

if __name__ == '__main__':
    mdb = RecordItem()
    #item ={"2019-07-17":8,"2019-07-18":8,"任务id":2}
    res = mdb.getTimeRecordIds({"日期":{"$gte":"2019-08-07","$lte":"2019-08-08"}})
    #res = mdb.get({'职务': {'$in':['检验员','项目主管','管理员']}})
    print(res)
