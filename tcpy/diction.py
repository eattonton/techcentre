# -*- coding: utf-8 -*-
import os,sys
import json
import codecs
from django.http import HttpResponse, HttpResponseBadRequest
from base import BaseControl

class Diction(BaseControl):
    def __init__(self):
        BaseControl.__init__(self)
        self.fileName="./tcpy/config/config.json"

    def html(self, request, fun1=''):
        return BaseControl.html(self, request, fun1)

    def get(self):
        return self.readJson(self.fileName)
 
    def read(self, fNa, fileCode='utf-8'):
        try:  
            with codecs.open(fNa,'r',fileCode) as f:
                return f.read()
        except:
            return ''

    def readList(self, fNa, fileCode='utf-8'):
        try:  
            with codecs.open(fNa,'r',fileCode) as f:
                lines = f.readlines()
                return [line.replace('\ufeff','').replace('\r\n','') for line in lines]
        except:
            return []

    def readJson(self, fNa,fileCode='utf-8'):
        objRes={}
        sdata = self.read(fNa,fileCode)
        sdata = sdata.replace('\ufeff','').replace('\r\n','')
        if sdata:
            objRes = json.loads(sdata)
        objRes["性别"]=["男","女"]
        objRes["结果"]=["合格","不合格"]
        return objRes

if __name__ == '__main__':
    mconfig = Diction()
    print(mconfig.get())