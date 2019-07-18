# -*- coding: utf-8 -*-

import multiprocessing
import json
import pymongo
import annotation
import os
from utils.logger import Logger

#返回的结果集合
def Result(data, flag=True):
    return data, flag


class BaseControl(object):
    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.client.WeldStaffdb
        self.lock = multiprocessing.Lock()

    # 操作加锁
    def lockCall(self, cb, *args, **kwargs):
        res = None
        self.lock.acquire(10)
        try:
            res = cb(*args, **kwargs)
        except Exception as e:
            Logger.error(e)
            res = "操作失败",False
        finally:
            self.lock.release()
        return res

    # 获取数据表的ID
    def getTableId(self, tb):
        count2 = tb.find({}, {'_id': 1}).count()
        if count2 > 0:
            obj1 = tb.find({}, {'_id': 1}).sort("_id", pymongo.ASCENDING).skip(count2 - 1)
            return int(obj1[0]['_id'])
        else:
            return 0

    # 操作分发
    @annotation.cros
    @annotation.jsonfy
    def html(self, request, stype=''):
        data = {}
        str1 = request.GET.get('data', None) or request.POST.get('data', None)
        if str1:
            data = json.loads(str1)

        call = getattr(self, stype)
        if call is None:
            return Result(u"请求方法有误" + stype, False)
        else:
            return self.lockCall(call, data)

    # 获取数据
    def get(self, data):
        return Result([cell for cell in self.table.find(data.get("filter", {}))])

    # 插入单个实例数据
    def insert(self, item):
        max = self.getTableId(self.table)
        item["_id"] = max + 1
        self.table.insert(item)
        return Result(item)

    # 批量插入实例数据
    def insertBatch(self, datas):
        max = self.getTableId(self.table)
        if isinstance(datas, dict):
            datas = datas.values()

        for index, cell in enumerate(datas):
            cell["_id"] = max + index + 1

        self.table.insert(datas)
        return Result(datas)

    # 更新实例数据
    def update(self, item):
        sid = item['_id']
        obj1 = self.table.find_one({'_id': sid})
        if obj1 is not None:
            self.table.update({'_id': sid}, {'$set': item}, multi=False)
            return Result(self.table.find_one({'_id': sid}))
        return Result(obj1)

    # 删除实例数据
    def delete(self, item):
        sid = item['_id']
        obj1 = self.table.find_one({'_id': sid})
        if obj1 is not None:
            if self.table.delete_one({'_id': sid}):
                return Result(obj1)
            return Result("删除数据失败", False)
        return Result(obj1)

    def saveFile(self,file,dirPath,fileName):
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
        path = os.path.join(dirPath,fileName)
        if os.path.exists(path):
            return False,"此文件已经存在"

        f = open(path, 'wb')
        [f.write(chunk) for chunk in file.chunks()]
        f.close()
        return True,path

    def removeFile(self,dirPath,fileName):
        if os.path.exists(os.path.join(dirPath,fileName)):
            os.remove(os.path.join(dirPath,fileName))

    def removeKey(self,data):
        query = data.get("filter",{})
        remKeys= data.get("remKeys",None)
        if not remKeys:
            return "未获取到需要移除的字段",False
        return self.table.update(query,remKeys,False,True)