# -*- coding: utf-8 -*-
import os,sys
import json
import datetime
import twfilehelper

#记录时间的列表
class QuaDailyFormDate():
    def __init__(self):
        self.sdate = datetime.datetime.now().strftime('%Y-%m-%d')
        self.proj = ''
        self.dir = './data/N688/date/'
        self.path = self.dir + self.sdate + '.txt'

    def add(self,files):
        if len(files) > 0:
            bres = False
            if os.path.exists(self.path):
                bres = twfilehelper.appendList(self.path, files)
            else:
                bres = twfilehelper.writeList(self.path, files)
            return bres
        return False

    def insert(self,file):
        if file != '':
            lst1 = twfilehelper.readList(self.path)
            if file not in lst1:
                return twfilehelper.append(self.path, file)
        return True

    def getJson(self,sdt,itype=0):
        path = self.dir + sdt + '.txt'
        files = twfilehelper.readList(path)
        lst = []
        files.sort()
        for item in files:
            path1 = './data/N688/db/'+item
            #申请单对象
            path1 = path1
            if os.path.exists(path1):
                print(path1)
            item2 = twfilehelper.readJson(path1)
            if itype == 100:
                if item2.get(u"状态",0) != -1:
                    lst.append(item2)
            else:
                if item2.get(u"状态",0) == itype:
                    lst.append(item2)
        return lst

if __name__ == '__main__':
    mdb = QuaDailyFormDate()
    lst = mdb.getJson('2017-11-13')
