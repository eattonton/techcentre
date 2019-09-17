#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Time       : 2019/8/6 14:14
@Author     : micrometer
@File       : result.py.py
@Software   : PyCharm
@Email      : 289012724@qq.com
"""
import json


class Result:
    """
    结果集合
    """

    def __init__(self, data="", state=True):
        self.data = data
        self.state = state

    def isOk(self):
        return self.state

    def get(self):
        return self.data, self.state

    @classmethod
    def true(cls, data):
        return Result(data, True)

    @classmethod
    def false(cls, data):
        return Result(data, False)

    def toJson(self):
        return json.dumps({"state": self.state, "data": self.data}, sort_keys=True, ensure_ascii=False,
                          separators=(',', ':'))
