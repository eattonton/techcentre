# -*- coding: utf-8 -*-
import os,sys
import json
import datetime
import twfilehelper
import itemindices

#记录时间的列表
class QuaDailyFormIndices():
    def __init__(self):
        self.proj = 'N688'
        self.dir = './data/N688/idx/'
        self.magor = ''
        self.path = ''
        self.idxObj = None
        self.idxObjs = {}
    
    def loadIndices(self,magor='HB'):
        if magor in self.idxObjs:
            self.idxObj = self.idxObjs[magor]
        else:
            self.idxObj = itemindices.ItemIndices(magor + '.txt')
            self.idxObjs[magor] = self.idxObj

    def getCurrentID(self,magor='HB'):
        self.loadIndices(magor)
        line = self.idxObj.lockNoParam(self.idxObj.askValidLine)
        if len(line) > 0:
            return line[0]
        return -1

    #根据id号取消使用
    def removeUse(self,id,magor='HB'):
        self.loadIndices(magor)
        def cb(pars,col,val):
            if pars[1] == 1:
                return True
            return False
        line = self.idxObj.lockParam(self.idxObj.delOneLine,id)

    #获得报验单编号
    def getDailyFormId(self,magor='HB'):
        id = self.getCurrentID(magor)
        sid = str(id).rjust(3,'0')
        return 'BY-'+self.proj+'-'+magor+'-'+sid

    def removeDailyFormId(self,sid):
        arr1 = sid.split('-')
        self.removeUse(int(arr1[-1]),arr1[-2])
  
    def save(self):
        for item in self.idxObjs:
            self.idxObjs[item].save()
       
if __name__ == '__main__':
    mdb = QuaDailyFormIndices()
    # print(mdb.getCurrentID())
    # mdb.removeUse(10)
    formid = mdb.getDailyFormId()
    mdb.removeDailyFormId(formid)
    mdb.save()
    # print(mdb.getCurrentID())
