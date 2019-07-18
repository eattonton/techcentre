# -*- coding: utf-8 -*-
import os, sys
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
from django.http import HttpResponse, HttpResponseBadRequest
from utils.logger import Logger


class QuaDailyForm():
    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.lock = multiprocessing.Lock()
        self.majorDic = {"HB": "Hull", "HE": "Hull", "M": "Machinery", "O": "Outfitting", "E": "Electric",
                         "P": "Piping", "C": "Coating","IN":"Income"}
        self.items = []
        self.db_dict = {}
        self.mship = ship.Ship()
        self.dferror = quadailyformerror.QuaDailyFormError()
        self.myComment = quadailyformcomment.QuaDailyFormComment()

    def html(self, request, stype='', stype2='n'):
        str1 = request.GET.get('data', '')
        if str1 == '':
            str1 = request.POST.get('data', '')
        item = {}
        if str1 != '':
            item = json.loads(str1)
        obj1 = {}
        itype1 = int(request.GET.get('type', 0))
        if stype == 'insert':
            obj1 = self.lockParam(self.insert, item)
        elif stype == 'copy':
            obj1 = self.lockParam(self.copyCancel, item)
        elif stype == 'copycd':
            obj1 = self.lockParam(self.copyCD, item)
        elif stype == 'get':
            sfilter = request.GET.get('filter', '')
            if sfilter != '':
                mfilter = json.loads(sfilter)
                if "type" in mfilter:
                    if mfilter["type"] == 1:
                        obj1 = self.getDFormRelate(mfilter)
                    elif mfilter["type"] == 2:
                        obj1 = self.getComm(mfilter)
                else:
                    obj1 = self.get(mfilter)
        elif stype == 'getall':
            sfilter = request.GET.get('filter', '')
            if sfilter != '':
                mfilter = json.loads(sfilter)
                obj1 = self.getAllDFormComm(mfilter)
        elif stype == 'delete':
            obj1 = self.remove(item)
        elif stype == 'cancelrc':
            obj1 = self.recheckCancel(item)
        elif stype == 'update':
            obj1 = self.update(item)
        elif stype == 'removeall':
            ship1 = request.GET.get('shipno', '')
            if ship1 != '':
                obj1 = self.clearAllByShipNo(ship1)
        elif stype == "adjustState":
            obj1 = self.adjustState(item)
        str2 = json.dumps(obj1, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        response = HttpResponse(str2, content_type="application/json")
        if stype == 'getall' or stype == 'get':
            response["Access-Control-Allow-Origin"] = "*" 
            response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
            response["Access-Control-Max-Age"] = "1000"
            response["Access-Control-Allow-Headers"] = "*"
        return response

    def getDB(self, shipno):
        if shipno not in self.db_dict:
            self.db_dict[shipno] = []
            self.db_dict[shipno].append(self.client[shipno].quatb)
            self.db_dict[shipno].append(self.client[shipno].commenttb)
        return self.db_dict[shipno][0], self.db_dict[shipno][1]

    def lockNoParam(self, cb):
        res = None
        self.lock.acquire(10)
        try:
            res = cb()
        finally:
            self.lock.release()
        return res

    def lockParam(self, cb, *arg):
        res = None
        self.lock.acquire(10)
        try:
            res = cb(*arg)
        finally:
            self.lock.release()
        return res

    # 对象添加时间戳
    def timeMark(self, item):
        if u'报验日期' in item:
            if item.get(u'报验日期', '') != '':
                # 对日期进行修正
                item[u'报验日期'] = quadailyformline.fun_date(item[u'报验日期'])
                item[u'报验日期2'] = time.mktime(time.strptime(item[u'报验日期'], "%Y-%m-%d")) + 28800
        return item

    def timeByMark(self, timestamp):
        return time.strftime("%Y-%m-%d", time.localtime(timestamp - 28800))

    # 新建
    def insert(self, item):
        shipno = item[u'船号']
        tableNow, tableNow2 = self.getDB(shipno)
        major = item[u"报验专业"]
        # 日期修证
        if u'报验日期' in item:
            item[u'报验日期'] = quadailyformline.fun_date(item[u'报验日期'])
        obj4 = tableNow.find_one({u'状态': 0, u'报验专业': major})
        if obj4 == None:
            item['_id'] = self.getMaxId(tableNow) + 1
            order2 = self.getMaxOrder(tableNow, major) + 1
            item[u'序号'] = order2
            item[u'报验编号'] = 'BY-' + shipno + '-' + major + '-' + str(order2).rjust(3, '0')
            item[u'状态'] = 1
            item[u'报验次数'] = 1
            item['date1'] = time.strftime("%Y-%m-%d", time.localtime())
            item['date2'] = time.strftime("%H:%M:%S", time.localtime())
            self.timeMark(item)
            res1 = tableNow.insert_one(item)
            return item
        else:
            item[u'状态'] = 1
            item[u'报验次数'] = 1
            item[u'报验编号'] = obj4[u'报验编号']
            item['date1'] = time.strftime("%Y-%m-%d", time.localtime())
            item['date2'] = time.strftime("%H:%M:%S", time.localtime())
            self.timeMark(item)
            sres = tableNow.update({'_id': obj4['_id']}, {"$set": item}, multi=False)
            if sres['updatedExisting'] == False:
                return None
            else:
                return tableNow.find_one({'_id': obj4['_id']})
        return obj4

    def getShipAtt01(self, shipno):
        item = self.mship.getshipbyno(shipno)
        if item.get(u'复检连号', '') == '*':
            return True
        return False

    # 复检--取消
    def copyCancel(self, item1):
        item2 = deepcopy(item1)
        sid = item2['_id']
        sid2 = item2[u'报验编号']
        shipno = sid2.split('-')[1]
        major = item2[u"报验专业"]
        tableNow, tableNow2 = self.getDB(shipno)
        preId = sid
        item2['_id'] = self.getMaxId(tableNow) + 1
        # 记录最原始的报验编号
        if u'报验编号0' not in item2:
            item2[u'报验编号0'] = item2[u'报验编号']
        if self.getShipAtt01(shipno):
            # 新编码
            order2 = self.getMaxOrder(tableNow, major) + 1
            item2[u'序号'] = order2
            item2[u'报验编号'] = 'BY-' + shipno + '-' + major + '-' + str(order2).rjust(3, '0')
        item2['preid'] = sid
        item2[u'报验日期'] = ""
        item2[u'状态'] = 50
        item2[u'船东结论'] = ''
        item2[u'船检结论'] = ''
        item2[u'复检登记日期'] = time.strftime("%Y-%m-%d", time.localtime())
        item2['date1'] = time.strftime("%Y-%m-%d", time.localtime())
        item2['date2'] = time.strftime("%H:%M:%S", time.localtime())
        # 去掉nextid
        if 'nextid' in item2:
            item2.pop('nextid')
        self.timeMark(item2)
        res1 = tableNow.insert_one(item2)
        # 更新原先的
        item3 = {}
        item3["_id"] = item1["_id"]
        item3[u'报验编号'] = item1[u'报验编号']
        item3["nextid"] = item2['_id']
        self.update(item3)
        return item2

    def copyCD(self, obj1):
        arr1 = []
        for k in obj1:
            shipno = k.split('#')[0]
            sid = int(k.split('#')[1])
            tableNow, tableNow2 = self.getDB(shipno)
            item = tableNow.find_one({'_id': sid})
            obj2 = self.copyCDfrom1(item, obj1[k])
            arr1.append(obj2)
        return arr1

    # 复检--CD
    def copyCDfrom1(self, item1, commArr):
        item2 = deepcopy(item1)
        sid = item2['_id']
        sid2 = item2[u'报验编号']
        shipno = sid2.split('-')[1]
        major = item2[u"报验专业"]
        tableNow, tableNow2 = self.getDB(shipno)
        preId = sid
        item2['_id'] = self.getMaxId(tableNow) + 1
        # 记录最原始的报验编号
        if u'报验编号0' not in item2:
            item2[u'报验编号0'] = item2[u'报验编号']
        if self.getShipAtt01(shipno):
            # 新编码
            order2 = self.getMaxOrder(tableNow, major) + 1
            item2[u'序号'] = order2
            item2[u'报验编号'] = 'BY-' + shipno + '-' + major + '-' + str(order2).rjust(3, '0')
        item2['preid'] = sid
        item2[u'报验日期'] = ""
        item2[u'状态'] = 40
        item2[u'船东意见'] = commArr[u"船东意见"]
        item2[u'船检意见'] = commArr[u"船检意见"]
        item2[u'船东结论'] = ''
        item2[u'船检结论'] = ''
        # 如果上一次的状态为取消
        if item1[u'状态'] == 5:
            item2[u'报验次数'] = item1.get(u'报验次数', 1)
        else:
            item2[u'报验次数'] = item1.get(u'报验次数', 1) + 1
        item2[u'复检登记日期'] = time.strftime("%Y-%m-%d", time.localtime())
        item2['date1'] = time.strftime("%Y-%m-%d", time.localtime())
        item2['date2'] = time.strftime("%H:%M:%S", time.localtime())
        # 去掉nextid
        if 'nextid' in item2:
            item2.pop('nextid')
        self.timeMark(item2)
        res1 = tableNow.insert_one(item2)
        # 更新意见中的报验单列表
        for commid1 in commArr[u"船东意见"]:
            self.myComment.updateForm(shipno, commid1, item2['_id'])
        for commid2 in commArr[u"船检意见"]:
            self.myComment.updateForm(shipno, commid2, item2['_id'])
        # 更新原先的
        item3 = {}
        item3["_id"] = item1["_id"]
        item3[u'报验编号'] = item1[u'报验编号']
        item3["nextid"] = item2['_id']
        self.update(item3)
        return item2

    def getMaxId(self, tableNow):
        count2 = tableNow.find({}, {'_id': 1}).count()
        if count2 > 0:
            obj1 = tableNow.find({}, {'_id': 1}).sort("_id", pymongo.ASCENDING).skip(count2 - 1)
            return int(obj1[0]['_id'])
        else:
            return 0

    def getMaxOrder(self, tableNow, major):
        count2 = tableNow.find({u'报验专业': major}, {u"序号": 1}).count()
        if count2 > 0:
            obj1 = tableNow.find({u'报验专业': major}, {u"序号": 1}).sort(u"序号", pymongo.ASCENDING).skip(count2 - 1)
            return int(obj1[0][u"序号"])
        else:
            return 0

    def update(self, item):
        sid = item['_id']
        sid2 = item[u'报验编号']
        shipno = sid2.split('-')[1]
        tableNow, tableNow2 = self.getDB(shipno)
        status = item.get(u'状态', 1)
        obj1 = tableNow.find_one({'_id': sid})
        if obj1 != None:
            if status == 2 and obj1[u'状态'] == 0:
                return obj1
            elif status == 1 and obj1[u'状态'] == 0:
                return obj1
            self.timeMark(item)
            sres = tableNow.update({'_id': sid}, {'$set': item}, multi=False)
            return tableNow.find_one({'_id': sid})
        return obj1

    def adjustState(self,item):
        sid = item['_id']
        sid2 = item[u'报验编号']
        shipno = sid2.split('-')[1]
        tableNow, tableNow2 = self.getDB(shipno)
        obj1 = tableNow.find_one({'_id': sid})
        if not obj1:
            return  {"state":False,"data":u"数据已经不存在,请刷新"}

        sres = tableNow.update({'_id': sid}, {'$set': item}, multi=False)
        return {"state":True,"data":tableNow.find_one({'_id': sid})}

    def remove(self, item):
        sid = item['_id']
        sid2 = item[u'报验编号']
        shipno = sid2.split('-')[1]
        tableNow, tableNow2 = self.getDB(shipno)
        obj1 = tableNow.find_one({'_id': sid})
        bdelOk = False
        if obj1[u'状态'] <= 1:
            if u'状态2' in obj1:
                if obj1[u'状态2'] == 40 or obj1[u'状态2'] == 50:
                    bdelOk = True
                    sres = tableNow.update({'_id': sid}, {'$set': {u'状态': obj1[u'状态2'], u'状态2': 0}}, multi=False)
            if bdelOk == False:
                item[u'报验专业'] = obj1[u'报验专业']
                item[u'序号'] = obj1[u'序号']
                self.timeMark(item)
                sres = tableNow.update({'_id': sid}, item, multi=False)

        # 当意见为取消时,并且不存在复验时,能够删除数据
        if obj1[u"状态"] == 5 and obj1.get(u"状态2", "") != 50:
            tableNow.update({'_id': sid}, {'$set': {u'状态': item[u'状态'], u'状态2': 0}})
        return tableNow.find_one({'_id': sid})

    # 意见取消复检
    def recheckCancel(self, item):
        sid = item['_id']
        sid2 = item[u'报验编号']
        shipno = sid2.split('-')[1]
        tableNow, tableNow2 = self.getDB(shipno)
        obj1 = tableNow.find_one({'_id': sid})
        # 取消意见文档中的报验单数组中的项
        if obj1[u'状态'] == 4 or obj1[u'状态'] == 40:
            arr1 = obj1.get(u'船东意见', [])
            arr2 = obj1.get(u'船检意见', [])
            for commid1 in arr1:
                tableNow2.update({"_id": commid1}, {"$pull": {u"报验单": sid}}, multi=False)
                tableNow2.update({"_id": commid1}, {'$set': {u'意见状态': 1}}, multi=False)
            for commid2 in arr2:
                tableNow2.update({"_id": commid2}, {"$pull": {u"报验单": sid}}, multi=False)
                tableNow2.update({"_id": commid2}, {'$set': {u'意见状态': 1}}, multi=False)
        # 修改当前报验单的状态
        if 'preid' in obj1:
            tableNow.update({"nextid": sid}, {'$set': {'nextid': 0}}, multi=True)
        tableNow.update({"_id": sid}, {'_id': sid, u'状态': 0}, multi=False)
        item[u"状态"] = 0
        return item

    # 只获得报验单  all
    def get(self, sfilter={}, sortkey=[(u'报验编号', pymongo.ASCENDING)]):
        status = sfilter.get(u'状态', 0)
        if u"船号" in sfilter:
            shipno = sfilter[u"船号"]
            sfilter.pop(u"船号")
            arr1 = []
            tableNow, tableNow2 = self.getDB(shipno)
            obj1 = tableNow.find(sfilter).sort(sortkey)
            for obj2 in obj1:
                arr1.append(obj2)
            return arr1
        elif u'船名' in sfilter:
            shipname = sfilter[u"船名"]
            sfilter.pop(u"船名")
            shipdb = ship.Ship()
            shiplst = shipdb.getshipno(shipname)
            arr1 = []
            for shipno in shiplst:
                tableNow, tableNow2 = self.getDB(shipno)
                obj1 = tableNow.find(sfilter).sort(sortkey)
                for obj2 in obj1:
                    arr1.append(obj2)
            return arr1
        else:
            arr1 = []
            shipnoall = self.mship.getshipnolst()
            Logger.dict(sfilter)
            for shipno in shipnoall:
                tableNow, tableNow2 = self.getDB(shipno)
                obj1 = tableNow.find(sfilter).sort(sortkey)
                print(shipno, obj1.count())
                for obj2 in obj1:
                    arr1.append(obj2)
            return arr1

    # 从报验单+报验意见  one
    def getComm(self, mfilter):
        sid = mfilter['_id']
        sid2 = mfilter[u"报验编号"]
        shipno = sid2.split('-')[1]
        tableNow, tableNow2 = self.getDB(shipno)
        obj1 = tableNow.find_one({'_id': sid})
        return self.getOneDFormComm(obj1)

    def getOneDFormComm(self, obj1, bck=False):
        shipno = obj1[u'船号']
        tableNow, tableNow2 = self.getDB(shipno)
        arr1 = []
        arr2 = obj1.get(u'船东意见', [])
        for id2 in arr2:
            obj2 = tableNow2.find_one({'_id': id2})
            obj4 = deepcopy(obj1)
            obj4['_id2'] = obj2['_id']
            obj4[u'意见编号'] = obj2[u'意见编号']
            obj4[u'意见内容'] = obj2[u'意见内容']
            obj4[u'意见分类'] = obj2[u'意见分类']
            obj4[u'意见状态'] = obj2[u'意见状态']
            obj4[u'责任工区'] = obj2.get(u'责任工区', '')
            obj4[u'关闭日期'] = obj2.get(u'关闭日期', '')
            if obj1.get(u'船东结论','') == 'B' and obj2.get(u'B意见状态',0) != 1:
                obj4[u'关闭日期'] = ""
            obj4[u"转移时间"] = obj2.get(u"转移时间",'')
            if bck:
                if obj1['_id'] == obj2[u'报验单1']:
                    arr1.append(obj4)
            else:
                arr1.append(obj4)
        arr3 = obj1.get(u'船检意见', [])
        for id3 in arr3:
            obj3 = tableNow2.find_one({'_id': id3})
            obj4 = deepcopy(obj1)
            obj4['_id2'] = obj3['_id']
            obj4[u'意见编号'] = obj3[u'意见编号']
            obj4[u'意见内容'] = obj3[u'意见内容']
            obj4[u'意见分类'] = obj3[u'意见分类']
            obj4[u'意见状态'] = obj3[u'意见状态']
            obj4[u'责任工区'] = obj3.get(u'责任工区', '')
            obj4[u'关闭日期'] = obj3.get(u'关闭日期', '')
            if obj1.get(u'船检结论','') == 'B' and obj3.get(u'B意见状态',0) != 1:
                obj4[u'关闭日期'] = ""
            if bck:
                if obj1['_id'] == obj3[u'报验单1']:
                    arr1.append(obj4)
            else:
                arr1.append(obj4)
        if len(arr1) == 0:
            arr1.append(obj1)
        return arr1

    # 获取报验单=报验已经 all
    def getAllDFormComm(self, sfilter={}, sortkey=[(u'报验编号', pymongo.ASCENDING)]):
        state = int(sfilter.get("state",-1))
        if "state" in sfilter:
            del(sfilter["state"])
        sfilter[u"状态"]={"$gte":2}

        #所有意见未关闭
        if state == 2:
            sfilter[u"报验单关闭日期"]={"$exists":False}

        #所有意见关闭
        if state == 3:
            sfilter[u"报验单关闭日期"]= {"$exists":True}

        items = self.get(sfilter, sortkey)
        arr1 = []
        for item in items:
            if 'preid' in item or 'nextid' in item:
                # 获取报验单相关
                tableNow, tableNow2 = self.getDB(item[u'船号'])
                preid = item.get('preid', 0)
                if preid != 0:
                    obj1 = tableNow.find_one({'_id': preid}, {u'报验编号': 1})
                    item[u'上次报验单'] = obj1[u'报验编号']
                nextid = item.get('nextid', 0)
                if nextid != 0:
                    obj2 = tableNow.find_one({'_id': nextid}, {u'报验编号': 1})
                    item[u'下次报验单'] = obj2.get(u'报验编号', '--')
            arr2 = self.getOneDFormComm(item, True)
            arr1.extend(arr2)
        return arr1

    # 根据报验单id 获得 所关联的报验单
    def getDFormRelate(self, mfilter):
        sid = mfilter['_id']
        sid2 = mfilter[u"报验编号"]
        shipno = sid2.split('-')[1]
        tableNow, tableNow2 = self.getDB(shipno)
        validVal = {'_id': 1, u'报验编号': 1, u'报验日期': 1, u'报验次数': 1, 'nextid': 1, 'preid': 1}
        item = tableNow.find_one({'_id': sid}, validVal)
        arr1 = []
        # 通过preid 往前获取
        if item != None:
            arr1.append(item)
            while 1:
                if 'preid' in item:
                    if item['preid'] != 0:
                        item = tableNow.find_one({'_id': item['preid']}, validVal)
                        arr1.insert(0, item)
                    else:
                        break
                else:
                    break
            item = tableNow.find_one({'_id': sid}, validVal)
            while 1:
                if 'nextid' in item:
                    if item['nextid'] != 0:
                        item = tableNow.find_one({'_id': item['nextid']}, validVal)
                        arr1.append(item)
                    else:
                        break
                else:
                    break
        return arr1

    def exportExcel(self, sid, sid2):
        shipno = sid2.split('-')[1]
        tableNow, tableNow2 = self.getDB(shipno)
        Logger.list([sid, sid2])
        if sid.find(',') == -1:
            obj1 = tableNow.find_one({'_id': int(sid)})
            # 根据船号 获得 项目描述
            obj1[u"项目名"] = self.mship.getshipdesc(obj1[u"船号"])
            if obj1 != None:
                return quadailyformexcel.excel_export_one(obj1)
        else:
            items = []
            sids2_t = sid.split(',')
            sids2_t2 = sid2.split(',')
            num1 = len(sids2_t)
            for sid2_t, sid2_t2 in zip(sids2_t, sids2_t2):
                sid2_t = int(sid2_t)
                if sid2_t != 0 and sid2_t2 != '':
                    shipno2 = sid2_t2.split('-')[1]
                    tableNow21, tableNow22 = self.getDB(shipno2)
                    obj2 = tableNow21.find_one({'_id': sid2_t})
                    obj2[u"项目名"] = self.mship.getshipdesc(obj2[u"船号"])
                    items.append(obj2)
            return quadailyformexcel.excel_export_batch(items)
        return ''

    def exportExcelList(self, sid, sid2):
        shipno = sid2.split('-')[1]
        tableNow, tableNow2 = self.getDB(shipno)
        items = {"Hull": [], "Machinery": [], "Outfitting": [], "Electric": [], "Piping": [], "Coating": [], "Income": []}
        sfile = ""
        sproj = ""
        sdate = ""
        if sid.find(',') == -1:
            obj1 = tableNow.find_one({'_id': int(sid)})
            major = self.majorDic[obj1[u"报验专业"]]
            if major not in items:
                items[major] = []
            items[major].append(obj1)
            if sfile == "":
                sfile = sid2
            if sproj == "":
                sproj = shipno
            if sdate == "":
                sdate = obj1[u'报验日期']
        else:
            ssids2 = sid.split(',')
            ssids22 = sid2.split(',')
            # ssids22.sort()
            num1 = len(ssids2)
            for idx in range(0, num1):
                ssid2 = int(ssids2[idx])
                ssid22 = ssids22[idx]
                if ssid2 != 0 and ssid22 != '':
                    shipno2 = ssid22.split('-')[1]
                    tableNow21, tableNow22 = self.getDB(shipno2)
                    obj2 = tableNow21.find_one({'_id': ssid2})
                    major = self.majorDic[obj2[u"报验专业"]]
                    if major not in items:
                        items[major] = []
                    items[major].append(obj2)
                    if sfile == "":
                        sfile = ssid22
                    if sproj == "":
                        sproj = shipno2
                    if sdate == "":
                        sdate = obj2[u'报验日期']
        return quadailyformexcel.excel_export_list(items, sfile, sproj, sdate)

    # 输出报验汇总表
    def exportExcelAll(self, shipno):
        sfilter = {u'船号': shipno, "$where": "this.状态>=2"}
        items = self.getAllDFormComm(sfilter, [(u'报验日期', pymongo.ASCENDING), (u'报验编号', pymongo.ASCENDING)])
        return quadailyformexcel.excel_export_all(items, shipno)

    def importExcel(self, fpath='', uuser=''):
        lines = quadailyformexcel.excel_table_byindex(fpath, 1)
        items = []
        errlstTot = []
        for line in lines:
            item = {}
            item[u"船号"] = line[0].upper().replace(' ', '')
            if item[u"船号"] == '':
                continue
            item[u"报验日期"] = quadailyformline.fun_date(line[1])
            item[u"报验时间"] = quadailyformline.fun_time(line[2])
            item[u"分段系统"] = line[3]
            item[u"报验专业"] = line[4].upper().replace(' ', '')
            item[u"报验地点"] = quadailyformline.fun_CheckPlace(line[5])
            item[u"报验项目"] = line[6]
            item[u"报验工区"] = quadailyformline.fun_CheckDepartment(line[7])
            item[u"施工班组"] = line[8]
            item[u"工区申请人"] = line[9]
            item[u"船东"] = line[10]
            item[u"船检"] = line[11]
            item[u"质检员"] = quadailyformline.fun_CheckChecker(line[12])
            item[u"登记人"] = uuser
            # 有效性检查
            errlst = self.dferror.fun_checkobj(item)
            if len(errlst) == 0:
                obj1 = self.insert(item)
                items.append(obj1)
            else:
                errlstTot.extend(errlst)
        return {"datas": items, "errors": errlstTot}

    # 清空数据库
    def clearAllByShipNo(self, shipno):
        tableNow, tableNow2 = self.getDB(shipno)
        tableNow.remove()
        tableNow2.remove()
        return 0


if __name__ == '__main__':
    mdb = QuaDailyForm()
    # filter1={u"状态":{"$in":[2,3,4,5]}}
    # mdb.exportExcelAll()
    # obj1 = mdb.get('2017-11-21')
    # print(obj1)
    # mdb.lockParam(mdb.delItem,'BY-N688-HB-003')
    # str1 = '{"报验项目":"测试33","报验专业":"HB"}'
    # obj1 = json.loads(str1)
    # obj2 = mdb.lockParam(mdb.addItem,obj1)
    # print(str(obj2))
