##
#
# @author micometer
# @data 2019/4/4
##
# -*- coding: utf-8 -*-
import os, sys

sys.path.append('../')
import annotation
from base import BaseControl
import weldStaffUserInfoExcel
import json
from PIL import Image
import qrcode
import time
import weldStaffInfoStruct

class WelbStaffUserInfo(BaseControl):
    def __init__(self, uploadDir):
        BaseControl.__init__(self)
        # 焊工信息表
        self.table = self.db.weldUserInfo
        self.uploadDir = "./static/WeldStaffWeb/upload/"
        self.pathProfile = './static/WeldStaffWeb/data/profile/'
        self.pathQR = './static/WeldStaffWeb/data/qr/'

    def html(self, request, stype=''):
        if stype == 'uploadFile':
            return self.uploadFile(request)
        elif stype == 'getCheckImage':
            return self.getCheckImage(request)
        elif stype == "getUserInfo":
            str1 = request.GET.get('user', None) or request.POST.get('user', None)
            return self.getUserInfo(str1)
        elif stype == "uploadExcelFile":
            return self.uploadExcelFile(request)

        return BaseControl.html(self, request, stype)

    def insert(self, item):
        #query = {"身份证": item["身份证"], "船级社": item["船级社"]}
        #items = self.table.find_one(query)
        #if items:
        #    items.update(item)
        #    self.update(items)
        #    return items, True
        return BaseControl.insert(self, item)

    # 获取数据
    @annotation.cros
    @annotation.jsonfy
    def getCheckImage(self, request):
        data = {}
        str1 = request.GET.get('data', None) or request.POST.get('data', None)
        if str1:
            data = json.loads(str1)
        items = self.table.find(data.get("filter", {}))
        items2 = []
        for item in items:
            item["是否上传照片"] = os.path.exists(self.pathProfile + item["身份证"] + '.bmp')
            if item["是否上传照片"]:
                item["照片地址"] = self.pathProfile + item["身份证"] + '.bmp'
            items2.append(item)
        return items2, True

    @annotation.cros
    @annotation.jsonfy
    # 焊工总清单中删除旧数据信息
    def uploadExcelFile(self, request):
        ofile = request.FILES.get("file", None)
        self.removeFile('./upload/', ofile.name)
        isOk, sPath = self.saveFile(ofile, './upload/', ofile.name)
        if isOk:
            mlist = weldStaffUserInfoExcel.excel_table_byindex(sPath, 1)
            mlist2 = weldStaffInfoStruct.GetWeldStaffInfo1(mlist)
            for mitem in mlist2:
                self.insert(mitem)
            return 1, True
        else:
            return 0,False

    @annotation.cros
    @annotation.jsonfy
    def uploadFile(self, request):
        id = request.POST.get('_id', None)
        file = request.FILES.get("file", None)
        targetName = request.POST.get("targetName", None)
        orgName = request.POST.get("orgName", None)
        if not id or not file or not targetName or not orgName:
            return "参数错误", False

        user = self.table.find_one({"_id": int(id)})
        if not user:
            return "用户不存在", False

        def saveUser(_path):
            setDict = {"file_src": _path}
            setDict[orgName] = file.name
            setDict[targetName] = _path
            setDict["_id"] = int(id)
            return self.update(setDict)

        user[orgName] = file.name
        filename = user["身份证"] + targetName + "." + file.name.split(".")[-1]
        isOk, _path = self.saveFile(file, self.uploadDir, filename)
        if not isOk:
            self.removeFile(self.uploadDir, filename)
        else:
            return saveUser(_path)

        isOk, _path = self.saveFile(file, self.uploadDir, filename)
        if not isOk:
            return _path, isOk

        return saveUser(_path)

    # 上传身份证
    # 如果上传的照片的名称不是身份证号码,如果区分
    def uploadFiles(self, request):
        uploadCards = []
        if request.method == "POST":
            ofiles = request.FILES.getlist("file")
            for of in ofiles:
                fpath = './WeldStaffPy/upload/' + of.name
                destination = open(fpath, 'wb+')  # 打开特定的文件进行二进制的写操作
                for chunk in of.chunks():  # 分块写入文件
                    destination.write(chunk)
                destination.close()
                # 身份证照片
                im = Image.open(fpath)
                imgs = im.convert("RGB")
                out = imgs.resize((76, 102), Image.ANTIALIAS)
                target = self.pathProfile + os.path.splitext(of.name)[0] + ".bmp"
                uploadCards.append({"id": os.path.splitext(of.name)[0], "path": target})
                out.save(target)
        return {"state": True, "data": uploadCards}

    def exportExcelCSS(self, sid):
        # items = []
        ssids2 = sid.split(',')
        # num1 = len(ssids2)
        itemIds = [int(cell) for cell in ssids2 if int(cell) != 0]
        items = [cell for cell in self.table.find({"_id": {"$in": itemIds}})]
        # dowloadOkIds = []
        # for idx in range(0, num1):
        #     ssid2 = int(ssids2[idx])
        #     if ssid2 != 0:
        #         obj2 = self.table.find_one({'_id': ssid2})
        #         dowloadOkIds.append(ssid2)
        #         items.append(obj2)
        self.table.update({"_id": {"$in": itemIds}}, {"$set": {"导出状态": "已导出", "导出时间": time.localtime()}}, multi=True)
        return weldStaffUserInfoExcel.excel_css(items)

    def getPic(self, data):
        table = self.db.WSExamRecordtb
        cells = [cell["考试批次"] for cell in table.find({"hasImport": {"$exists": False}})]

    def exportExcelDaiyong(self, sid):
        items = []
        ssids2 = sid.split(',')
        num1 = len(ssids2)
        for idx in range(0, num1):
            ssid2 = int(ssids2[idx])
            if ssid2 != 0:
                obj2 = self.table.find_one({'_id': ssid2})
                items.append(obj2)
        return weldStaffUserInfoExcel.export_daiyong(items)

    def exportExcelQR(self, sid):
        items = []
        ssids2 = sid.split(',')
        num1 = len(ssids2)
        for idx in range(0, num1):
            ssid2 = int(ssids2[idx])
            if ssid2 != 0:
                obj2 = self.table.find_one({'_id': ssid2})
                obj2["QR"] = self.createQR(obj2)
                items.append(obj2)
        return weldStaffUserInfoExcel.export_qr(items)

    def createQR(self, item):
        sPath1 = self.pathQR + item["身份证"] + '.bmp'
        if os.path.exists(sPath1) == False:
            #img = qrcode.make('http://220.189.200.12:8002/webapp/info.html?user=' + item["身份证"])
            img = qrcode.make('http://zsqua.triweb.cn:8002/webapp/info.html?user=' + item["身份证"])
            imgs = img.convert("RGB")
            out = imgs.resize((120, 120), Image.ANTIALIAS)
            out.save(sPath1)
        return sPath1

    def getPic(self, data):
        table = self.db.WSExamUsertb
        picHasSet = self.db.picHasSet
        cells1 = [cell["name"] for cell in picHasSet.find()]
        cells = [cell.get("考试批次") for cell in table.find({"考试批次": {"$nin": cells1}}) if cell["考试批次"]]
        return cells, True

    def importUser(self, data):
        def insert(one):
            one["createState"] = one["考试批次"]
            self.insert(one)

        def filterUser(user):
            value = user.get("结果", "不合格")
            return "合格" == value

        users = self.db.WSExamtb.find(data)
        [insert(cell) for cell in users if filterUser(cell)]
        self.db.WSExamRecordtb.update(data, {"$set": {"hasImport": "是"}})
        return "导入数据成功", True

    def insertUserByImport(self, user):
        """
        将考试合格的人员导入到焊工管理-信息录入模块
        此时设置焊工的状态信息为未录入全 数据信息
        :param user:
        :return:
        """
        # user["createState"] = user["考试批次"]
        user["发布"] = True
        user["createState"] = "自动创建"
        self.db.WSExamtb.update({"_id": user["_id"]}, {"$set": {"发布": True}})
        return self.insert(user)
        [insert(cell) for cell in self.db.WSExamUsertb.find(data) if filterUser(cell)]
        insertF = [{"name": cell} for cell in data.get("考试批次").get("$in")]
        self.db.picHasSet.insert(insertF)
        return "导入数据成功", True

    @annotation.cros
    @annotation.jsonfy
    def getUserInfo(self, data):
        user, flag = self.get({"filter": {"身份证": data}})
        for item in user:
            item["是否上传照片"] = os.path.exists(self.pathProfile + item["身份证"] + '.bmp')
            if item["是否上传照片"]:
                item["照片地址"] = self.pathProfile + item["身份证"] + '.bmp'
        return user, flag

    def downloadPdf(self, request):
        sid = request.POST.get("id")
        user = self.table.find_one({"_id": int(sid)})
        if user:
            return user["PDF_file"]
        return None


if __name__ == '__main__':
    mWeldStaffInfo = WelbStaffUserInfo("")
    mWeldStaffInfo.exportExcelCSS("1")
