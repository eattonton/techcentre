# -*- coding: utf-8 -*-
import os, sys
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
            arr1.append(cell)
        mlist.append(arr1)
    return mlist


# 保存为xls
def excel_export_one(item):
    _ExcelUtil = ExcelUtil()
    templ = u'./templates/quality_template.xls'
    xlsFile = u'./data/download/' + item[u"报验编号"] + '.xls'
    if not _ExcelUtil.open(templ):
        return
    new_excel = _ExcelUtil.copy()
    # 获得第一个sheet的对象  
    ws = new_excel.get_sheet(0)
    ws.set_header_str(''.encode())
    ws.set_footer_str(''.encode())
    style0 = _ExcelUtil.aligncenter()
    style0.alignment.wrap = True
    _ExcelUtil.border(style0)
    _ExcelUtil.font(u'宋体', True, style0)
    write_one_sheet(ws, item, style0)
    new_excel.save(xlsFile)
    return xlsFile


def write_one_sheet(ws20, val, style):
    ws20.set_header_str(''.encode())
    ws20.set_footer_str(''.encode())
    ws20.write(3, 1, val[u"项目名"], style)
    ws20.write(3, 3, val[u"船号"], style)
    ws20.write(1, 6, val[u"报验编号"], style)
    ws20.write(2, 6, val[u"报验日期"], style)
    ws20.write(3, 6, val[u"报验地点"], style)
    ws20.write(4, 1, val[u"报验项目"], style)
    ws20.insert_bitmap(u'./static/res/logo.bmp', 1, 0, 2, 2, 0.5, 0.6)


def excel_export_batch(items):
    fnaTmpl = u'./templates/quality_template.xls'
    item = items[0]
    fna2 = u'./data/download/' + item[u"报验编号"] + '-t.xls'
    fna3 = u'./data/download/' + item[u"报验编号"] + '.xls'
    _ExcelUtil = ExcelUtil()
    if not _ExcelUtil.open(fnaTmpl):
        return
    new_excel = _ExcelUtil.copy()
    _ExcelUtil.workbook.release_resources()
    del _ExcelUtil.workbook
    style0 = _ExcelUtil.aligncenter()
    style0.alignment.wrap = True
    _ExcelUtil.border(style0)
    for i, val in enumerate(items):
        if i <= len(items) - 2:
            _ExcelUtil.copy_sheet(new_excel, str(i), i)
        _sheet = new_excel.get_sheet(i)
        _sheet.set_header_str(''.encode())
        _sheet.set_footer_str(''.encode())
        _sheet.set_name(val[u"报验编号"])
    _ExcelUtil.save(new_excel, fna2)
    if not _ExcelUtil.open(fna2):
        return
    new_excel = _ExcelUtil.copy()
    _ExcelUtil.workbook.release_resources()
    del _ExcelUtil.workbook
    [write_one_sheet(new_excel.get_sheet(i), val, style0) for i, val in enumerate(items)]
    _ExcelUtil.active(0, new_excel)
    _ExcelUtil.save(new_excel, fna3)
    os.remove(fna2)
    return fna3


# 报验申请单模板
def excel_export_list(items, sfile, sproj='', sdate=''):
    templ = u'./templates/apply_info_template.xls'
    xlsFile = u'./data/download/' + sfile + '-list.xls'
    _ExcelUtil = ExcelUtil()
    if not _ExcelUtil.open(templ):
        return
    # 将操作文件对象拷贝，变成可写的workbook对象
    new_excel = _ExcelUtil.copy()
    ws = new_excel.get_sheet(0)
    ws.set_header_str(''.encode())
    ws.set_footer_str(''.encode())
    ws.set_portrait(2)
    style0 = getStyle1()
    style1 = getStyle2()
    startRow = 6
    irow = startRow
    ws.write(3, 2, sproj, style0)
    ws.write(3, 8, sdate, style0)
    itemkeys = ["Hull", "Machinery", "Outfitting", "Electric", "Piping", "Coating", "Income"]
    for k in itemkeys:
        count = len(items[k])
        if count == 0:
            continue
        ws.write_merge(irow, irow, 0, 8, k, style1)
        irow = irow + 1
        for i in range(count):
            item = items[k][i]
            ws.write(irow, 0, str(i + 1), style0)
            ws.write(irow, 1, item.get(u"报验时间", ''), style0)
            ws.write(irow, 2, item.get(u"报验地点", ''), style0)
            ws.write(irow, 3, item.get(u"报验编号", ''), style0)
            ws.write(irow, 4, item.get(u"报验项目", ''), style0)
            ws.write(irow, 5, item.get(u"报验工区", ''), style0)
            ws.write(irow, 6, item.get(u"船东", ''), style0)
            ws.write(irow, 7, item.get(u"船检", ''), style0)
            ws.write(irow, 8, item.get(u"质检员", ''), style0)
            irow = irow + 1
    # 设置列表宽
    ws.col(0).width = 2000
    ws.col(1).width = 2400
    ws.col(3).width = 4000
    # 另存为excel文件，并将文件命名  
    new_excel.save(xlsFile)
    return xlsFile


