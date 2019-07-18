# -*- coding: utf-8 -*-
import os,sys
import json
import datetime
import time
import multiprocessing  
import json
import pymongo
import threading
import ship
import quadailyformexcel
from copy import deepcopy
from django.http import HttpResponse,HttpResponseBadRequest

class QuaDailyFormComment():
    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1',27017 )
        self.lock = multiprocessing.Lock()
        #加载船号
        self.db_dict = {}
    
    def lockNoParam(self,cb):
        res = None
        self.lock.acquire(10)  
        try: 
            res = cb()
        finally:  
            self.lock.release()
        return res

    def lockParam(self,cb,*arg):
        res = None
        self.lock.acquire(10)  
        try: 
            res = cb(*arg)
        finally:  
            self.lock.release()
        return res

    def html(self,request,stype,stype2=''):
        print(stype)
        request2 = None
        if request.method == "POST":
            request2 = request.POST
        else:
            request2 = request.GET
        sdata = request2.get('data','')
        jsonData = {}
        if sdata != '':
            jsonData = json.loads(sdata)
        obj1 = {"state":False,"data":"not int"}
        if stype == 'get':
            sfilter = request2.get('filter','')
            sfilter2 = request2.get('filter1','')
            sfilter3 = request2.get('filter2','')
            if sfilter != '':
                mfilter = json.loads(sfilter)
                if "type" in mfilter:
                    if mfilter["type"] == 0:
                        obj1 = self.getByDFromId(mfilter)
                else:
                    obj1 = self.get(mfilter)
            elif sfilter2 != '' and sfilter3 != '':
                mfilter2 = json.loads(sfilter2)
                mfilter3 = json.loads(sfilter3)
                if mfilter2.get(u'意见状态',0) == 3:
                    obj1 = self.getDFromAndCommB(mfilter2,mfilter3)
                else:
                    obj1 = self.getDFromAndComm(mfilter2,mfilter3)
            else:
                obj1 = self.get()
        elif stype == 'update':
            str1 = request2.get('data','')
            itype = int(request2.get('type',0))
            item = json.loads(str1)
            if str1 != '' and itype == 2:
                obj1 = self.update(item)
            elif str1 != '':
                obj1 = self.lockParam(self.commentUpdate,item)
                #obj1 = self.commentUpdate(item)
        elif stype == "adjustRate":
            str1 = request2.get('data', '')
            item = json.loads(str1)
            obj1 = self.ajustRateState(item)
        else:
            obj1 ={"state":False,"data":"not in"}
            print (stype)
        str2 = json.dumps(obj1, sort_keys=True,ensure_ascii=False,separators=(',',':'))
        response = HttpResponse(str2, content_type="application/json")
        if stype == 'get':
            response["Access-Control-Allow-Origin"] = "*" 
            response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
            response["Access-Control-Max-Age"] = "1000"
            response["Access-Control-Allow-Headers"] = "*"
        return response  

    def getDB(self,shipno):
        if shipno not in self.db_dict:
            self.db_dict[shipno] = []
            self.db_dict[shipno].append(self.client[shipno].commenttb)
            self.db_dict[shipno].append(self.client[shipno].quatb)
        return self.db_dict[shipno][0],self.db_dict[shipno][1]

    def getMaxId(self,tableNow):
        count2 =  tableNow.find({},{'_id':1}).count()
        if count2 > 0:
            obj1 = tableNow.find({},{'_id':1}).sort("_id",pymongo.ASCENDING).skip(count2 - 1)
            return int(obj1[0]['_id'])
        else:
            return 0

    def getMaxOrder(self,tableNow,order):
        count2 =  tableNow.find({u'报验编号':order},{u"序号":1}).count()
        if count2 > 0:
            obj1 = tableNow.find({u'报验编号':order},{u"序号":1}).sort(u"序号",pymongo.ASCENDING).skip(count2 - 1)
            return int(obj1[0][u"序号"])
        else:
            return 0
    #此函数可以删除
    def inserts(self,dfitem):
        sid = dfitem[u'报验编号']
        commlst = dfitem[u'报验意见']
        for comm1 in commlst:
            if comm1['_id'] == 0 and comm1[u'意见状态'] == 0:
                self.insert(comm1)
            elif comm1['_id'] != 0 and comm1[u'意见状态'] == -1:
                self.remove(comm1)
            elif comm1['_id'] != 0 and comm1[u'意见状态'] == 0:
                self.update(comm1)

    def insert(self,item):
        sid = item[u'报验编号']
        shipno = sid.split('-')[1]
        tableNow,tableNow2 = self.getDB(shipno)
        item['_id'] = self.getMaxId(tableNow) + 1
        item[u'序号'] = self.getMaxOrder(tableNow,sid) + 1
        item[u'意见编号'] = sid + '-' + str(item[u'序号'])
        item['date1'] = time.strftime("%Y-%m-%d", time.localtime())
        item['date2'] = time.strftime("%H:%M:%S", time.localtime())
        tableNow.insert_one(item)
        return item

    def update(self,item):
        sid = item['_id']
        sid2 = item[u'意见编号']
        shipno = sid2.split('-')[1]
        tableNow,tableNow2 = self.getDB(shipno)
        if item.get(u'意见状态',0) == 3:
            item[u'关闭日期'] = time.strftime("%Y-%m-%d", time.localtime())
            item[u'关闭时间'] = time.strftime("%H:%M:%S", time.localtime())
        tableNow.update({'_id':sid},{"$set":item},multi=False)
        obj2 = tableNow.find_one({'_id':sid})
        return obj2

    # 调整报验单是否计入合格率统计中
    def ajustRateState(self,item):
        sid = item["_id"]
        tongji = item[u"合格率统计"]
        danh = item[u'报验编号']
        shipno = danh.split('-')[1]
        tableNow, tableNow2 = self.getDB(shipno)
        tableNow2.update({'_id': sid}, {"$set":{"合格率统计": tongji}}, multi=False)
        obj2 = tableNow2.find_one({'_id': sid})
        return  {"state":True,"data":obj2}

    #更新报验单列表
    def updateForm(self,shipno,commid,formid):
        tableNow,tableNow2 = self.getDB(shipno)
        obj1 = tableNow.find_one({'_id':commid})
        obj1[u"报验单"].append(formid)
        obj1[u"意见状态"] = 2
        tableNow.update({'_id':commid},{"$set":obj1},multi=False)
        return obj1


    #处理意见 更新报验单 和 意见文档
    def commentUpdate(self,item):
        sid = item['_id']
        sid2 = item[u'报验编号']
        shipno = sid2.split('-')[1]
        tableNow,tableNow2 = self.getDB(shipno)
        obj1 = tableNow2.find_one({'_id':sid})
        if obj1 != None:
            item2 = {}
            item2[u"船东意见"] = obj1.get(u"船东意见",[])
            item2[u"船检意见"] = obj1.get(u"船检意见",[])
            if u'船东结论' in item:
                item2[u'船东结论'] = item[u'船东结论']
            if u'船检结论' in item:
                item2[u'船检结论'] = item[u'船检结论']
            item2[u'状态'] = item.get(u'状态',"")
            baoyan = item.get(u"报验项目")
            if baoyan is not  None:
                item2[u"报验项目"] = baoyan
            ##写入意见数据
            for itemcomm in item[u"报验意见"]:
                #更新意见数据表
                stype,itype,commid = self.doneComment(itemcomm)
                if itype == 1:
                    item2[stype].append(commid)
                elif itype == 2:
                    if commid in item2[stype]:
                        item2[stype].remove(commid)
            sres = tableNow2.update({'_id':sid}, {'$set': item2},multi=False)
            dform = tableNow2.find_one({'_id':sid})
            if dform.get(u'船东结论','') == 'A' or dform.get(u'船东结论','') == 'B' or dform.get(u'船检结论','') == 'A' or dform.get(u'船检结论','') == 'B':
                self.doneCommentOk(dform)
            else:
                self.doneCommentCancel(dform)
            return dform
        return None

    #对报验单包括的意见，如果为A.B就行意见状态关闭=3
    def doneCommentOk(self,obj1):
        shipno = obj1[u'船号']
        tableNow,tableNow2 = self.getDB(shipno)
        arr2 = obj1.get(u'船东意见',[])
        for id2 in arr2:
            if obj1[u'船东结论'] == 'A' or obj1[u'船东结论'] == 'B':
                item = {}
                item[u'意见状态'] = 3
                item[u'关闭日期'] = time.strftime("%Y-%m-%d", time.localtime())
                item[u'关闭时间'] = time.strftime("%H:%M:%S", time.localtime())
                tableNow.update({'_id':id2},{"$set":item},multi=False)
        arr3 = obj1.get(u'船检意见',[])
        for id3 in arr3:
            if obj1.get(u'船检结论','') == 'A' or obj1.get(u'船检结论','') == 'B':
                item = {}
                item[u'意见状态'] = 3
                item[u'关闭日期'] = time.strftime("%Y-%m-%d", time.localtime())
                item[u'关闭时间'] = time.strftime("%H:%M:%S", time.localtime())
                tableNow.update({'_id':id3},{"$set":item},multi=False)
        self.doneComentOkItem(obj1,tableNow2)

    #新增了一个报验单关闭日期, -- 在意见处理的时候需要更新 报验单关闭日期
    #在报验汇总的时候需要去检查 报验单是否已经关闭
    #设置报验单的意见状态关闭
    def doneComentOkItem(self,obj1,tableNow2):
        cdong = obj1.get(u"船东",None) == "*"
        cjian = obj1.get(u"船检",None) == "*"
        cdongOk = obj1.get(u'船东结论',"C") in ["A","B"]
        cjianOk = obj1.get(u'船东结论',"C") in ["A", "B"]
        if (cdong and not cdongOk) or (cjian and not cjianOk):
            return tableNow2.update({"_id":obj1["_id"]},
                                    {"$unset":{u'报验单关闭日期': ''}})

        tableNow2.update({"_id":obj1["_id"]},{"$set":{u"报验单关闭日期":time.strftime("%Y-%m-%d", time.localtime())}})

    #如果第二次复检后还是没通过
    def doneCommentCancel(self,obj1):
        shipno = obj1[u'船号']
        tableNow,tableNow2 = self.getDB(shipno)
        arr2 = obj1.get(u'船东意见',[])
        for id2 in arr2:
            obj2 = tableNow.find_one({'_id':id2})
            if obj1.get(u'船东结论','') != 'A' and obj1.get(u'船东结论','') != 'B':
                if obj2[u'意见状态'] == 2:
                    tableNow.update({'_id':id2},{"$set":{u'意见状态':1}},multi=False)
        arr3 = obj1.get(u'船检意见',[])
        for id3 in arr3:
            obj3 = tableNow.find_one({'_id':id3})
            if obj1.get(u'船检结论','') != 'A' and obj1.get(u'船检结论','') != 'B':
                if obj3[u'意见状态'] == 2:
                    tableNow.update({'_id':id3},{"$set":{u'意见状态':1}},multi=False)

    def doneComment(self,itemcomm):
        stype = ''
        if itemcomm[u"意见分类"] == u"船东":
            stype = u'船东意见'
        elif itemcomm[u"意见分类"] == u"船检":
            stype = u"船检意见"
        itype = 0
        commid = 0
        if itemcomm.get("_id",0) == 0 and itemcomm.get(u"意见状态",0) == 1:
            #如果不存在_id就新建
            itemcomm2 = self.insert(itemcomm)
            commid = itemcomm2['_id']
            itype = 1
        elif itemcomm.get("_id",0) == 0 and itemcomm.get(u"意见状态",0) == 11:
            #如果不存在_id就新建
            itemcomm2 = self.insert(itemcomm)
            commid = itemcomm2['_id']
            itype = 1
        elif itemcomm.get("_id",0) == 0 and itemcomm.get(u"意见状态",0) == 21:
            #如果不存在_id就新建
            itemcomm2 = self.insert(itemcomm)
            commid = itemcomm2['_id']
            itype = 1
        elif itemcomm.get("_id",0) != 0 and itemcomm.get(u"意见状态",0) == -1:
            #删除
            commid = self.remove(itemcomm)
            itype = 2
        elif itemcomm.get("_id",0) != 0 and itemcomm.get(u"意见状态",0) == 1:
            #修改
            self.update(itemcomm)
        elif itemcomm.get("_id",0) != 0 and itemcomm.get(u"意见状态",0) == 11:
            #修改
            self.update(itemcomm)
        elif itemcomm.get("_id",0) != 0 and itemcomm.get(u"意见状态",0) == 21:
            #修改
            self.update(itemcomm)
        elif itemcomm.get("_id",0) != 0:
            #修改
            self.update(itemcomm)
        return stype,itype,commid

    def remove(self,item):
        sid = item['_id']
        shipno = item[u'报验编号'].split('-')[1]
        tableNow,tableNow2 = self.getDB(shipno)
        tableNow.remove({'_id':sid})
        return sid

    def clear(self,sid):
        shipno = sid.split('-')[1]
        tableNow,tableNow2 = self.getDB(shipno)
        tableNow.remove({u'报验编号':sid})

    def get(self,sfilter={}):
        arr1 = []
        if u"船号" in sfilter:
            shipno = sfilter[u"船号"]
            arr1 = self.getByShipNo(sfilter,shipno)
        elif u'船名' in sfilter:
            shipdb = ship.Ship()
            shiplst = shipdb.getshipno(sfilter[u"船名"])
            for shipno in shiplst:
                arr2 = self.getByShipNo(sfilter,shipno)
                arr1.extend(arr2)
        else:
            arr1 = self.getAll(sfilter)
        return arr1

    def getAll(self,sfilter={}):
        arr1 = []
        #加载船号
        shipdb = ship.Ship()
        shoparr = shipdb.getshipnolst()
        for mship in shoparr:
            arr2 = self.getByShipNo(sfilter,mship[u'船号'])
            arr1.extend(arr2)
        return arr1
            
    #根据船号
    def getByShipNo(self,sfilter={},shipno=''):
        arr1 = []
        #记录报验单
        dict1 = {}
        tableNow,tableNow2 = self.getDB(shipno)
        items = tableNow.find(sfilter).sort(u"意见编号",pymongo.ASCENDING)
        for item in items:
            sids = item[u'报验单']
            sid = sids[0]
            item['_id2'] = sid
            if sid not in dict1:
                dict1[sid] = tableNow2.find_one({'_id':sid},{'_id':0,u'报验次数':1,u'报验编号':1,u'船号':1,u'报验日期':1,u'报验地点':1,u'报验项目':1,u'报验工区':1,u'报验专业':1,u'质检员':1})
            item.update(dict1[sid])
            arr1.append(item)
        return arr1

    #根据编号获取
    #获取包含某报验单的意见数组
    def getByDFromId(self,mfilter):
        shipno = mfilter[u'船号']
        tableNow,tableNow2 = self.getDB(shipno)
        mfilter2 = {}
        mfilter2[u'报验单'] = mfilter['_id']
        mfilter2[u'意见分类']= mfilter[u'意见分类']
        items = tableNow.find(mfilter2)
        arr1 = []
        for item in items:
            arr1.append(item)
        return arr1

    #根据管道附带报验单表进行联合查询
    def getDFromAndComm(self,mfilter1={},mfilter2={}):
        arr1 = []
        if u'船号' in mfilter1:
            shipno = mfilter1.pop(u'船号')
            arr2 = self.getDFromAndCommByShipno(shipno,mfilter1,mfilter2)
            arr1.extend(arr2)
        else:
            shipdb = ship.Ship()
            shoparr = shipdb.getshipnolst()
            for shipno in shoparr:
                arr2 = self.getDFromAndCommByShipno(shipno,mfilter1,mfilter2)
                arr1.extend(arr2)
        #整理输出
        arr3 = []
        for item1 in arr1:
            item2 = {}
            if 'dform' in item1:
                if len(item1['dform']) > 0:
                    item2[u'船号'] = item1['dform'][0].get(u'船号','')
                    item2[u'报验日期'] = item1['dform'][0].get(u'报验日期','')
                    item2[u'报验次数'] = item1['dform'][0].get(u'报验次数','')
                    item2[u'报验项目'] = item1['dform'][0].get(u'报验项目','')
                    item2[u'报验工区'] = item1['dform'][0].get(u'报验工区','')
                    item2[u'质检员'] = item1['dform'][0].get(u'质检员','')
                    item2[u'_id2'] = item1['dform'][0].get('_id',0)
                   # item2[u'船东意见'] = item1['dform'][0].get(u'船东意见',[])
                    #item2[u'船检意见'] = item1['dform'][0].get(u'船检意见',[])
                    for k in item1:
                        if k != 'dform':
                            item2[k] = item1[k]
                    arr3.append(item2)
        return arr3

    #根据管道附带报验单表进行联合查询 B意见
    def getDFromAndCommB(self,mfilter1={},mfilter2={}):
        arr1 = []
        if u'船号' in mfilter1:
            shipno = mfilter1.pop(u'船号')
            arr2 = self.getDFromAndCommByShipno(shipno,mfilter1,mfilter2)
            arr1.extend(arr2)
        else:
            shipdb = ship.Ship()
            shoparr = shipdb.getshipnolst()
            for shipno in shoparr:
                arr2 = self.getDFromAndCommByShipno(shipno,mfilter1,mfilter2)
                arr1.extend(arr2)
        #整理输出
        arr3 = []
        for item1 in arr1:
            item2 = {}
            if 'dform' in item1:
                if len(item1['dform']) > 0:
                    sCommType = item1.get(u'意见分类','')
                    sCommRes = item1['dform'][0].get(sCommType+u'结论','')
                    if sCommRes == "B":
                        item2[u'船号'] = item1['dform'][0].get(u'船号','')
                        item2[u'报验日期'] = item1['dform'][0].get(u'报验日期','')
                        item2[u'报验次数'] = item1['dform'][0].get(u'报验次数','')
                        item2[u'报验项目'] = item1['dform'][0].get(u'报验项目','')
                        item2[u'报验工区'] = item1['dform'][0].get(u'报验工区','')
                        item2[u'质检员'] = item1['dform'][0].get(u'质检员','')
                        item2[u'_id2'] = item1['dform'][0].get('_id',0)
                        item2[u'船东结论'] = item1['dform'][0].get(u'船东结论','')
                        item2[u'船检结论'] = item1['dform'][0].get(u'船检结论','')
                        for k in item1:
                            if k != 'dform':
                                item2[k] = item1[k]
                        arr3.append(item2)
        return arr3

    def getDFromAndCommByShipno(self,shipno,mfilter1={},mfilter2={}):
        tableNow,tableNow2 = self.getDB(shipno)
        mfilter22 = {}
        for k in mfilter2:
            mfilter22['dform.'+k] = mfilter2[k]
        pipeline = [{'$match':mfilter1},{"$lookup":{"localField":"报验单1","from":"quatb","foreignField":"_id","as":"dform"}},{'$match':mfilter22}]
        return list(tableNow.aggregate(pipeline))

    def exportCommentUndo(self,mfilter):
        sfilter1 = mfilter.get(u'船号','')
        #sfilter2 = mfilter.get('filter2','')
        #mfilter1 = {u'意见状态':{'$in':[1,2]}}
        #mfilter2 = {u'船号':sfilter1}
        mfilter1 = {u'船号':sfilter1,u'意见状态':{'$in':[1,2]}}
        mfilter2 = {}
        items=[]
        items = self.getDFromAndComm(mfilter1,mfilter2)
        return quadailyformexcel.excel_export_commentUndo(sfilter1,items)

if __name__ == '__main__':
    mdb = QuaDailyFormComment()
    mfilter1 = {u'船号':"N688",u'意见状态':{'$in':[1,2]}}
    mfilter2 = {}
    items = mdb.getDFromAndComm(mfilter1,mfilter2)
    print(items)
    #arr1 = mdb.getDFromAndCommByShipno('N636',{u"意见状态":1},{u"报验日期":"2017-12-19"})
    #print(arr1)
    #obj1 = mdb.get('2017-11-21')
    #print(obj1)
    #mdb.lockParam(mdb.delItem,'BY-N688-HB-003')
    #str1 = '{"报验项目":"测试33","报验专业":"HB"}'
    #obj1 = json.loads(str1)
    #obj2 = mdb.lockParam(mdb.addItem,obj1)
    #print(str(obj2))
    

    

