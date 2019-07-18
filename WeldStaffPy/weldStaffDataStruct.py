# -*- coding: utf-8 -*-
def GetWeldStaffStatus1(mlist):
    mlist2 = []
    for mitem in mlist:
        if len(mitem) >= 13:
            if mitem[2] != "":
                mitem2 = {}
                mitem2[u"姓名"]=mitem[1]
                mitem2[u"身份证"]=mitem[2]
                mitem2[u"性别"]=mitem[3]
                mitem2[u"考试位置"]=mitem[4]
                mitem2[u"工区"]=mitem[5]
                mitem2[u"施工队"]=mitem[6]
                mitem2[u"焊接方法1"]=mitem[7]
                mitem2[u"焊接方法2"]=mitem[8]
                mitem2[u"试件形式"]=mitem[9]
                mitem2[u"板厚"]=mitem[10]
                mitem2[u"管壁厚度"]=mitem[11]
                mitem2[u"管子外径"]=mitem[12]
                mlist2.append(mitem2)
    return mlist2

def GetWeldStaffStatus2(mlist):
    mlist2 = []
    for mitem in mlist:
        if len(mitem) >= 9:
            if mitem[1] != "":
                mitem2 = {}
                mitem2[u"姓名"]=mitem[0]
                mitem2[u"身份证"]=mitem[1]
                mitem2[u"性别"]=mitem[2]
                mitem2[u"船级社"]=mitem[3]
                mitem2[u"考试位置"]=mitem[4]
                mitem2[u"工区"]=mitem[5]
                mitem2[u"施工队"]=mitem[6]
                mitem2[u"焊接方法1"]=mitem[7]
                mitem2[u"焊接方法2"]=mitem[8]
                mlist2.append(mitem2)
    return mlist2