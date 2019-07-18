# -*- coding: UTF-8 -*-
from excel import ExcelUtil
import os
import ImgConvert

class WriteDaiYong:
    def write(self, sheet, row, col1, row2, col2, value, style=None):
        if not style:
            style = self.excel.font("SimSun", False, 7)
            self.excel.alignLeft(style)
        else:
            self.excel.font("SimSun", False, 7, style)

        self.excel.writeMerge(sheet, row, col1, row2, col2, "%s" % value, style)

    def writeFont1(self, sheet, row, col1, row2, col2, value, style=None):
        if not style:
            style = self.excel.font("Arial Unicode MS", False, 7)
            self.excel.alignLeft(style)
        else:
            self.excel.font("Arial Unicode MS", False, 7, style)

        self.excel.writeMerge(sheet, row, col1, row2, col2, "%s" % value, style)

    def font1(self):
        return self.excel.font("Arial Unicode MS", False, 7);

    def writeImg(self,sheet,sr,sc,img1,img2):
        img1 = "/Users/micometer/Develop/quality_control/templates/"+img1
        img2 = "/Users/micometer/Develop/quality_control/templates/"+img2

        self.excel.insert_bitmap(sheet,img2,sr+1,sc+1,1,0)
        self.excel.insert_bitmap(sheet,img1,sr+1,sc+7,1,0)

    def write14_21(self, sheet, sr, sc, user):
        self.write(sheet, sr + 14, sc + 1, sr + 14, sc + 3, u"中远海运重工焊工等级")
        self.writeFont1(sheet, sr + 15, sc + 1, sr + 15, sc + 3, u"CHI welder’s grade:")
        self.write(sheet, sr + 14, sc + 4, sr + 15, sc + 7, user.get(u"焊工等级", ""))
        self.write(sheet, sr + 14, sc + 8, sr + 14, sc + 14, u"备注Note:")
        self.write(sheet, sr + 14, sc + 8, sr + 14, sc + 14, u"W01：碳钢/碳锰钢和最小屈服强度ReH≤390N/mm2 的低合金高强度钢")
        self.write(sheet, sr + 16, sc + 1, sr + 16, sc + 3, u"发证日期Date of Issue:")
        self.write(sheet, sr + 16, sc + 8, sr + 16, sc + 14, u"W02：CrMo 钢及抗蠕变CrMoV 钢:")

        self.write(sheet, sr + 17, sc + 1, sr + 17, sc + 3, u"发证日期Date of Issue:")
        self.write(sheet, sr + 17, sc + 8, sr + 17, sc + 14, u"W03：最小屈服强度ReH>390N/mm2的高强度钢，以及Ni含量＜5%的镍钢")

        self.write(sheet, sr + 18, sc + 1, sr + 18, sc + 14, u"发证机构：舟山中远海运重工焊工考试委员会")

        self.write(sheet, sr + 18, sc + 8, sr + 18, sc + 14, u"W04：Cr 含量为12%~20% 的铁素体或马氏体不锈钢")

        self.write(sheet, sr + 19, sc + 8, sr + 19, sc + 14, u"W05:Ni 含量≥ 5% 的低温镍钢")
        self.write(sheet, sr + 20, sc + 8, sr + 20, sc + 14, u"W11:奥氏体或双相不锈钢")

        self.write(sheet, sr + 21, sc + 8, sr + 21, sc + 14, u"注：本证书证明离厂无效", self.excel.aligncenter())

        sr21 = u"Issued by： COSCO SHIPPING Heavy Industry(ZhouShan）Qualification Test Committee";
        self.writeFont1(sheet, sr + 19, sc + 1, sr + 21, sc + 7, sr21)


    def getUserImg(self,userImg,user):
        _id = user.get("身份证",None)
        if not _id:
            return None
        path = os.path.dirname(userImg)
        _new = os.path.join(path,"%s.bmp"%_id)
        return _new



    def write7_13(self, sheet, sr, sc, user):
        # 表格信息
        self.write(sheet, sr + 7, sc + 1, sr + 7, sc + 2, u"姓名Name:")
        self.write(sheet, sr + 8, sc + 1, sr + 8, sc + 2, u"性别 Sex:")
        self.write(sheet, sr + 9, sc + 1, sr + 9, sc + 2, u"ID No:")
        self.write(sheet, sr + 10, sc + 1, sr + 10, sc + 3, u"试件形式welding detial:")
        self.write(sheet, sr + 11, sc + 1, sr + 11, sc + 3, u"焊委会登记号REG No.")
        self.write(sheet, sr + 12, sc + 1, sr + 12, sc + 3, u"施工队Construction Team:")
        self.write(sheet, sr + 13, sc + 1, sr + 13, sc + 3, u"所属工区Department:")

        ##数据库信息
        self.write(sheet, sr + 7, sc + 3, sr + 7, sc + 5, user.get(u"姓名", ""))
        self.write(sheet, sr + 8, sc + 3, sr + 8, sc + 5, user.get(u"性别", ""))
        self.write(sheet, sr + 9, sc + 3, sr + 9, sc + 5, user.get(u"身份证", ""))
        self.write(sheet, sr + 10, sc + 4, sr + 10, sc + 5, user.get(u"试件形式", ""))
        self.write(sheet, sr + 11, sc + 4, sr + 11, sc + 5, user.get(u"焊工编号", ""))
        self.write(sheet, sr + 12, sc + 4, sr + 12, sc + 5, user.get(u"施工队", ""))
        self.write(sheet, sr + 13, sc + 4, sr + 13, sc + 5, user.get(u"所属工区", ""))

        ##照片
        self.write(sheet, sr + 7, sc + 6, sr + 13, sc + 7, "")

        imgs = self.getUserImg(user.get(u"照片地址",""),user)
        if imgs:
            # 将图片转换为标准的格式,固定宽度和高度,并写成bmp格式
            ImgConvert.ImageConver.bmp(user.get(u"照片地址",""),imgs,120,400)

        self.excel.insert_bitmap(sheet,imgs, sr + 7, sc + 6, 1, 0)

        self.write(sheet, sr + 7, sc + 8, sr + 7, sc + 10, u"填充金属类型:")
        self.writeFont1(sheet, sr + 8, sc + 8, sr + 8, sc + 10, u"Filler metal type.")
        self.write(sheet, sr + 9, sc + 8, sr + 9, sc + 10, u"母材性质:")
        self.writeFont1(sheet, sr + 10, sc + 8, sr + 10, sc + 10, u"Base Metal Group.:")
        self.write(sheet, sr + 11, sc + 8, sr + 11, sc + 10, u"板厚 Plate thickness:")
        self.write(sheet, sr + 12, sc + 8, sr + 12, sc + 10, u"管厚 Pipe thickness:")
        self.write(sheet, sr + 13, sc + 8, sr + 13, sc + 10, u"管径 Pipe outside Diameter:")

        self.write(sheet, sr + 7, sc + 11, sr + 8, sc + 14, user.get(u"填充金属", ""))
        self.write(sheet, sr + 9, sc + 11, sr + 10, sc + 14, user.get(u"母材性质", ""))
        self.write(sheet, sr + 11, sc + 11, sr + 11, sc + 14, user.get(u"板厚", ""))
        self.write(sheet, sr + 12, sc + 11, sr + 12, sc + 14, user.get(u"管厚", ""))
        self.write(sheet, sr + 13, sc + 11, sr + 13, sc + 14, user.get(u"管径", ""))

    def write2_3(self, sheet, sr, sc, user):
        sr7 = u"兹证明本证书持有人已经通过中国船级社的焊工资格考试，能够从事本证书规定范围内的焊接工作"
        self.write(sheet, sr + 3, sc + 1, sr + 4, sc + 7, sr7)
        sr8 = u"THIS IS TO CERTIFICATY that the bearer has been qualified by the qualification test committee for welders of CCS and is able to undertake welding operation specified in this Certificate.";

        self.writeFont1(sheet, sr + 5, sc + 1, sr + 6, sc + 7, sr8)
        self.excel.rowHeight(sheet,sr+5,8*20)
        self.excel.rowHeight(sheet,sr+6,8*20)

        self.write(sheet, sr + 3, sc + 8, sr + 3, sc + 10, u"焊接方法:")
        self.writeFont1(sheet, sr + 4, sc + 8, sr + 4, sc + 10, u"Welding Process:")

        self.write(sheet, sr + 5, sc + 8, sr + 5, sc + 10, u"焊接位置:")
        self.writeFont1(sheet, sr + 6, sc + 8, sr + 6, sc + 10, u"Welding Position Range:")

        self.write(sheet, sr + 3, sc + 11, sr + 4, sc + 14, user.get(u"焊接方法", ""))
        self.write(sheet, sr + 5, sc + 11, sr + 6, sc + 14, user.get(u"焊接位置", ""))

    def writeH(self, sheet, sr, sc, user):
        style0 = self.excel.aligncenter()
        self.write(sheet, sr + 1, sc + 2, sr + 1, sc + 6, u"焊  工  资  格  证  书", style0)
        self.writeFont1(sheet, sr + 2, sc + 2, sr + 2, sc + 6, u"WELDER QUALIFICATION CERTIFICATE", style0)

        self.write(sheet, sr + 1, sc + 1, sr + 2, sc + 1,"")
        self.write(sheet, sr + 1, sc + 7, sr + 2, sc + 7,"")
        self.write(sheet, sr + 1, sc + 8, sr + 1, sc + 14, u"电焊工认证考试相关参数", style0)
        self.writeFont1(sheet, sr + 2, sc + 8, sr + 2, sc + 14, u"WELDING OPERATOR QUALIFICATION TEST RECORD", style0)

    def writeMain(self, users):
        startRow, startIndex = 0, 0
        maxNumber = len(users) * 4
        index = 0
        pics = getPic()
        for cell in range(0, maxNumber):
            if cell % 2 == 0:
                startRow = (cell / 2) * 57
            elif cell != 0:
                startRow += 30
            self.writeH(0, startRow, startIndex, users[index])
            self.write2_3(0, startRow, startIndex, users[index])
            self.write7_13(0, startRow, startIndex, users[index])
            self.write14_21(0, startRow, startIndex, users[index])
            cellImg = pics.get("replace")[cell % 4]
            self.writeImg(0,startRow,startIndex,pics.get("icon"),cellImg)
            if cell % 4 == 0 and cell !=0:
                index += 1

    def main(self, users, excel=None):
        self.excel = excel or ExcelUtil()
        self.excel.open("/Users/micometer/Develop/quality_control/exceltst/daiyong.xls")
        self.writeMain(users)
        self.excel.colWidth(0, 5.6)
        self.excel.save(file="/Users/micometer/Develop/quality_control/exceltst/daiyongzheng1.xls")

def getPic():
    return {"icon":"0cosco.bmp","replace":["1ccs.bmp","2lr.bmp","3abs.bmp","4dnv.bmp"]}

def test():
    WriteDaiYong().main([{u"姓名": u"张三"}])


if __name__ == "__main__":
    test()
