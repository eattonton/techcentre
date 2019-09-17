#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Time       : 2019/8/2 08:56
@Author     : micrometer
@File       : dbUtil.py.py
@Software   : PyCharm
@Email      : 289012724@qq.com
"""
import pymongo
import multiprocessing
from techwebapp.src.result import Result


class DbUitl:
    """
    数据库操作安全
    """

    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 27017
        self.lock = multiprocessing.Lock()

    def lockCall(self, cb, *args, **kwargs):
        """
        对数据库操作进行加锁
        :param cb: 操作
        :param args: 参数
        :param kwargs: 配置参数
        :return:
        """
        self.lock.acquire(10)
        try:
            res = cb(*args, **kwargs)
        except Exception as e:
            return Result.false("操作失败lockcall")
        finally:
            self.lock.release()
        return res

    def nolockCall(self, cb, *args, **kwargs):
        """
        对操作不加锁
        :param cb:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            return cb(*args, **kwargs)
        except Exception as e:
            print(e)
            return "操作失败nolockcall", False

    def start(self, host=None, port=None):
        """
        启动数据库连接
        :param host:
        :param port:
        :return:
        """
        _host = host or self.host
        _port = port or self.port
        self.client = pymongo.MongoClient(_host, _port)
        self.db = self.client.SourceWeb

    def insert(self, table, item, uniqueCall):
        """
        插入数据信息
        :param table:
        :param item:
        :param uniqueCall:
        :return:
        """

        def run():
            result = uniqueCall(item)
            if result.isOk():
                table.insert(item)
                return Result.true(item)
            return result

        return self.lockCall(run)

    def update(self, table, item, uniqueCall):
        """
        更新数据信息
        :param table:
        :param item:
        :param uniqueCall:
        :return:
        """

        def run():
            result = uniqueCall(item)
            if result.isOk():
                table.update({'_id': item['_id']}, {'$set': item}, multi=False)
                return Result.true(item)
            else:
                return result

        return self.lockCall(run)

    def get_pro(self, string):
        return getattr(pymongo, string)
