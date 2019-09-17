# -*- coding: utf-8 -*-

import multiprocessing
import json
import os

from techwebapp.src import annotation
from techwebapp.src.result import Result
from utils.logger import Logger


class BaseControl(object):
    """
    简单控制器
    insert:insert(item)
    insertBatch:insert(itmes)
    get:get(query)
    getPager:get(query)
    update:update(item)
    delete:delete(item)
    """

    def __init__(self, _dbUtil):
        self.db = _dbUtil.db
        self.lock = multiprocessing.Lock()
        self.dbUtil = _dbUtil

    def _checkUniqu(self, item):
        """
        检测数据的唯一性
        :param item:
        :return:
        """
        return Result.true("")

    # 操作加锁
    def lockCall(self, cb, *args, **kwargs):
        self.lock.acquire(10)
        try:
            res = cb(*args, **kwargs)
        except Exception as e:
            Logger.error(e)
            return Result.false("操作失败lockcall")
        finally:
            self.lock.release()
        return res

    def nolockCall(self, cb, *args, **kwargs):
        try:
            res = cb(*args, **kwargs)
        except Exception as e:
            Logger.error(e)
            return Result.false("操作失败nolockcall")
        return res

    def getTableId(self, tb):
        """
        获取数据ID号
        :param tb:
        :return:
        """
        count2 = tb.find({}, {'_id': 1}).count()
        if count2 > 0:
            obj1 = tb.find({}, {'_id': 1}).sort("_id", self.dbUtil.get_pro("ASCENDING")).skip(count2 - 1)
            return int(obj1[0]['_id'])
        else:
            return 0

    @annotation.cros
    @annotation.jsonfy
    def html(self, request, stype=''):
        data = {}
        str1 = request.GET.get('data', None) or request.POST.get('data', None)
        if str1:
            data = json.loads(str1)

        call = getattr(self, stype)
        if call is None:
            return Result.false(u"请求方法有误" + stype)
        else:
            return self.nolockCall(call, data)

    def get(self, data):
        """
        获取所有数据
        :param data:
        :return:
        """
        return Result.true([cell for cell in self.table.find(data.get("filter", {}))])

    def getPager(self, data):
        """
        获取分页数据
        :param data: {filter:{},pageNumber:int,pageSize:int,sort}
        :return:
        """
        _filter = data.get("filter", {})
        _pageNumber = data.get("pageNumber", 1)
        _pageSize = data.get("pageSize", 50)
        _sort = []
        if "sort" in data:
            for key, value in data.get('sort').items():
                _sort.append((key, value))

        count = self.table.find(_filter).count()
        if len(_sort) > 0:
            cursor = self.table.find(_filter).limit(_pageSize).skip((_pageNumber - 1) * _pageSize).sort(_sort)
        else:
            cursor = self.table.find(_filter).limit(_pageSize).skip((_pageNumber - 1) * _pageSize)
        data = tuple(cursor)
        return Result.true({"rows": data, "total": count})

    def insert(self, item):
        """
        新增单个实例
        :param item:
        :return:
        """
        item["_id"] = self.getTableId(self.table) + 1
        return self.dbUtil.insert(self.table, item, self._checkUniqu)

    def insertBatch(self, datas):
        """
        批量插入数据
        :param datas:
        :return:
        """
        if isinstance(datas, dict):
            datas = datas.values()
        oks = []

        def run(item):
            result = self.insert(item)
            result.isOk() and oks.append(result.data)

        [run(item) for item in datas]
        return Result.true(oks)

    # 更新实例数据
    def update(self, item):
        """
        更新数据
        :param item:
        :return:
        """
        sid = item['_id']
        obj1 = self.table.find_one({'_id': sid})
        if not obj1:
            return Result("数据已经被删除,请刷新", flag=False)

        result = self.dbUtil.update(self.table, item, self._checkUniqu)
        if result.isOk():
            result = Result.true(self.table.find_one({"_id": item["_id"]}))
        return result

    def delete(self, item):
        """
        删除实例数据
        :param item:
        :return:
        """
        sid = item['_id']
        obj1 = self.table.find_one({'_id': sid})
        if obj1 is not None:
            if self.table.remove({'_id': sid}):
                return Result.true(obj1)
            return Result.false("删除数据失败")
        return Result.true(obj1)

    def saveFile(self, file, dirPath, fileName):
        """
        保存文件
        :param file: 真实文件
        :param dirPath: 保存路径
        :param fileName: 保存后的文件名称
        :return:
        """
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
        path = os.path.join(dirPath, fileName)
        if os.path.exists(path):
            return Result.false("此文件已经存在")
        f = open(path, 'wb')
        [f.write(chunk) for chunk in file.chunks()]
        f.close()
        return Result.true(path)

    def removeFile(self, dirPath, fileName):
        """
        移除文件
        :param dirPath:
        :param fileName:
        :return:
        """
        if os.path.exists(os.path.join(dirPath, fileName)):
            os.remove(os.path.join(dirPath, fileName))

    def removeKey(self, data):
        """
        移除数据表中的字段
        :param data: {"filter":{},"remKeys":{}}
        :return:
        """
        query = data.get("filter", {})
        remKeys = data.get("remKeys", None)
        if not remKeys:
            return Result.false("未获取到需要移除的字段")
        self.table.update(query, remKeys, False, True)
        return Result.true("移除字段成功")
