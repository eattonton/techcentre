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


class QuaDailyFormCount():
    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db_dict = {}
        self.mship = ship.Ship()

    def html(self, request, stype='', stype2='n'):
        obj1 = {}
        if stype == 'get':
            sfilter = request.GET.get('filter', '')
            if sfilter != '':
                mfilter = json.loads(sfilter)
                if u'分类' not in sfilter or u'报验工区' not in sfilter:
                    obj1 = self.get2(mfilter)
                else:
                    obj1 = self.get(mfilter)

        str2 = json.dumps(obj1, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        response = HttpResponse(str2, content_type="application/json")
        if stype == 'get':
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

    def get(self, sfilter={}):
        if u"船号" in sfilter:
            shipno = sfilter[u"船号"]
            flagT = sfilter[u"分类"]
            sfilter.pop(u"船号")
            sfilter.pop(u'分类')
            arr1 = []
            obj1 = self.getShipCount(shipno, flagT, sfilter)
            if obj1.get(u'合计', 0) != 0:
                arr1.append(obj1)
            return arr1
        elif u'船名' in sfilter:
            shipname = sfilter[u"船名"]
            flagT = sfilter[u"分类"]
            sfilter.pop(u"船名")
            sfilter.pop(u'分类')
            shipdb = ship.Ship()
            shiplst = shipdb.getshipno(shipname)
            arr1 = []
            for shipno in shiplst:
                obj1 = self.getShipCount(shipno, flagT, sfilter)
                if obj1.get(u'合计', 0) != 0:
                    arr1.append(obj1)
            return arr1
        else:
            flagT = sfilter[u"分类"]
            sfilter.pop(u'分类')
            arr1 = []
            shoparr = self.mship.getshipnolst()
            for shipno in shoparr:
                obj1 = self.getShipCount(shipno, flagT, sfilter)
                if obj1.get(u'合计', 0) != 0:
                    arr1.append(obj1)
            return arr1

    def get2(self, sfilter={}):
        arr1 = []
        arrTypes = [u'船东', u'船检']
        arrPlaces = [u"分段工区", u"搭载工区", u"机装工区", u"电装工区", u"舾装工区", u"涂装工区",u"制造工区"]
        if u'分类' not in sfilter and u'报验工区' not in sfilter:
            for mtype in arrTypes:
                for mplace in arrPlaces:
                    sfilter[u'分类'] = mtype
                    sfilter[u'报验工区'] = mplace
                    arr2 = self.get(sfilter.copy())
                    arr1.extend(arr2)
        elif u'分类' in sfilter and u'报验工区' not in sfilter:
            for mplace in arrPlaces:
                sfilter[u'报验工区'] = mplace
                arr2 = self.get(sfilter.copy())
                arr1.extend(arr2)
        elif u'分类' not in sfilter and u'报验工区' in sfilter:
            for mtype in arrTypes:
                sfilter[u'分类'] = mtype
                arr2 = self.get(sfilter.copy())
                arr1.extend(arr2)
        return arr1

    def format(self, cell):
        if cell > 0:
            return "%0.2f" % (cell * 100) + "%"
        return cell

    def getRateInfo(self, res):
        _call = lambda key: self.format(res[key] / float(res[u'小合计']))
        res[u'合格比'] = _call(u'合格')
        res[u'不合格比'] = _call(u'不合格')
        res[u'取消比'] = _call(u'取消')

    def getShipCount(self, shipno='N688', flagType=u'船东', filter0={}):
        res = {}
        res[u'船号'] = shipno
        res[u'分类'] = flagType
        flagType = flagType + u'结论'
        #不计入合格率统计的单子,不在计算合格率的统计范围内容
        def getFilter(filterC):
            filterC.update({"合格率统计":{"$nin":["不计入合格率统计"]}})
            return filterC

        filter1 = {'$or': [{flagType: 'A'}, {flagType: 'B'}]}
        filter1.update(filter0)
        filter1 = getFilter(filter1)
        count1 = self.getCount(shipno, filter1)
        res[u'合格'] = int(float(count1))

        filter2 = {'$or': [{flagType: 'C'}, {flagType: 'D'}]}
        filter2.update(filter0)
        filter2 = getFilter(filter2)
        count2 = self.getCount(shipno, filter2)
        res[u'不合格'] = int(float(count2))

        def getcanel(_type):
            cancel = {flagType: _type}
            cancel.update(filter0)
            cancel = getFilter(cancel)
            count = self.getCount(shipno, cancel)
            return {_type: count}

        ecancel = getcanel("E")
        fcancel = getcanel("F")
        gcancel = getcanel("G")
        hcancel = getcanel("H")

        # filter3 = {'$or':[{flagType:'E'},{flagType:'F'},{flagType:'G'},{flagType:'H'}]}
        # filter3 = {'$or': [{flagType: 'G'}]}

        res.update(ecancel)
        res.update(fcancel)
        res.update(gcancel)
        res.update(hcancel)

        res[u'取消'] = ecancel["E"] + fcancel["F"] +gcancel["G"] + hcancel["H"]
        res[u'合计'] = count1 + count2 + res[u'取消']
        res[u"小合计"] = count1 + count2
        res[u'合格比'] = 0
        res[u'不合格比'] = 0
        res[u'取消比'] = 0

        if res[u'小合计'] != 0:
            self.getRateInfo(res)
        res[u'报验工区'] = filter0.get(u'报验工区', '')
        return res

    def getCount(self, shipno='N688', mfilter={}):
        tableNow, tableNow2 = self.getDB(shipno)
        return tableNow.find(mfilter).count()

    # 导出报验合格率
    def exportExcelRate(self, st1, st2):
        timestamp1 = time.mktime(time.strptime(st1, "%Y-%m-%d")) + 28800
        timestamp2 = time.mktime(time.strptime(st2, "%Y-%m-%d")) + 28800
        sfilter = {u'报验日期2': {'$gte': timestamp1, '$lte': timestamp2}}
        items = self.get2(sfilter)
        return quadailyformexcel.excel_export_rate(st1, st2, items)
        # 导出报验合格率

    def exportExcelRateNew(self, sfilter, st1, st2):
        timestamp1 = time.mktime(time.strptime(st1, "%Y-%m-%d")) + 28800
        timestamp2 = time.mktime(time.strptime(st2, "%Y-%m-%d")) + 28800
        sfilter[u"报验日期2"] = {'$gte': timestamp1, '$lte': timestamp2}

        Logger.dict(sfilter)
        items = self.get2(sfilter)
        return quadailyformexcel.excel_export_rate(st1, st2, items)

    # 导出一次报验合格率
    def exportExcelRateOne(self, st1, st2):
        timestamp1 = time.mktime(time.strptime(st1, "%Y-%m-%d")) + 28800
        timestamp2 = time.mktime(time.strptime(st2, "%Y-%m-%d")) + 28800
        sfilter = {u'报验日期2': {'$gte': timestamp1, '$lte': timestamp2}, u'报验次数': 1}
        items = self.get2(sfilter)
        return quadailyformexcel.excel_export_rateone(st1, st2, items)


if __name__ == '__main__':
    mdb = QuaDailyFormCount()
    # print(mdb.get2({u'分类':u'船东'}))
    #  print(mdb.get(sfilter={"报验日期2":{"$gte":1512086400,"$lte":1512172800},"分类":"船东"}))
    # filter1={u"状态":{"$in":[2,3,4,5]}}
    # mdb.exportExcelAll()
    # obj1 = mdb.get('2017-11-21')
    # print(obj1)
    # mdb.lockParam(mdb.delItem,'BY-N688-HB-003')
    # str1 = '{"报验项目":"测试33","报验专业":"HB"}'
    # obj1 = json.loads(str1)
    # obj2 = mdb.lockParam(mdb.addItem,obj1)
    # print(str(obj2))
