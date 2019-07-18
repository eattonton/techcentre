# -*- coding: utf-8 -*-
import os, sys
sys.path.append('../')
import xlrd
import xlwt
from utils.excel import ExcelUtil

def open_excel(file='file.xls'):
    try:
        data = xlrd.open_workbook(file, formatting_info=True)
        return data
    except Exception as e:
        print(str(e))

def excel_datetime_str(arr, fmt):
    sres = ''
    if len(arr) >= 6:
        if fmt == 'h:mm':
            return '%d:%02d' % (arr[3], arr[4])
    return sres

def excel_test():
    templ = u'./templates/1.xls'
    mWBook = open_excel(templ)
    print(mWBook.datemode)

def excel_table_byindex(file='file.xls', startrow=0, by_index=0):
    data = open_excel(file)
    table = data.sheets()[by_index]
    nrows = table.nrows  # 行数
    ncols = table.ncols  # 列数
    mlist = []
    for i in range(startrow, nrows):
        arr1 = []
        for j in range(ncols):
            ctype = table.cell(i, j).ctype  # 表格的数据类型
            cell = table.cell_value(i, j)
            if ctype == 2 and cell % 1 == 0:  # 如果是整形
                cell = int(cell)
            elif ctype == 3:
                # 转成datetime对象
                xfx = table.cell_xf_index(i, j)
                xf = data.xf_list[xfx]
                fmt = data.format_map[xf.format_key].format_str
                cell = excel_datetime_str(xlrd.xldate_as_tuple(cell, 0), fmt)
            elif ctype == 4:
                cell = True if cell == 1 else False
            else:
                cell = cell.strip()
            arr1.append(cell)
        mlist.append(arr1)
    return mlist

# css申请表
def excel_css(items):
    templ = u'./WeldStaffPy/templates/css_template.xls'
    xlsFile = u'./WeldStaffPy/download/css_upload.xls'
    _ExcelUtil = ExcelUtil()
    if not _ExcelUtil.open(templ):
        return
    # 将操作文件对象拷贝，变成可写的workbook对象
    new_excel = _ExcelUtil.copy()
    # 获得第一个sheet的对象  
    ws = new_excel.get_sheet(0)
    ws.set_header_str(''.encode())
    ws.set_footer_str(''.encode())
    style0 = getStyle1()
    startRow = 1
    startCol = 0
    irow = startRow
    count = len(items)
    for i in range(count):
        item = items[i]
        ws.write(irow, startCol, item.get("证书类型",""), style0)  
        ws.write(irow, startCol+1, item.get("焊工编号",""), style0)  
        ws.write(irow, startCol+2, item.get("姓名",""), style0)  
        ws.write(irow, startCol+3, item.get("身份证",""), style0)  
        ws.write(irow, startCol+4, item.get("性别",""), style0)  
        ws.write(irow, startCol+5, item.get("工厂名称",""), style0)  
        ws.write(irow, startCol+6, item.get("文化程度",""), style0)  
        ws.write(irow, startCol+7, item.get("焊接工作时间",""), style0)  
        ws.write(irow, startCol+8, item.get("邮政编码",""), style0)  
        ws.write(irow, startCol+9, item.get("联系地址",""), style0)  
        ws.write(irow, startCol+10, item.get("联系电话",""), style0)  
        ws.write(irow, startCol+11, item.get("焊接简历",""), style0)  
        ws.write(irow, startCol+12, item.get("WPS编号",""), style0)  
        ws.write(irow, startCol+13, item.get("新证",""), style0)  
        ws.write(irow, startCol+14, item.get("原证书编号",""), style0)  
        ws.write(irow, startCol+15, item.get("产品类型",""), style0)  
        ws.write(irow, startCol+16, item.get("定位焊",""), style0)  
        ws.write(irow, startCol+17, item.get("焊接方法",""), style0)  
        ws.write(irow, startCol+18, item.get("母材性质",""), style0)  
        ws.write(irow, startCol+19, item.get("填充金属",""), style0)  
        ws.write(irow, startCol+20, item.get("试件形式",""), style0)  
        ws.write(irow, startCol+21, item.get("可焊板厚",""), style0)  
        ws.write(irow, startCol+22, item.get("可焊管厚",""), style0)  
        ws.write(irow, startCol+23, item.get("可焊管径",""), style0)  
        ws.write(irow, startCol+24, item.get("接头形式",""), style0)  
        ws.write(irow, startCol+25, item.get("合格位置",""), style0)  
        ws.write(irow, startCol+26, item.get("其他细节1",""), style0)  
        ws.write(irow, startCol+27, item.get("其他细节2",""), style0)  
        irow = irow + 1
    # 另存为excel文件，并将文件命名  
    new_excel.save(xlsFile)
    return xlsFile

