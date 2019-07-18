# -*- coding: utf-8 -*-
import json
import time
import pymongo
import weldstaffexcel
import weldStaffDataStruct
import weldStaffuser
import weldStaffRecordmgdb
#from utils.charSearch import multi_get_letter
from base import BaseControl, Result

#
# 焊工考试管理
#
class MgdbWeldStaff(BaseControl):
    def __init__(self):
        BaseControl.__init__(self)
        self.table = self.db.WSExamtb
        self.dbUser = weldStaffuser.WeldStaffUser()
        self.dbRecord = weldStaffRecordmgdb.mgdbWeldStaffRecord()

    # 获取焊工考试的参加率和合格率
    def searchRate(self, sfilter={}):
        items = self.table.find(sfilter).sort("_id", pymongo.ASCENDING)
        dataMap = {}

        def set(one, concontainer):
            result = one.get(u"结果", None)
            if result is not None:
                concontainer[u"参加人数"] += 1
                if result == u"合格":
                    concontainer[u"合格人数"] += 1
            concontainer[u"预约人数"] += 1

        for cell in items:
            key = cell[u"考试批次"]
            if not dataMap.has_key(key):
                dataMap[key] = {u"合格人数": 0, u"参加人数": 0,
                                u"预约人数": 0, u"考试批次": key,
                                u"考试时间": cell[u"考试时间"],
                                u"所属工区": cell[u"所属工区"]}
            set(cell, dataMap[key])
        return Result(dataMap.values())

    # 获取系统的考试批次信息
    def getLevel(self, sfilter={}):
        return [cell for cell in self.table.distinct("考试批次", sfilter)]

    def _one(self, item):
        if item.get('_id', 0) == 0:
            if u'status' not in item:
                item["status"] = 0
            if u'date1' not in item:
                item['date1'] = time.strftime("%Y-%m-%d", time.localtime())
                item['date2'] = time.strftime("%H:%M:%S", time.localtime())

            item['_id'] = self.getTableId(self.table) + 1
            weldid = item['_id']
            useritem = {}
            useritem[u"姓名"] = item[u"姓名"]
            useritem[u"身份证"] = item[u"身份证"]
            useritem[u"性别"] = item[u"性别"]
            useritem[u"电话"] = ""
            useritem[u"地址"] = ""
            useritem[u"焊接考试"] = [weldid]
            #useritem[u"nameCode"] = multi_get_letter(item[u"姓名"])
            #item["nameCode"] = multi_get_letter(item[u"姓名"])
        else:
            useritem = None

        return item, useritem

    def insert(self, item):
        item, useritem = self._one(item)
        if useritem is not None:
            self.table.insert_one(item)
            self.dbUser.insertUser(useritem)
        return Result(item)

    # 批量插入焊工信息,主要用于从模板导入数据
    def insertBath(self, items):
        useritems = []
        titems = []
        for item in items:
            _, useritem = self._one(item)
            if useritem:
                useritems.append(useritem)
                titems.append(item)

        def _insert():
            self.db.insert(titems)
            self.dbUser.insert(useritems)

        self.lockCall(_insert, titems)
        return Result(titems)

    def update(self, item):
        sid = item['_id']
        tableNow = self.table
        obj1 = tableNow.find_one({'_id': sid})
        #item["nameCode"] = multi_get_letter(item[u"姓名"])
        if obj1 is not None:
            tableNow.update({'_id': sid}, {'$set': item}, multi=False)
            return Result(tableNow.find_one({'_id': sid}))
        return Result(obj1)

    #考试预约
    def bookdate(self, item):
        sid = item['_id']
        obj1 = self.table.find_one({'_id': sid})
        if obj1 is not None:
            self.table.update({'_id': sid}, {'$set': item}, multi=False)
            #record bookseq
            self.dbRecord.recorddate(item)
            return Result(self.table.find_one({'_id': sid}))
        return Result(obj1)

    #取消预约
    def deldate(self, item):
        sid = item['_id']
        obj1 = self.table.find_one({'_id': sid})
        if obj1 is not None:
            self.table.update({'_id': sid}, {'$set': item}, multi=False)
            #record bookseq
            self.dbRecord.canceldate(item)
            return Result(self.table.find_one({'_id': sid}))
        return Result(obj1)

    def remove(self, item):
        item['status'] = -1
        self.dbUser.removeWeldTest(item)
        return self.update(item)

    def clear(self):
        self.table.remove({})

    def importExcel(self, fpath='', uuser=''):
        mlist = weldstaffexcel.excel_table_byindex(fpath, 1)
        mlist2 = weldStaffDataStruct.GetWeldStaffStatus2(mlist)
        self.insertListStatus0(mlist2, uuser)
        errlstTot = []
        return {"datas": mlist2, "errors": errlstTot}

    def insertListStatus0(self, mlist, uuser=''):
        for mitem in mlist:
            mitem["status"] = 0
            mitem[u"登记人"] = uuser
            mitem['date1'] = time.strftime("%Y-%m-%d", time.localtime())
            mitem['date2'] = time.strftime("%H:%M:%S", time.localtime())
            self.insert(mitem)

    def lockinsertListStatus0(self, mlist):
        return self.lockCall(self.insertListStatus0, mlist)

    def setOne(self, user, uuser, fpath):
        user[u"登记人"] = uuser
        user['imgdate1'] = time.strftime("%Y-%m-%d", time.localtime())
        user['imgdate1'] = time.strftime("%H:%M:%S", time.localtime())
        user[u"照片"] = fpath

    # 上传单个人的照片数据
    def importImg(self, fpath="", uuser="", target=[]):
        users = []
        if len(target) <= 0:
            return {"state": True, "data": [{u"照片": fpath}]}

    def updateUserImg(self,users,uuser,fpath,updateUserImg,target=[]):
        for user in self.db.find({"身份证": {"$in": target}}):
            self.setOne(user, uuser, fpath), self.update(user), users.append(user)
        self.lockCall(updateUserImg)
        return {"state": True, "data": users}

    # 通过照片压缩包上传考试人员的照片数据,照片的格式问 身份证号码.照片类型
    def importImgZip(self, fpath="", uuser=""):
        import zipfile
        zipfile.extractall(fpath)

        shens = []
        names = {}
        users = []

        for name in zipfile.namelist():
            _names = name.split("/")[1].split(".")
            shens.push(_names[0])
            names[_names[0]] = fpath + "/" + name

        for user in self.db.find({"身份证": {"$in": shens}}):
            self.setOne(user, uuser, names[user["u身份证"]]), \
            self.update(user), \
            users.append(user)

        return {"state": True, "data": users}

    #获取考试批次
    def getrecord(self,item):
        if "filter" in item:
            return Result(self.dbRecord.get(item["filter"]))
        else:
            return Result(self.dbRecord.get())


