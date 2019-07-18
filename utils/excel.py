# -*- coding: utf-8 -*-
import os
import xlrd
import xlwt
from xlutils.copy import copy
from copy import deepcopy
# from logger import Logger

class ExcelUtil:
    def __init__(self):
        self._file = None
        self.workbook = None

    def open(self, file=None):
        try:
            self._file = file
            if self._file:
                self.workbook = xlrd.open_workbook(self._file, formatting_info=True)
            else:
                self.workbook = xlwt.Workbook()
                self.workbook.add_sheet("sheet")
            return True
        except Exception as e:
            print(e)
            # Logger.error(str(e))

        return False

    def one_row(self, table, rowindex, callback):
        callback(table.row_values(rowindex))

    def get_byindex(self, file='file.xls', colnameindex=0, by_index=0):
        if not self.open(file):
            return []

        table = self.workbook.sheets()[by_index]
        table.set_header_str(''.encode())
        table.set_footer_str(''.encode())
        ncols = table.ncols
        nrows = table.nrows

        def get_one_line(rows):
            return ",".join([str(rows[i]) for i in range(ncols)])

        return [self.one_row(table, _r, get_one_line) for _r in range(colnameindex + 1, nrows)]

    def get_byname(self, file='file.xls', colnameindex=0, by_name=u'Sheet1'):
        if not self.open(file):
            return

        table = self.workbook.sheet_by_name(by_name)
        nrows = table.nrows  # 行数
        colnames = table.row_values(colnameindex)

        def get_one_line(row):
            return dict([(v, row[i]) for i, v in range(enumerate(colnames))])

        return [get_one_line(table.row_values(rowindex)) for rowindex in range(1, nrows)]

    def aligncenter(self, style=None):
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER
        alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT
        style0 = style or xlwt.XFStyle()
        style0.alignment = alignment
        return style0

    def alignLeft(self, style=None):
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_LEFT
        alignment.vert = xlwt.Alignment.VERT_CENTER
        alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT
        style0 = style or xlwt.XFStyle()
        style0.alignment = alignment
        return style0

    def alignRight(self, style=None):
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        alignment.vert = xlwt.Alignment.VERT_CENTER
        alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT
        style0 = style or xlwt.XFStyle()
        style0.alignment = alignment
        return style0

    def border(self, style):
        style0 = style or xlwt.XFStyle()
        borders = xlwt.Borders()
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        style0.borders = borders
        return style0

    def font(self, name, bold=False,style=None,size=9):
        font0 = xlwt.Font()
        font0.name = name
        font0.bold = bold
        font0.height = size * 20
        style = style or xlwt.XFStyle()
        style.font = font0
        return style

    def colWidth(self,sheetName,width,colmax=50):
        sheet = self.workbook.get_sheet(sheetName)
        for index in range(colmax):
            sheet.col(index).width = int(width * 256)

    def rowHeight(self,sheetName,rowIndex,height):
        style = xlwt.easyxf("font:height %s"%height)
        sheet = self.workbook.get_sheet(sheetName)
        row = sheet.row(rowIndex)
        row.set_style(style)

    def copy(self):
        return copy(self.workbook)

    def copy_sheet(self, excel, name, index):
        ws = excel.get_sheet(index)
        ws.set_header_str(''.encode())
        ws.set_footer_str(''.encode())
        ws2 = deepcopy(ws)
        ws2.set_name(name)
        excel._Workbook__worksheets.append(ws2)

    def active(self, index=0, excel=None):
        excel = excel or self.workbook
        excel.set_active_sheet(index)

    def save(self, excel=None, file=None):
        excel = excel or self.workbook
        if file:
            excel.save(file)
        else:
            excel.save()

    def parse_cell(self, excel, table, row, col):
        ctype = table.cell(row, row).ctype  # 表格的数据类型
        cell = table.cell_value(row, col)

        def excel_datetime_str(arr, fmt):
            sres = ''
            if len(arr) >= 6:
                if fmt == 'h:mm':
                    return '%d:%02d' % (arr[3], arr[4])
            return sres

        def parse_date():
            xfx = table.cell_xf_index(row, col)
            xf = excel.xf_list[xfx]
            fmt = excel.format_map[xf.format_key].format_str
            return excel_datetime_str(xlrd.xldate_as_tuple(cell, 0), fmt)

        def parse_bool(cell):
            return True if cell == 1 else False

        if ctype == 2 and cell % 1 == 0:  # 如果是整形
            cell = int(cell)
        elif ctype == 3:
            cell = parse_date()
        elif ctype == 4:
            cell = parse_bool(cell)
            cell = True if cell == 1 else False
        return cell

    def insert_bitmap(self, sheet,img, x, y, x1, y1, scale_x=1,scale_y=1):
        if img and os.path.exists(img):
            _sheet = self.workbook.get_sheet(sheet)
            _sheet.insert_bitmap(img,x,y,x1,y1,scale_x,scale_y)
        else:
            print (img,"不存在")

    def setCell(self,sheet,row,col,value,style=None):
        self.workbook.get_sheet(sheet).write(row,col,value,style)

    def writeMerge(self,sheet,row,col,row1,col1,value,style=None):
        self.workbook.get_sheet(sheet).write_merge(row,row1,col,col1,value,style)

def main3():
    fna1 = './exceltst/产品质量报验单模板.xls'
    fna2 = './exceltst/1.xls'
    fna3 = './exceltst/2.xls'
    # 打开想要更改的excel文件
    old_excel = xlrd.open_workbook(fna1, formatting_info=True)
    # 将操作文件对象拷贝，变成可写的workbook对象
    new_excel = copy(old_excel)
    # 获得第一个sheet的对象
    ws = new_excel.get_sheet(0)
    # 写入数据
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    alignment.vert = xlwt.Alignment.VERT_CENTER
    # Create Borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    style0 = xlwt.XFStyle()
    style0.alignment = alignment
    style0.borders = borders
    ws2 = deepcopy(ws)
    ws2.set_name('Sheet2')
    new_excel._Workbook__worksheets.append(ws2)
    ws2 = new_excel.get_sheet(1)
    ws3 = deepcopy(ws)
    ws3.set_name('Sheet3')
    new_excel._Workbook__worksheets.append(ws3)
    # 另存为excel文件，并将文件命名
    new_excel.save(fna2)
    # 重新打开
    old_excel2 = xlrd.open_workbook(fna2, formatting_info=True)
    # 将操作文件对象拷贝，变成可写的workbook对象
    new_excel2 = copy(old_excel2)

    ws20 = new_excel2.get_sheet(0)
    ws20.write(1, 6, '编号', style0)
    ws20.write(2, 6, '报验日期', style0)

    ws21 = new_excel2.get_sheet(1)
    ws21.write(1, 6, '编号2', style0)
    ws21.write(2, 6, '报验日期2', style0)

    ws22 = new_excel2.get_sheet(2)
    ws22.write(1, 6, '编号3', style0)
    ws22.write(2, 6, '报验日期3', style0)
    new_excel2.set_active_sheet(0)
    new_excel2.save(fna3)
    os.remove(fna2)
    # ws = wb.get_sheet(0)
    # wb.save()
    # w = copy('./templates/产品质量报验单模板.xls')
    # w.save('./data/N688/download/1.xls')
    print('3')

def test1():
    _excel  = ExcelUtil()
    _excel.open()
    _excel.copy_sheet("template1","template")
    _excel.save(file="/Users/micometer/Develop/quality_control/exceltst/daiyongzheng1.xls")

if __name__ == '__main__':
    ##main()
    test1()
