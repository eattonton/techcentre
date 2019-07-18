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

class QuaDailyFormCount2():
    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1',27017 )
        self.db_dict = {}
        self.mship = ship.Ship()
  
    def html(self,request,stype='',stype2='n'):
        obj1 = {}
        if stype == 'get':
            sfilter1 = request.GET.get('filter1','')
            sfilter2 = request.GET.get('filter2','')
            if sfilter1 != '' and sfilter1 != '':
                mfilter1 = json.loads(sfilter1)
                mfilter2 = json.loads(sfilter2)
                if u'责任工区' not in sfilter1:
                    obj1 = self.get2(mfilter1,mfilter2)
                else:
                    obj1 = self.get(mfilter1,mfilter2)
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
            self.db_dict[shipno].append(self.client[shipno].quatb)
            self.db_dict[shipno].append(self.client[shipno].commenttb)
        return self.db_dict[shipno][0],self.db_dict[shipno][1]

    def get(self,sfilter1={},sfilter2={}):
        if u"船号" in sfilter1:
            shipno = sfilter1.pop(u"船号")
            arr1 = []
            obj1 = self.getShipCount(shipno,sfilter1,sfilter2)
            if obj1[u'意见遗留数'] != 0:
                arr1.append(obj1)
            return arr1
        elif u'船名' in sfilter1:
            shipname = sfilter.pop(u"船名")
            shipdb = ship.Ship()
            shiplst = shipdb.getshipno(shipname)
            arr1 = []
            for shipno in shiplst:
                obj1 = self.getShipCount(shipno,sfilter1,sfilter2)
                if obj1[u'意见遗留数'] != 0:
                    arr1.append(obj1)
            return arr1
        else:
            arr1 = []
            shoparr = self.mship.getshipnolst()
            for shipno in shoparr:
                obj1 = self.getShipCount(shipno,sfilter1,sfilter2)
                if obj1[u'意见遗留数'] != 0:
                    arr1.append(obj1)
            return arr1

    def get2(self,sfilter1={},sfilter2={}):
        arr1 = []
        arrPlaces = [u"分段工区",u"搭载工区",u"机装工区",u"电装工区",u"舾装工区",u"涂装工区","制造工区","技术中心","物资部","质量部"]
        if u'责任工区' not in sfilter1:
            for mplace in arrPlaces:
                sfilter1[u'责任工区'] = mplace
                arr2 = self.get(sfilter1.copy(),sfilter2.copy())
                arr1.extend(arr2)
        else:
            arr2 = self.get(sfilter1.copy(),sfilter2.copy())
            arr1.extend(arr2)
        return arr1

    #获取某条船的意见遗留项
    def getShipCount(self,shipno='N781',sfilter1={},sfilter2={}):
        res = {}
        res[u'船号'] = shipno
        res[u'责任工区'] = sfilter1[u'责任工区']
        res[u'意见遗留数'] = 0
        mcount = self.getCount(shipno,sfilter1,sfilter2)
        if len(mcount) > 0:
            res[u'意见遗留数'] = mcount[0]['count']
        return res
 
    #获取数量
    def getCount(self,shipno='N781',mfilter1={},mfilter2={}):
        tableNow,tableNow2 = self.getDB(shipno)
        mfilter22 = {}
        for k in mfilter2:
            mfilter22['dform.'+k] = mfilter2[k]
        pipeline = []
        pipeline.append({'$match':mfilter1})
        pipeline.append({"$lookup":{"localField":"报验单1","from":"quatb","foreignField":"_id","as":"dform"}})
        pipeline.append({'$match':mfilter22})
        pipeline.append({'$group':{'_id':None,'count':{'$sum':1}}})
        return list(tableNow2.aggregate(pipeline))

    #导出意见遗留项
    def exportExcelUndoOld(self,st1,st2):
        sfilter1 = {"意见状态":{"$in":[1,2]}}
        timestamp1 = time.mktime(time.strptime(st1, "%Y-%m-%d"))+28800
        timestamp2 = time.mktime(time.strptime(st2, "%Y-%m-%d"))+28800
        sfilter2 = {u'报验日期2':{'$gte':timestamp1,'$lte':timestamp2}}
        items = self.get2(sfilter1,sfilter2)
        #return quadailyformexcel.excel_export_rate(st1,st2,items)

    # 导出意见遗留项
    def exportExcelUndo(self, filter):
        query1 = {u"意见状态":{"$in":[1,2]}}
        query2 = {}
        ship = filter.get(u"船号")
        if ship:
            query1[u"船号"] = ship

        checker = filter.get(u"质检员")
        if checker:
            query2[u"质检员"] = checker

        zren = filter.get(u"责任工区")
        if zren:
            query1[u"责任工区"] = zren

        start = filter.get(u"报验日期2",0)
        end = filter.get(u"报验日期21",0)
        if start == 0 and end == 0:
            pass

        if start != 0 and end == 0:
            query2[u"报验日期2"]={"$gte":start}

        if start == 0 and end != 0:
            query2[u"报验日期2"] = {"$lte": end}

        if start !=0 and end != 0:
            query2[u"报验日期2"] = {"$gte": start,"$lte":end}

        items = []
        if u'责任工区' not in query1:
            items = self.get2(query1, query2)
        else:
            items = self.get(query1, query2)
        _file = quadailyformexcel.excel_export_ylx(items)
        return _file

    def exportExcelUndoCount(self,st1):
        filter1 = {"意见状态":{"$in":[1,2]}}
        dt0 = datetime.datetime.strptime(st1, "%Y-%m-%d")
        #span1
        delta1=datetime.timedelta(days=-7)
        dt1 = dt0 + delta1
        sdt1 = dt1.strftime("%Y-%m-%d")
        timestamp1 = time.mktime(dt1.timetuple())+28800
        #span2
        delta2=datetime.timedelta(days=-13)
        dt2 = dt0 + delta2
        sdt2 = dt2.strftime("%Y-%m-%d")
        timestamp2 = time.mktime(dt2.timetuple())+28800
        filter21={"报验日期2":{"$gte":timestamp2,"$lte":timestamp1}}
        #span3
        delta3=datetime.timedelta(days=-14)
        dt3 = dt0 + delta3
        sdt3 = dt3.strftime("%Y-%m-%d")
        timestamp3 = time.mktime(dt3.timetuple())+28800
        #span4
        delta4=datetime.timedelta(days=-29)
        dt4 = dt0 + delta4
        sdt4 = dt4.strftime("%Y-%m-%d")
        timestamp4 = time.mktime(dt4.timetuple())+28800
        filter22={"报验日期2":{"$gte":timestamp4,"$lte":timestamp3}}
        #span5
        delta5=datetime.timedelta(days=-30)
        dt5 = dt0 + delta5
        sdt5 = dt5.strftime("%Y-%m-%d")
        timestamp5 = time.mktime(dt5.timetuple())+28800
        filter23={"报验日期2":{"$lte":timestamp5}}
        items1 = self.get2(filter1.copy(),filter21.copy())
        items2 = self.get2(filter1.copy(),filter22.copy())
        items3 = self.get2(filter1.copy(),filter23.copy())
        return quadailyformexcel.excel_export_ylx_count([sdt1,sdt2,sdt3,sdt4,sdt5],[items1,items2,items3])

if __name__ == '__main__':
    mdb = QuaDailyFormCount2()
    #filter1 = {"意见状态":{"$in":[1,2]}}
    #filter2 = {"船号":"N753"}
    #item = mdb.get2(filter1,filter2)
    dt0 = mdb.exportExcelUndoCount("2018-6-1")
    print(dt0)
