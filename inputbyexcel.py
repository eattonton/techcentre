# -*- coding: utf-8 -*-
import os,sys
import json
import datetime
import time
import multiprocessing  
import json
import pymongo
import threading
import quadailyformexcel
import quadailyformcomment
import quadailyformline
import quadailyformerror
import ship
from copy import deepcopy
from django.http import HttpResponse,HttpResponseBadRequest

class QuaDailyFormInput():
    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1',27017 )
        self.majorDic = {"HB":"Hull","HE":"Hull","M":"Machinery","O":"Outfitting","E":"Electric","P":"Piping","C":"Coating"}
        self.items = []
        self.db_dict = {}
        self.mship = ship.Ship()
        self.dferror = quadailyformerror.QuaDailyFormError()
        self.myComment = quadailyformcomment.QuaDailyFormComment()
 
    def getDB(self,shipno):
        if shipno not in self.db_dict:
            self.db_dict[shipno] = []
            self.db_dict[shipno].append(self.client[shipno].quatb)
            self.db_dict[shipno].append(self.client[shipno].commenttb)
        return self.db_dict[shipno][0],self.db_dict[shipno][1]

    #对象添加时间戳
    def timeMark(self,item):
        if u'报验日期' in item:
            if item.get(u'报验日期','') != '':
                #对日期进行修正
                item[u'报验日期'] = quadailyformline.fun_date(item[u'报验日期'])
                item[u'报验日期2'] = time.mktime(time.strptime(item[u'报验日期'], "%Y-%m-%d"))+28800
        return item

    def timeByMark(self,timestamp):
        return time.strftime("%Y-%m-%d",time.localtime(timestamp-28800))

    #存储报验单
    def insert(self,item):
        shipno = item[u'船号']
        tableNow,tableNow2 = self.getDB(shipno)
        item['_id'] = self.getMaxId(tableNow)+1
        self.timeMark(item)
        res1 = tableNow.insert_one(item)
        return item

    #存储意见
    def insertComm(self,item,dformId):
        shipno = item[u'船号']
        tableNow,tableNow2 = self.getDB(shipno)
        item['_id'] = self.getMaxId(tableNow2)+1
        res1 = tableNow2.insert_one(item)
        return item

    #根据意见更新报验单指向 和 意见指向
    def updateDFormAndComm(self,item,item2):
        shipno = item[u'船号']
        tableNow,tableNow2 = self.getDB(shipno)
        if item2[u'意见分类'] == u'船东':
            sres = tableNow.update({'_id':item['_id']}, {'$addToSet': {u'船东意见':item2['_id']}},multi=False)
        if item2[u'意见分类'] == u'船检':
            sres = tableNow.update({'_id':item['_id']}, {'$addToSet': {u'船检意见':item2['_id']}},multi=False)
        #更新意见对象
        sres2 = tableNow2.update({'_id':item2['_id']}, {'$addToSet': {u'报验单':item['_id']}},multi=False)
        if u'报验单1' not in item2:
            tableNow2.update({'_id':item2['_id']}, {'$set': {u'报验单1':item['_id']}},multi=False)

    def getShipAtt01(self,shipno):
        item = self.mship.getshipbyno(shipno)
        if item.get(u'复检连号','') == '*':
            return True
        return False
 
    def getMaxId(self,tableNow):
        count2 =  tableNow.find({},{'_id':1}).count()
        if count2 > 0:
            obj1 = tableNow.find({},{'_id':1}).sort("_id",pymongo.ASCENDING).skip(count2 - 1)
            return int(obj1[0]['_id'])
        else:
            return 0

    def getMaxOrder(self,tableNow,major):
        count2 =  tableNow.find({u'报验专业':major},{u"序号":1}).count()
        if count2 > 0:
            obj1 = tableNow.find({u'报验专业':major},{u"序号":1}).sort(u"序号",pymongo.ASCENDING).skip(count2 - 1)
            return int(obj1[0][u"序号"])
        else:
            return 0

    def getMaxOrder2(self,tableNow,order):
        count2 =  tableNow.find({u'报验编号':order},{u"序号":1}).count()
        if count2 > 0:
            obj1 = tableNow.find({u'报验编号':order},{u"序号":1}).sort(u"序号",pymongo.ASCENDING).skip(count2 - 1)
            return int(obj1[0][u"序号"])
        else:
            return 0

    #获取意见状态
    def getCommStatusCode(self,item,val1):
        if val1 == 'A' or val1 == 'B':
            item[u'意见状态'] =  21
        elif val1 == 'C' or val1 == 'D':
            item[u'意见状态'] = 1
        elif val1 == 'E' or val1 == 'F' or val1 == 'G' or val1 == 'H':
            item[u'意见状态'] = 11

    #获得报验意见对象
    def getdailyformcommobj(self,line,uuser=''):
        item = {}
        arr1 = line[2].split('-')
        item[u"船号"] = arr1[1]
        tableNow,tableNow2 = self.getDB(item[u"船号"])
        item[u"报验编号"] = line[2]
        item[u"序号"] = self.getMaxOrder2(tableNow2,item[u"报验编号"]) + 1
        item[u"意见编号"] = item[u"报验编号"] + '-' + str(item[u'序号'])
        item[u"登记人"] = uuser
        val1 = 'C'  #报验结论
        if line[7] != '':
            item[u"意见内容"] = line[7]
            item[u"意见分类"] = u'船东'
            val1 = line[5]
        if line[8] != '':
            item[u"意见内容"] = line[8]
            item[u"意见分类"] = u'船检'
            val1 = line[6]
        item[u"关闭日期"] = ''
        if line[9] != '':
            item[u"关闭日期"] = quadailyformline.fun_date(line[9])
            item[u"关闭时间"] = ''
        item[u"责任工区"] = quadailyformline.fun_CheckDepartment2(line[11])
        #意见状态
        self.getCommStatusCode(item,val1)
        if item[u"关闭日期"] != "":
            item[u"意见状态"] = 3
        item[u'报验单'] = []
        item['date1'] = time.strftime("%Y-%m-%d", time.localtime())
        item['date2'] = time.strftime("%H:%M:%S", time.localtime())
        return item

    #获取状态
    def getStatusCode(self,item,val1):
        if val1 == 'A' or val1 == 'B':
            item[u'状态'] =  item[u'状态'] if item[u'状态'] > 3 else 3
        elif val1 == 'C' or val1 == 'D':
            item[u'状态'] = item[u'状态'] if item[u'状态'] > 4 else 4
        elif val1 == 'E' or val1 == 'F' or val1 == 'G' or val1 == 'H':
            item[u'状态'] = item[u'状态'] if item[u'状态'] > 3 else 3

    #获得相关联的号
    def getPreNextId(self,item,note1=''):
        tableNow,tableNow2 = self.getDB(item[u"船号"])
        sid = item[u"报验编号"]
        if note1 != '' and note1.startswith('BY-'+item[u"船号"]+'-'):
            sid = note1
        count2 =  tableNow.find({'_id':{'$lt':item['_id']},u'报验编号':sid},{u"_id":1}).count()
        if count2 > 0:
            items2 = tableNow.find({'_id':{'$lt':item['_id']},u'报验编号':sid},{u"_id":1}).sort(u"_id",pymongo.ASCENDING).skip(count2 - 1)
            if items2 != None:
                item2 = items2[0]
                tableNow.update({'_id':item2['_id']}, {'$set': {u'nextid':item['_id']}},multi=False)
                tableNow.update({'_id':item['_id']}, {'$set': {u'preid':item2['_id']}},multi=False)
                return
        count3 =  tableNow.find({'_id':{'$lt':item['_id']},u'报验项目':item[u"报验项目"]},{u"_id":1}).count()
        if count3 > 0:
            items2 = tableNow.find({'_id':{'$lt':item['_id']},u'报验项目':item[u"报验项目"]},{u"_id":1}).sort(u"_id",pymongo.ASCENDING).skip(count3 - 1)
            if items2 != None:
                item2 = items2[0]
                tableNow.update({'_id':item2['_id']}, {'$set': {u'nextid':item['_id']}},multi=False)
                tableNow.update({'_id':item['_id']}, {'$set': {u'preid':item2['_id']}},multi=False)
                return

    #创建报验单对象
    def getdailyformobj(self,line,uuser=''):
        item = {}
        arr1 = line[2].split('-')
        item[u"船号"] = arr1[1]
        item[u"报验编号"] =line[2]
        item[u"序号"] = int(arr1[3])
        item[u"报验日期"] = quadailyformline.fun_date(line[1])
        item[u"报验时间"] = ''
        item[u"报验专业"] = arr1[2]
        item[u"报验地点"] = ''
        item[u"报验项目"] = line[4]
        item[u"报验工区"] = quadailyformline.fun_CheckDepartment(line[10])
        item[u"施工班组"] = ''
        item[u"工区申请人"] = ''
        item[u"船东结论"] = line[5]
        item[u"状态"] = 0
        if item[u"船东结论"] != '':
            item[u"船东"] = '*'
            self.getStatusCode(item,item[u"船东结论"])
            item[u"船东意见"] = []
        item[u"船检结论"] = line[6]
        if item[u"船检结论"] != '':
            item[u"船检"] = '*'
            item[u"船检意见"] = []
            self.getStatusCode(item,item[u"船检结论"])
        item[u"质检员"] = quadailyformline.fun_CheckChecker(line[12])
        item[u"登记人"] = uuser
        line[3] = str(line[3]).replace(' ','')
        if line[3] != '':
            item[u"报验次数"] = int(line[3])
        else:
            item[u"报验次数"] = 0
        item['date1'] = time.strftime("%Y-%m-%d", time.localtime())
        item['date2'] = time.strftime("%H:%M:%S", time.localtime())
        return item

    def importExcel(self,fpath='',uuser='',shipno=''):
        lines = quadailyformexcel.excel_table_byindex(fpath,3)
        items = []
        errlstTot = []
        lastItem = {}
        dformid = 0
        for line in lines:
            item = self.getdailyformobj(line,uuser)
            #有效性检查
            errlst = self.dferror.fun_checkobj(item,shipno)
            if len(errlst) == 0:
                if item[u"报验次数"] >= 1:
                    #写入数据库 并获取_id
                    self.insert(item)
                    lastItem = item
                    dformid = item["_id"]
                #如果存在报验意见
                if line[7] != '' or line[8] != '':
                    item2 = self.getdailyformcommobj(line,uuser)
                    self.insertComm(item2,dformid)
                    self.updateDFormAndComm(lastItem,item2)
                #报验单相互关联
                if item[u"报验次数"] >= 1:
                    self.getPreNextId(item,str(line[13]).replace(' ',''))
                #items.append(item)
            else:
                errlst2 = []
                for serr in errlst:
                    merr = {'dform':item[u'报验编号'],'err':serr}
                    errlst2.append(merr)
                errlstTot.extend(errlst2)
        #print(items)
        return {"datas":items,"errors":errlstTot}
 
if __name__ == '__main__':
    mdb = QuaDailyFormInput()
    mdb.importExcel('./upload/N781.xls')
   # mdb.exportExcelAll()
    #obj1 = mdb.get('2017-11-21')
   # print(obj1)
    #mdb.lockParam(mdb.delItem,'BY-N688-HB-003')
    #str1 = '{"报验项目":"测试33","报验专业":"HB"}'
    #obj1 = json.loads(str1)
    #obj2 = mdb.lockParam(mdb.addItem,obj1)
    #print(str(obj2))
    

    

