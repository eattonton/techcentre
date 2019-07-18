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

class ProjList(BaseControl):
    def __init__(self):
        BaseControl.__init__(self)
        self.table = self.db.ProjListtb

    def html(self, request, fun1=''):
        return BaseControl.html(self, request, fun1)

#if __name__ == '__main__':
    #mdb = mgdbUser()
    #res = mdb.get({'英文名': 'lezhoutong'})
    #res = mdb.get({'职务': {'$in':['检验员','项目主管','管理员']}})
    #print(res)