def write_daiyong_one(ws20, item, style, rowIdx):
    style5 = getStyle5()
    ws20.write_merge(7+rowIdx,7+rowIdx, 3,5, item.get(u"姓名",""), style)
    ws20.write(8+rowIdx, 3, item.get(u"性别",""), style)
    ws20.write(9+rowIdx, 3, item.get(u"身份证",""), style)
    ws20.write(10+rowIdx, 4, item.get(u"试件形式",""), style)
    ws20.write(11+rowIdx, 4, item.get(u"焊工编号",""), style)
    ws20.write(12+rowIdx, 4, item.get(u"施工队",""), style)
    ws20.write(13+rowIdx, 4, item.get(u"工区",""), style)
    ws20.write(14+rowIdx, 4, item.get(u"代用证日期",""), style5)
    ws20.write(15+rowIdx, 4, item.get(u"代用证到期",""), style5)
    ws20.write(3+rowIdx, 11, item.get(u"焊接方法2",""), style)
    ws20.write(4+rowIdx, 11, item.get(u"焊接方法1",""), style5)
    ws20.write_merge(5+rowIdx,5+rowIdx+1, 11,14, item.get(u"可焊位置",""), style5)
    ws20.write_merge(7+rowIdx,7+rowIdx+1, 11,14, item.get(u"填充金属",""), style5)
    ws20.write_merge(9+rowIdx,9+rowIdx+1, 11,14, item.get(u"母材性质",""), style5)
    ws20.write(11+rowIdx, 11, item.get(u"板厚",""), style5)
    ws20.write(12+rowIdx, 11, item.get(u"管厚",""), style5)
    ws20.write(13+rowIdx, 11, item.get(u"管径",""), style5)

def write_daiyong(ws20, items, style,pageIdx,pageSize):
    iRow = 3
    iCol = 1
    iStart = pageIdx * pageSize
    style3 = getStyle3()
    style4 = getStyle4()
    ws20.set_header_str(''.encode())
    ws20.set_footer_str(''.encode())
    for i in range(iRow):
        idx1 = iStart+i
        if idx1 < len(items):
            write_daiyong_one(ws20, items[idx1], style3, 0+21*i)
            #insert logo
            sPathTemplate = './WeldStaffPy/templates/'
            sDesc1="兹证明本证书持有人已经通过"
            sDesc2="THIS IS TO CERTIFICATY that the bearer has been qualified by the qualification test committee for welders of "
            if items[idx1]["船级社"] == "CCS":
                ws20.insert_bitmap(sPathTemplate+'1ccs.bmp', 1+21*i, 1, 1, 1,1,1)
                sDesc1 = sDesc1 +"中国船级社"
                sDesc2 = sDesc2 +"CCS"
            elif items[idx1]["船级社"] == "LR":
                ws20.insert_bitmap(sPathTemplate+'2lr.bmp', 1+21*i, 1, 1, 1,1,1)
                sDesc1 = sDesc1 +"劳氏船级社"
                sDesc2 = sDesc2 +"LR"
            elif items[idx1]["船级社"] == "ABS":
                ws20.insert_bitmap(sPathTemplate+'3abs.bmp', 1+21*i, 1, 1, 1,1,1)
                sDesc1 = sDesc1 +"美国船级社"
                sDesc2 = sDesc2 +"ABS"
            elif items[idx1]["船级社"] == "DNV":
                ws20.insert_bitmap(sPathTemplate+'4dnv.bmp', 1+21*i, 1, 1, 1,1,1)
                sDesc1 = sDesc1 +"挪威船级社"
                sDesc2 = sDesc2 +"DNV"
            sDesc1 = sDesc1 +"的焊工资格考试，能够从事本证书规定范围内的焊接工作。"
            sDesc2 = sDesc2 +" and is able to undertake welding operation specified in this Certificate."
            ws20.write_merge(3+21*i,3+21*i+1, 1,7, sDesc1, style4)
            ws20.write_merge(5+21*i,5+21*i+1, 1,7, sDesc2, style4)
            ws20.insert_bitmap(sPathTemplate+'0cosco.bmp', 1+21*i, 7, 1, 1,1,1)
            #insert profile 
            sPathUpload = './static/WeldStaffWeb/data/profile/'
            sbmp = sPathUpload + items[idx1][u"身份证"]+".bmp"
            if os.path.exists(sbmp) == True:
                ws20.insert_bitmap(sbmp, 7+21*i, 6, 1, 1,1,1)
    #set print area
    ws20.set_fit_num_pages(1)

