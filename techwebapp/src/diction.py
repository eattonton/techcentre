# -*- coding: utf-8 -*-
import os,sys
import json
import codecs
from django.http import HttpResponse, HttpResponseBadRequest

class Diction():
    def __init__(self):
        self.fileName="./SourceWeb/config/config.json"

    def html(self, request, stype=''):
        sdata = request.GET.get('data', '')
        jsonData = {}
        if sdata != '':
            jsonData = json.loads(sdata)
        obj1 = {}
        if stype == 'get':
            obj1 = self.readJson(self.fileName)
        str2 = json.dumps(obj1, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        response =  HttpResponse(str2, content_type="application/json")
        if stype == 'get':
            response["Access-Control-Allow-Origin"] = "*" 
            response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
            response["Access-Control-Max-Age"] = "1000"
            response["Access-Control-Allow-Headers"] = "*"
        return response

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
        sdata = self.read(fNa,fileCode)
        sdata = sdata.replace('\ufeff','').replace('\r\n','')
        objRes = json.loads(sdata)
        objRes["性别"]=["男","女"]
        objRes["结果"]=["合格","不合格"]
        return objRes

if __name__ == '__main__':
    mconfig = Diction()
    print(mconfig.readJson("config/weldstaffconfig.json"))