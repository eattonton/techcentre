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
import projectlist
import datetime

class RecordItem(BaseControl):
    def __init__(self):
        BaseControl.__init__(self)
        self.table = self.db.RecordItemtb
        self.projlisttabel = projectlist.ProjList()

    def html(self, request, fun1=''):
        return BaseControl.html(self, request, fun1)

    def get(self, sfilter={}):
        arr1 = []
        items = self.table.find(sfilter).sort("_id", pymongo.ASCENDING)
        projID={}
        i=0
        for item in items:
            arr1.append(item)
            sidx =item["任务id"]
            if sidx in projID:
                projID[sidx].append(i)
            else:
                projID[sidx] = [i]
            i=i+1
        arr2=[]
        for k in projID:
            newObj={}
            projItem = self.projlisttabel.get({"filter":{"_id":k}})
            if len(projItem) > 0:
                newObj["工时代码"]=projItem[0]["工时代码"]
                newObj["船号"]=projItem[0]["船号"]
                newObj["工作任务"]=projItem[0]["工作任务"]
                newObj["任务id"]=projItem[0]["_id"]
                newObj["_id"] = newObj["任务id"]
                arr3 = projID[k]
                for idx in arr3:
                    newObj[arr1[idx]["日期"]]=arr1[idx]["工时"]
                arr2.append(newObj)
        return arr2

    # 插入单个实例数据
    def insert(self, item={}):
        if len(item) == 0:
            return None
        filter1 = {}
        filter1["任务id"] = item.get("任务id",0)
        filter1["日期"] = item.get("日期","1970-1-1")
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

    def verify_date_str_lawyer(self,datetime_str):
        try:        
            datetime.datetime.strptime(datetime_str, '%Y-%m-%d')        
            return True    
        except ValueError:        
            return False

if __name__ == '__main__':
    mdb = RecordItem()
    #item ={"2019-07-17":8,"2019-07-18":8,"任务id":2}
    res = mdb.get()
    #res = mdb.get({'职务': {'$in':['检验员','项目主管','管理员']}})
    print(res)
