# -*- coding: utf-8 -*-
import os, sys
import json
import xlrd 
import weldStaffDataStruct
import weldStaffmgdb

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
            else:
                cell = cell.strip()
            arr1.append(cell)
        mlist.append(arr1)
    return mlist

def LoadWeldStaffExcel(file='file.xls'):
    mlist = excel_table_byindex(file,1)
    mlist2 = weldStaffDataStruct.GetWeldStaffStatus1(mlist)
    mdb = weldStaffmgdb.mgdbWeldStaff()
    mdb.lockinsertListStatus0(mlist2)

if __name__ == '__main__':
    mlist = excel_table_byindex('D:\\Coding\\quality_control\\upload\\lezhoutong_weldstaff.xls',1)
    print(mlist)