#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Time       : 2019/8/2 09:04
@Author     : micrometer
@File       : dictionary.py
@Software   : PyCharm
@Email      : 289012724@qq.com
"""
from techwebapp.src.base import BaseControl


class Dictionary(BaseControl):
    """
    用于保存数据下拉选择数据信息
    """

    def __init__(self, _dbUtil):
        BaseControl.__init__(self, _dbUtil)
        self.table = self.db.dictionary

