#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Time       : 2019/8/2 08:51
@Author     : micrometer
@File       : __init__.py.py
@Software   : PyCharm
@Email      : 289012724@qq.com
"""

from techwebapp.src.dbUtil import DbUitl
from techwebapp.src.mgdbwsuser import MgdbUser
from techwebapp.src.dictionary import Dictionary
from techwebapp.src.works import Works

# 获取数据库连接
_DbUtil = DbUitl()
_DbUtil.start()


class Control:
    def __init__(self):
        pass


_parttern = Control()
_parttern.user = MgdbUser(_DbUtil).html
_parttern.dictionary = Dictionary(_DbUtil).html
_parttern.works = Works(_DbUtil).html
