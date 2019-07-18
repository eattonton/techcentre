# -*- coding: utf-8 -*-
import os,sys
import json
import codecs
import datetime
import time

def GetWeldStaffInfo1(mlist):
    mlist2 = []
    dict0 = LoadConfigJson()
    for mitem in mlist:
        if len(mitem) > 18:
            if mitem[3] != "":
                mitem2 = {}
                mitem2[u"姓名"]=mitem[1]
                mitem2[u"性别"]=mitem[2]
                mitem2[u"身份证"]=mitem[3]
                mitem2[u"工区"]=mitem[4]
                mitem2[u"施工队"]=mitem[5]
                mitem2[u"船级社"]=mitem[6]
                mitem2[u"焊工编号"]=mitem[7]
                mitem2[u"焊接方法1"]=mitem[8]
                mitem2[u"焊接方法2"]=GetWeldMethod2(mitem[8],dict0)
                mitem2[u"合格位置"]=mitem[9]
                mitem2[u"可焊位置"]=mitem[10]
                mitem2[u"母材性质"]=mitem[11]
                mitem2[u"板厚"]=mitem[12]
                mitem2[u"管厚"]=mitem[13]
                mitem2[u"管径"]=mitem[14]
                mitem2[u"试件形式"]=mitem[15]
                mitem2[u"接头形式"]=mitem[16]
                mitem2[u"代用证到期"]=GetDay2(mitem[17])
                mitem2[u"代用证日期"]=GetDay1(mitem[17])
                mitem2[u"船级社证书号"]=mitem[18]
                mitem2[u"在厂状态"]="在厂"
                mitem2[u"createStatus"]="手工创建"
                mitem2[u"未录入全"]="未录入完整"
                mitem2[u"填充金属"]=GetWeldMaterialFromWeld2(mitem2[u"焊接方法2"],dict0)
                mlist2.append(mitem2)
    return mlist2

def GetDay2(strDay2):
    strDay2 = strDay2.replace('.','-')
    day2 = datetime.datetime.strptime(strDay2, "%Y-%m-%d")
    return day2.strftime("%Y-%m-%d")

def GetDay1(strDay2):
    strDay2 = strDay2.replace('.','-')
    day2 = datetime.datetime.strptime(strDay2, "%Y-%m-%d")
    day1 = datetime.datetime(year=day2.year-3, month=day2.month, day=day2.day)
    return day1.strftime("%Y-%m-%d")

def GetWeldMethod2(weld1,dict0):
    arr1 = dict0.get('焊接方法',[])
    for mitem in arr1:
        if mitem["1"] == weld1:
            return mitem["2"]
    return ""

def GetWeldMaterialFromWeld2(weld2,dict0):
    arr1 = dict0.get('填充金属',[])
    for mitem in arr1:
        if mitem["2"] == weld2:
            return mitem["1"]
    return ""

def LoadConfigJson():
    sdata = read("./WeldStaffPy/config/weldstaffconfig.json")
    sdata = sdata.replace('\ufeff','').replace('\r\n','')
    objRes = json.loads(sdata)
    return objRes

def read(fNa, fileCode='utf-8'):
    try:  
        with codecs.open(fNa,'r',fileCode) as f:
            return f.read()
    except:
        return ''

# 1.把datetime转成字符串
def datetime_toString(dt):
    print("1.把datetime转成字符串: ", dt.strftime("%Y-%m-%d"))

# 2.把字符串转成datetime
def string_toDatetime(st):
    st = st.replace('.','-')
    day2 = datetime.datetime.strptime(st, "%Y-%m-%d")
    #delta = datetime.timedelta(days=365*3)
    day1 = datetime.datetime(year=day2.year-3, month=day2.month, day=day2.day)
    print("2.把字符串转成datetime: ", day1)

if __name__ == '__main__':
    string_toDatetime("2020.05.30")