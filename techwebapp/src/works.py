#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Time       : 2019/9/17 23:34
@Author     : micrometer
@File       : works.py
@Software   : PyCharm
@Email      : 289012724@qq.com
"""

from techwebapp.src.base import BaseControl


class Works(BaseControl):
    def __init__(self, _dbUtil):
        BaseControl.__init__(self, _dbUtil)
        self.table = self.db.dictionary
