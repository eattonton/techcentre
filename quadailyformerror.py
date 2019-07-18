# -*- coding: utf-8 -*-
import os,sys
import json
import datetime
import time
import json
import pymongo
import ship

class QuaDailyFormError():
    def __init__(self):
        self.lineDic = ["HB","HE","M","P","E","C","O","IN"]
        self.workshop=["分段工区","搭载工区","机装工区","电装工区","舾装工区","涂装工区","制造工区"]
        self.majorDic = {"HB":"Hull","HE":"Hull","M":"Machinery","O":"Outfitting","E":"Electric","P":"Piping","C":"Coating","IN":"Income"}
        
    def fun_checkobj(self,obj1,shipno=''):
        errlst = []
        bres1,str1 = self.fun_checkmajor(obj1.get(u'报验专业',''))
        if bres1 == False:
            errlst.append(str1)
        bres2,str2 = self.fun_checkshipno(obj1.get(u'船号',''))
        if bres2 == False:
            errlst.append(str2)
        if obj1[u'质检员'] == '':
            errlst.append(obj1[u'报验编号'] + '质检员不存在')
        if shipno != '' and obj1.get(u'船号','') != shipno:
            errlst.append(obj1[u'报验编号'] + '船号与当前船号不一致')
        bres3,str3 = self.fun_checkworkshop(obj1.get(u'报验工区',''))
        if bres3 == False:
            errlst.append(str3)
        return errlst
    
    def fun_checkworkshop(self,strIn):
        if strIn in self.workshop:
            return True,""
        return False,"不存在"+strIn+"工区"

    def fun_checkmajor(self,strIn):
        if strIn in self.lineDic:
            return True,""
        return False,"不存在"+strIn+"专业"

    def fun_checkshipno(self,strIn):
        shipdb = ship.Ship()
        lstShipNo = shipdb.get()
        for mship in lstShipNo:
            shipno = mship[u'船号']
            if strIn == shipno:
                return True,""
        return False,"不存在"+strIn+"船号"

if __name__ == '__main__':
    mdb = QuaDailyFormError()
    obj1 = {u'报验专业':'HE1',u'船号':'N688'}
    errlst = mdb.fun_checkobj(obj1)
    print(errlst)
    

    