# 生产报验汇总表
def excel_export_all(items, shipno):
    templ = u'./templates/apply_total_template.xls'
    xlsFile = u'./data/download/' + shipno + '-dform-all.xls'
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
    startRow = 3
    irow = startRow
    count = len(items)
    predform = ''
    for i in range(count):
        item = items[i]
        ws.write(irow, 0, str(i + 1), style0)  # 序号
        ws.write(irow, 1, item.get(u"船号", ''), style0)  # 船号
        ws.write(irow, 2, item.get(u"报验日期", ''), style0)
        ws.write(irow, 3, item.get(u"报验编号", ''), style0)
        if item.get(u"报验编号", '') != predform:
            ws.write(irow, 4, str(item.get(u"报验次数", '')), style0)
        ws.write(irow, 5, item.get(u"报验项目", ''), style0)
        if item.get(u"船东结论", '') != '':
            ws.write(irow, 6, item.get(u"船东结论", ''), style0)
        else:
            ws.write(irow, 6, item.get(u"船东", ''), style0)
        if item.get(u"船检结论", '') != '':
            ws.write(irow, 7, item.get(u"船检结论", ''), style0)
        else:
            ws.write(irow, 7, item.get(u"船检", ''), style0)
        ws.write(irow, 8, item.get(u"意见分类", ''), style0)
        ws.write(irow, 9, item.get(u"意见内容", ''), style0)
        ws.write(irow, 10, item.get(u"关闭日期", ''), style0)
        ws.write(irow, 11, item.get(u"报验工区", ''), style0)
        ws.write(irow, 12, item.get(u"责任工区", ''), style0)
        ws.write(irow, 13, item.get(u"质检员", ''), style0)
        ws.write(irow, 14, item.get(u"上次报验单", ''), style0)
        ws.write(irow, 15, item.get(u"下次报验单", ''), style0)
        ws.write(irow,16,item.get(u"合格率统计","计入合格率统计"),style0)
        ws.write(irow, 17, item.get(u"施工班组", ""), style0)
        ws.write(irow, 18, item.get(u"转移时间", ""), style0)
        ws.write(irow, 19, item.get("_id", ''), style0)
        ws.write(irow, 20, item.get("_id2", ''), style0)
        irow = irow + 1
        predform = item.get(u"报验编号", '')
    # 设置列表宽
    ws.col(3).width = 4500
    ws.col(5).width = 10000
    ws.col(10).width = 4000
    ws.col(13).width = 4000
    ws.col(14).width = 4500
    ws.col(15).width = 4500
    # 另存为excel文件，并将文件命名  
    new_excel.save(xlsFile)
    return xlsFile

#意见遗留项导出
def excel_export_commentUndo(shipno,items):
    templ = u'./templates/dform-yiliux.xls'
    xlsFile = u'./data/download/yiliuxiang--'+shipno+'.xls'
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
    startRow = 2
    irow = startRow
    count = len(items)
    for i in range(count):
        item = items[i]
        ws.write(irow, 0, item.get(u"船号", ''), style0)  # 船号
        ws.write(irow, 1, item.get(u"报验日期", ''), style0)
        ws.write(irow, 2, item.get(u"报验次数", ''), style0)
        ws.write(irow, 3, item.get(u"报验编号", ''), style0)
        ws.write(irow, 4, item.get(u"意见编号", ''), style0)
        ws.write(irow, 5, item.get(u"报验项目", ''), style0)
        ws.write(irow, 6, item.get(u"报验工区", ''), style0)
        ws.write(irow, 7, item.get(u"责任工区", ''), style0)
        ws.write(irow, 8, item.get(u"意见内容", ''), style0)
        ws.write(irow, 9, item.get(u"意见分类", ''), style0)
        ws.write(irow, 10, item.get(u"质检员", ''), style0)
        icommentStatus = int(item.get(u"意见状态", '0'))
        if icommentStatus == 3:
            ws.write(irow, 11, "已关闭", style0)
        elif icommentStatus == 2:
            ws.write(irow, 11, "待复检", style0)
        else:
            ws.write(irow, 11, "未关闭", style0)
        irow = irow + 1
    # 另存为excel文件，并将文件命名  
    new_excel.save(xlsFile)
    return xlsFile

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


def exprot_rate(st1, st2, xlsFile, title, items={}, ):
    if os.path.exists(xlsFile):
        os.remove(xlsFile)
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet('Sheet1', cell_overwrite_ok=True)
    sheet.set_header_str(''.encode())
    sheet.set_footer_str(''.encode())
    sheet.set_portrait(2)
    sheet.write(0, 0, st1 + u'至' + st2 + title)
    _call = lambda item, key: item.get(key, '')
    iStartRow = 1
    # _list = [u'船号', u'分类', u'报验工区', u'合格', u'不合格', u'取消', u'合计', u'合格比', u'不合格比', u'取消比']
    # title
    _list = [u'船号', u'分类', u'报验工区', u'合格', u'不合格',
             u'船东取消(E)', u'船检取消(G)', u'船厂取消(F)', u'不可抗取消(H)',
             u'合计', u'合格比', u'不合格比']

    [sheet.write(iStartRow, j, key) for j, key in enumerate(_list)]

    def getKey(key):
        if "(" in key:
            return key.split("(")[1].split(")")[0]
        return key

    for item in items:
        iStartRow += 1
        [sheet.write(iStartRow, j, _call(item, getKey(key))) for j, key in enumerate(_list)]

    wbk.save(xlsFile)
    return xlsFile


