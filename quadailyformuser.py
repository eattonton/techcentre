# -*- coding: utf-8 -*-
import os,sys
import json
import datetime
import twfilehelper

#记录用户的列表
class QuaDailyFormUser():
    def __init__(self):
        self.sdate = datetime.datetime.now().strftime('%Y-%m-%d')
        self.proj = ''
        self.user = '17661'
        self.dir = './data/N688/user/'
        self.path = self.dir + self.user + '.txt'

    def addExist(self,str_old,str_new):
        item_old = json.loads(str_old)
        item_new = json.loads(str_new)
        key1 = next(iter(item_new))
        if key1 in item_old:
            item_old[key1].extend(item_new[key1])
        else:
            item_old[key1] = item_new[key1]
        return json.dumps(item_old,ensure_ascii=False,sort_keys=True)

    def add(self,files):
        if len(files) > 0:
            bres = False
            item = {self.sdate:files}
            if os.path.exists(self.path):
                sitem = json.dumps(item,sort_keys=True)
                bres = twfilehelper.readandWrite(self.path, self.addExist, sitem)
            else:
                bres = twfilehelper.writeDict(self.path, item)
            return bres
        return False

    def insert(self,file):
        if file != '':
            bres = False
            files = []
            files.append(file)
            item = {self.sdate:files}
            if os.path.exists(self.path):
                sitem = json.dumps(item,sort_keys=True)
                bres = twfilehelper.readandWrite(self.path, self.addExist, sitem)
            else:
                bres = twfilehelper.writeDict(self.path, item)
            return bres
        return False

    def getJson(self,sdt,itype=0):
        userdb = twfilehelper.readJson(self.path)
        lst = []
        if sdt in userdb:
            for item in userdb[sdt]:
                path1 = './data/N688/db/'+item
                #申请单对象
                item2 = twfilehelper.readJson(path1)
                if itype == 100:
                    if item2.get(u"状态",0) != -1:
                        lst.append(item2)
                else:
                    if item2.get(u"状态",0) == itype:
                        lst.append(item2)
        return lst

if __name__ == "__main__":
    mdb = QuaDailyFormUser()
    lst = mdb.getJson('2017-11-13')
    print(lst)