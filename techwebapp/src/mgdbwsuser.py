# -*- coding: utf-8 -*-
import os
from techwebapp.src.base import BaseControl, Result
from techwebapp.src import annotation
from utils.excel import ExcelUtil


class MgdbUser(BaseControl):
    #
    # _dbUtil 数据库连接
    #
    def __init__(self, _dbUtil):
        BaseControl.__init__(self, _dbUtil)
        self.table = self.db.usertb
        self.uploadDir = "./static/SourceWeb/upload/"
        self.downloadDir = "./static/SourceWeb/download/"
        self.templateDir = "./static/SourceWeb/template/"

    def html(self, request, stype=''):
        if stype == "uploadExcelFile":
            return self.uploadExcelFile(request)
        return BaseControl.html(self, request, stype=stype)

    def get(self, query):
        if "filter" not in query:
            query["filter"] = {}
        query["filter"]["_state_"] = "激活"
        return BaseControl.get(self, query)

    def getPager(self, query):
        if "filter" not in query:
            query["filter"] = {}
        query["filter"]["_state"] = "激活"
        return BaseControl.getPager(self, query)

    def insert(self, item):
        item["_state_"] = "激活"
        return BaseControl.insert(self, item)

    def delete(self, item):
        item["_state_"] = "冻结"
        return self.update(item)

    def _checkUniqu(self, item):
        name = item["英文名"]
        user = self.table.find_one({"英文名": name, '_state_': "激活"})
        if not user:
            return Result.true("")
        if user.get("_id", None) == item.get("_id", None):
            return Result.true("")
        return Result.false("英文名%s已经被使用" % item["英文名"])

    def find(self, item):
        name = item.get('name', None)
        password = item.get('pass', None)
        if not (name and password):
            return Result.false("用户名和密码不能为空")

        user = self.table.find_one({"英文名": name, "_state_": "激活"})
        if not user:
            return Result.false("用户名不存在")

        if user["密码"] != password:
            return Result.false("密码不正确")

        return Result.true(user)

    @annotation.cros
    @annotation.jsonfy
    def uploadExcelFile(self, request):
        """
        上传excel文件,导入用户信息
        :param request:
        :return:
        """
        file = request.FILES.get("excel_file", None)
        if not file:
            return Result.false("请选择需要导入的文件")
        _file = os.path.join(self.uploadDir, file.name);
        if os.path.exists(_file):
            os.remove(_file)
        result = self.saveFile(file, self.uploadDir, file.name)
        if not result.isOk():
            return Result.false("上传文件失败")

        def transform(cell):
            return {
                "部门": cell[0],
                "姓名": cell[1],
                "英文名": cell[2],
                "职务": cell[3],
                "专业": cell[4],
                "密码": cell[5],
                "权限": cell[6],
                "手机长号": cell[7],
                "手机短号": cell[8],
                "备注": cell[9],
                "_state_": "激活"
            }

        def readExcel(_path):
            _excel = ExcelUtil()
            _datas = _excel.get_byindex_object(file=_path)
            [self.insert(transform(data)) for data in _datas]
            return Result.true(_datas)

        return readExcel(result.data)


if __name__ == '__main__':
    mdb = mgdbUser()
    # res = mdb.get({'英文名': 'lezhoutong'})
    res = mdb.get({'职务': {'$in': ['检验员', '项目主管', '管理员']}})
    print(res)