def export_ylx(xlsFile,title,items):
    if os.path.exists(xlsFile):
        os.remove(xlsFile)
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet('Sheet1', cell_overwrite_ok=True)
    sheet.set_header_str(''.encode())
    sheet.set_footer_str(''.encode())
    sheet.set_portrait(2)
    style0 = getStyle1()
    # sheet.write(0, 0,title,style0)
    _call = lambda item, key: item.get(key, '')
    iStartRow = 1
    _list = [u'船号', u'报验日期', u'报验次数', u'报验编号', u'意见编号',
             u'报验项目', u'报验工区', u'责任工区', u'意见内容',
             u'意见分类', u'质检员', u'意见关闭']

    [sheet.write(iStartRow, j, key,style0) for j, key in enumerate(_list)]
    sheet.write_merge(0, 0, 0, len(_list)-1, title, style0)

    def getKey(key):
        if "(" in key:
            return key.split("(")[1].split(")")[0]
        return key

    for item in items:
        iStartRow += 1
        [sheet.write(iStartRow, j, _call(item, getKey(key))) for j, key in enumerate(_list)]

    wbk.save(xlsFile)
    return xlsFile

# 导出报验合格率
def excel_export_rate(st1, st2, items={}):
    return exprot_rate(st1, st2, u'./data/download/dform-rate.xls', u'报验合格率', items)

# 导出一次报验合格率
def excel_export_rateone(st1, st2, items={}):
    return exprot_rate(st1, st2, u'./data/download/dform-rate-one.xls', u'一次报验合格率', items)

# 导出报验遗留项目
def excel_export_ylx(items=[]):
    return export_ylx(u'./data/download/dform-yiliux.xls', u'报验遗留项', items)

#意见遗留项数量导出
def excel_export_ylx_count(sdtArr,itemArr):
    templ = u'./templates/dform-yiliux-count.xls'
    xlsFile = u'./data/download/yiliuxiang-count.xls'
    _ExcelUtil = ExcelUtil()
    if not _ExcelUtil.open(templ):
        return
    # 将操作文件对象拷贝，变成可写的workbook对象
    new_excel = _ExcelUtil.copy()
    # 获得第一个sheet的对象  超1周
    ws1 = new_excel.get_sheet(0)
    ws1.set_header_str(''.encode())
    ws1.set_footer_str(''.encode())
    style0 = getStyle1()
    startRow = 2
    irow = startRow
    items1 = itemArr[0]
    count1 = len(items1)
    ws1.write(0, 1, sdtArr[1], style0)
    ws1.write(0, 2, sdtArr[0], style0)
    for i in range(count1):
        item1 = items1[i]
        ws1.write(irow, 0, item1.get(u"船号", ''), style0)  # 船号
        ws1.write(irow, 1, item1.get(u"责任工区", ''), style0)
        ws1.write(irow, 2, item1.get(u"意见遗留数", ''), style0)
        irow = irow + 1
    # 获得第一个sheet的对象  超2周
    ws2 = new_excel.get_sheet(1)
    ws2.set_header_str(''.encode())
    ws2.set_footer_str(''.encode())
    irow = startRow
    items2 = itemArr[1]
    count2 = len(items2)
    ws2.write(0, 1, sdtArr[3], style0)
    ws2.write(0, 2, sdtArr[2], style0)
    for i in range(count2):
        item2 = items2[i]
        ws2.write(irow, 0, item2.get(u"船号", ''), style0)  # 船号
        ws2.write(irow, 1, item2.get(u"责任工区", ''), style0)
        ws2.write(irow, 2, item2.get(u"意见遗留数", ''), style0)
        irow = irow + 1
    # 获得第一个sheet的对象  超1月
    ws3 = new_excel.get_sheet(2)
    ws3.set_header_str(''.encode())
    ws3.set_footer_str(''.encode())
    irow = startRow
    items3 = itemArr[2]
    count3 = len(items3)
    ws3.write(0, 1, sdtArr[4], style0)
    for i in range(count3):
        item3 = items3[i]
        ws3.write(irow, 0, item3.get(u"船号", ''), style0)  # 船号
        ws3.write(irow, 1, item3.get(u"责任工区", ''), style0)
        ws3.write(irow, 2, item3.get(u"意见遗留数", ''), style0)
        irow = irow + 1
    # 另存为excel文件，并将文件命名  
    new_excel.save(xlsFile)
    return xlsFile

# if __name__ == '__main__':
# myform = QuaDailyForm()
# myform.read()
# print(myform.lineDic)
# myform.save('data/N688/db/')
