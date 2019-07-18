# -*- coding: utf-8 -*-
import os,sys
import multiprocessing  
import json
import codecs as zcodecs
import twfilehelper
import atexit 

#数列的索引
class ItemIndices():
    def __init__(self, fNa='indices1.txt'):
        self.proj = ''
        self.dir = './data/N688/idx/'
        self.path = self.dir + fNa
        self.lock = multiprocessing.Lock()
        self.dict_id = {}
        self.indices = []
        self.pointer = -1     #当前的行指针 主要用来添加用 还有重新指定 空的序号
        self.reset()
    
    def getRangeIndices(self,sta=0,len1=10):
        end = sta + len1
        lst1 = []
        for i in range(sta, end):
            lst1.append([i,0,0,0,0,0])
        return lst1

    def getRangeIndicesEx(self):
        len1 = len(self.indices)
        if (len1 - self.pointer) <= 5:
            lst1 = self.getRangeIndices(len1)
            self.indices.extend(lst1)
            self.append(lst1)

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

    def findPointer(self,id):
        idx = -1
        if self.indices[id][0] == id:
            return id
        else:
            len1 = len(self.indices)
            for i in range(len1-1,-1,-1):
                item = self.indices[i]
                if item[0] == id:
                    idx = i
                    break
        return idx

    #获得当前游标值
    def getPointer(self):
        return self.pointer

    def nextPointer(self):
        self.pointer += 1
        self.getRangeIndicesEx()
        return self.pointer

    def prePointer(self):
        self.pointer -= 1
        if self.pointer < -1:
            self.pointer = -1
        return self.pointer
 
    def getParam(self,pars,col):
        len1 = len(pars)
        if col < len1:
            return pars[col]
        return 0

    def setParam(self,pars,col,val):
        len1 = len(pars)
        if col >= len1:
            for i in range(len1,col+1):
                pars.append(0)
        pars[col] = val

    #根据id获得当前状态
    def getStatus(self,id,col=0):
        idx = self.findPointer(id)
        if self.pointer >= 0:
            return self.indices[idx][col]
        else:
            return -1

    def getAll(self):
        return self.indices

    def setStatus(self,id,col,val,cb=None,cb2=None):
        pars = []
        idx = self.findPointer(id)
        if idx >= 0:
            pars = self.indices[idx]
            if cb != None:
                if(callable(cb)):
                    if cb(pars,col,val) == True:
                        self.setParam(pars,col,val)
                        self.indices[idx] = pars
            else:
                self.setParam(pars,col,val)
                self.indices[idx] = pars
            if cb2 != None:
                if(callable(cb2)):
                    cb2(pars)
            self.getRangeIndicesEx()
            self.update(idx, pars)
        return pars

    def getParamStr(self,pars):
        str1 = ''
        len2 = len(pars)
        for idx2 in range(0,len2):
            if idx2 == 0:
                str1 = str(pars[0]).rjust(8,'0')
            else:
                str1 = str1 + ","+str(pars[idx2]).rjust(3,'0')
        return str1

    def save(self):
        lst1 = []
        len1 = len(self.indices)
        for idx1 in range(0,len1):
            str1 = self.getParamStr(self.indices[idx1])
            lst1.append(str1)
        twfilehelper.writeList(self.path, lst1,'utf-8')

    def update(self,idx,pars):
        startpos = idx * 30
        str1 = self.getParamStr(self.indices[idx]) + '\r\n'
        twfilehelper.update(self.path,str1,'utf-8',startpos)

    def append(self,lst):
        lst2 = []
        for i in lst:
            lst2.append(self.getParamStr(i))
        twfilehelper.appendList(self.path,lst2,'utf-8')
     
    def reset(self):
        #读取文件
        if os.path.exists(self.path):
            lst1 = twfilehelper.readList(self.path,'utf-8')
            for str1 in lst1:
                lst2 = str1.split(',')
                lst3 = []
                for str2 in lst2:
                    lst3.append(int(str2))
                self.indices.append(lst3)
        else:
            self.indices = self.getRangeIndices()
            self.save()
        self.resetPointer()

    #设置游标
    def resetPointer(self):
        len1 = len(self.indices)
        for idx in range(1,len1):
            pars = self.indices[idx]
            if int(self.getParam(pars,1)) == 0:
                self.pointer = idx
                break

    #获得当前有效的行
    def askValidLine(self):
        sres = []
        while 1:
            pars = self.indices[self.pointer]
            if int(self.getParam(pars,1)) == 0:
                sres = self.setStatus(self.pointer,1,1)
                break
            else:
                self.nextPointer()
        return sres

    def askValidLines(self,count):
        sres = []
        for i in range(0,count,1):
            sarr = self.askValidLine()
            if len(sarr) > 0:
                sres.append(sarr)
        return sres
    #根据id删除某行
    def delOneLine(self,id,cb=None):
        pars = self.setStatus(id,1,0,cb)
        if pars[1] == 0:
            self.resetPointer()
        return pars

    def delMoreLines(self,ids,cb=None):
        sres = []
        for id in ids:
            pars = self.delOneLine(id,cb)
            sres.append(sres)
        return sres

if __name__ == '__main__':
    mdb = ItemIndices()
    sres = mdb.lockParam(mdb.askValidLines,2)
    print(sres)