def export_daiyong(items):
    fnaTmpl = u'./WeldStaffPy/templates/daiyongzheng.xls'
    fna2 = u'./WeldStaffPy/download/daiyongzheng_down-t.xls'
    fna3 = u'./WeldStaffPy/download/daiyongzheng_down.xls'
    _ExcelUtil = ExcelUtil()
    if not _ExcelUtil.open(fnaTmpl):
        return
    new_excel = _ExcelUtil.copy()
    _ExcelUtil.workbook.release_resources()
    del _ExcelUtil.workbook
    style0 = _ExcelUtil.aligncenter()
    style0.alignment.wrap = True
    _ExcelUtil.border(style0)
    pageSize = 3
    pageNum,pageOther = divmod(len(items), pageSize)
    if pageOther > 0:
        pageNum = pageNum + 1
    for i in range(pageNum):
        if i <= pageNum - 2:
            _ExcelUtil.copy_sheet(new_excel, str(i), i)
        _sheet = new_excel.get_sheet(i)
        _sheet.set_header_str(''.encode())
        _sheet.set_footer_str(''.encode())
        _sheet.set_name(str(i))
    _ExcelUtil.save(new_excel, fna2)
    if not _ExcelUtil.open(fna2):
        return
    new_excel = _ExcelUtil.copy()
    _ExcelUtil.workbook.release_resources()
    del _ExcelUtil.workbook
    for i in range(pageNum):
        write_daiyong(new_excel.get_sheet(i), items,style0, i,pageSize)
    _ExcelUtil.active(0, new_excel)
    _ExcelUtil.save(new_excel, fna3)
    os.remove(fna2)
    return fna3

def write_qr(ws20, items,style,pageIdx,pageSize):
    iRow = 5
    iCol = 4
    iStart = pageIdx * pageSize
    ws20.set_header_str(''.encode())
    ws20.set_footer_str(''.encode())
    for i in range(iRow):
        for j in range(iCol):
            idx1 = iStart+i*iCol+j
            if idx1 < len(items):
                ws20.write(9+13*i, 2+j*4, items[idx1][u"姓名"], style)
                ws20.write(10+13*i, 2+j*4, items[idx1][u"工区"], style)
                ws20.write(11+13*i, 2+j*4, items[idx1][u"施工队"], style)
    #insert logo
    sPathTemplate = './static/WeldStaffWeb/data/qr/'
    for i in range(iRow):
        for j in range(iCol):
            idx1 = iStart+i*iCol+j
            if idx1 < len(items):
                ws20.insert_bitmap(items[idx1]["QR"], 2+13*i, 1+4*j, 1, 1,1,1)
    #set print area
    ws20.set_fit_num_pages(1)

