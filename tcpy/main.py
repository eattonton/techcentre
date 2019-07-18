# -*- coding: utf-8 -*-
import os, sys
sys.path.append('./tcpy')
import multiprocessing
import json
import pymongo
import threading
from django.http import HttpResponse, HttpResponseBadRequest
import annotation
import user
import diction
import projectlist
import recorditem

#返回的结果集合
def Result(*args):
    if args is None:
        return None,False
    if isinstance(args[0],(list,tuple)) and len(args[0]) >=2 and isinstance(args[0][1],bool):
            return args[0][0],args[0][1]
    else:
        data = args[0]
        flag=True
    return data,flag

@annotation.cros
@annotation.jsonfy
def html(request, className='',fun1=''):
    if className=='user':
        oUser =user.User()
        return oUser.html(request,fun1)
    elif className=='diction':
        oDict = diction.Diction()
        return oDict.html(request,fun1)
    elif className=='projlist':
        oProjList = projectlist.ProjList()
        return oProjList.html(request,fun1)
    elif className=='recorditem':
        oRecItem = recorditem.RecordItem()
        return oRecItem.html(request,fun1)
    return Result(u"请求方法有误" + fun1, False)

#if __name__ == '__main__':
    #print(useritem2)
