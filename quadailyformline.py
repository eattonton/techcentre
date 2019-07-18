# -*- coding: utf-8 -*-
import os,sys
import json
import datetime
import time
import twfilehelper
import mgdbuser

confObj = None
confUser = mgdbuser.mgdbUser()
#对传入的时间字符进行处理
def fun_date(str1='2017/1/02'):
    t = None
    str1 = str1.replace(' ','').replace('.','-').replace('/','-').replace('\\','-')
    if str1.find('-') > 0:
        t = time.strptime(str1, "%Y-%m-%d")
    else:
        t = time.strptime(str1, "%Y%m%d")
    if t != None:
        return time.strftime("%Y-%m-%d", t)
    return ''

def fun_time(str1):
    return str1.replace(' ','')

def loadConfig():
    global confObj
    path = r'./static/quality/dailyformconfig.json'
    confObj = twfilehelper.readJson(path)
    #print(confObj)
    #str1 = twfilehelper.read(path,'utf_16')
    #print(str1)

def fun_CheckPlace(strIn=''):
    global confObj
    if confObj == None:
        loadConfig()
    params = confObj[u'报验地点']
    strIn = strIn.replace(' ','').replace('\r','').replace('\n','')
    if strIn != '':
        for param in params:
            param2 = param.replace(' ','')
            if strIn == param2:
                return param
    return ''

def fun_CheckDepartment(strIn=''):
    global confObj
    if confObj == None:
        loadConfig()
    params = confObj[u'报验工区']
    strIn = strIn.replace(' ','')
    if strIn != '':
        for param in params:
            if param.find(strIn) >= 0:
                return param
    return ''

def fun_CheckDepartment2(strIn=''):
    global confObj
    if confObj == None:
        loadConfig()
    params = confObj[u'责任工区']
    strIn = strIn.replace(' ','')
    if strIn != '':
        for param in params:
            if param.find(strIn) >= 0:
                return param
    return ''

def fun_CheckChecker(strIn=''):
    strIn = strIn.replace(' ','')
    sres = confUser.findName2(strIn)
    if sres == 0:
        return ''
    else:
        return sres.get(u'英文名','')

if __name__ == '__main__':
    #str1 = fun_CheckChecker('lezhoutong')
    #print(str1)
    #fun_CheckPlace()
    loadConfig()
    #print(confObj)