def export_qr(items):
    fnaTmpl = u'./WeldStaffPy/templates/erweima.xls'
    fna2 = u'./WeldStaffPy/download/erweima_down-t.xls'
    fna3 = u'./WeldStaffPy/download/erweima_down.xls'
    _ExcelUtil = ExcelUtil()
    if not _ExcelUtil.open(fnaTmpl):
        return
    new_excel = _ExcelUtil.copy()
    _ExcelUtil.workbook.release_resources()
    del _ExcelUtil.workbook
    style0 = _ExcelUtil.aligncenter()
    style0.alignment.wrap = True
    _ExcelUtil.border(style0)
    pageSize = 20
    pageNum,pageOther = divmod(len(items), pageSize)
    if pageOther > 0:
        pageNum = pageNum + 1
    for i in range(pageNum):
        if i <= pageNum-2 :
            _ExcelUtil.copy_sheet(new_excel, str(i), i)
        _sheet = new_excel.get_sheet(i)
        _sheet.set_header_str(''.encode())
        _sheet.set_footer_str(''.encode())
        _sheet.set_name(str(i))
    _ExcelUtil.save(new_excel, fna2)
    if not _ExcelUtil.open(fna2):
        return
    new_excel = _ExcelUtil.copy()
    _ExcelUtil.workbook.release_resources()
    del _ExcelUtil.workbook
    for i in range(pageNum):
        write_qr(new_excel.get_sheet(i), items,style0, i,pageSize)
    _ExcelUtil.active(0, new_excel)
    _ExcelUtil.save(new_excel, fna3)
    os.remove(fna2)
    return fna3

def getStyle1():
    _ExcelUtil = ExcelUtil()
    style0 = _ExcelUtil.aligncenter()
    _ExcelUtil.border(style0)
    _ExcelUtil.font(u'宋体', False, style0)
    return style0

def getStyle2():
    _ExcelUtil = ExcelUtil()
    style0 = _ExcelUtil.aligncenter()
    _ExcelUtil.border(style0)
    _ExcelUtil.font(u'宋体', False, style0)
    style0.font.height = 240
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 7
    style0.pattern = pattern
    return style0

def getStyle3():
    _ExcelUtil = ExcelUtil()
    style0 = _ExcelUtil.aligncenter()
    _ExcelUtil.font(u'等线', False, style0,7)
    #borders = xlwt.Borders()
    #borders.left = xlwt.Borders.DASHED
    #borders.right = xlwt.Borders.DASHED
    #borders.top = xlwt.Borders.DASHED
    #borders.bottom = xlwt.Borders.DASHED
    #borders.left_colour = 4
    #borders.right_colour = 4
    #borders.top_colour = 4
    #borders.bottom_colour = 4
    #style0.borders = borders
    return style0

def getStyle4():
    _ExcelUtil = ExcelUtil()
    style0 = _ExcelUtil.aligncenter()
    _ExcelUtil.font(u'等线', False, style0,6)
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.DASHED
    borders.right = xlwt.Borders.DASHED
    borders.top = xlwt.Borders.NO_LINE
    borders.bottom = xlwt.Borders.DASHED
    borders.left_colour = 4
    borders.right_colour = 4
    borders.top_colour = 4
    borders.bottom_colour = 4
    style0.borders = borders
    return style0

def getStyle5():
    _ExcelUtil = ExcelUtil()
    style0 = _ExcelUtil.aligncenter()
    _ExcelUtil.font(u'等线', False, style0,6)
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.NO_LINE
    borders.right = xlwt.Borders.NO_LINE
    borders.top = xlwt.Borders.NO_LINE
    borders.bottom = xlwt.Borders.DASHED
    borders.left_colour = 4
    borders.right_colour = 4
    borders.top_colour = 4
    borders.bottom_colour = 4
    style0.borders = borders
    return style0

if __name__ == '__main__':
    #excel_test()
    mlist = []
    mlist.append({"T":"1"})
    excel_css(mlist)