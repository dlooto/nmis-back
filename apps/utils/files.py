#coding=utf8

"""
used for file process
"""

import os, logging
from typing import Dict, List

from openpyxl.worksheet import Worksheet

import settings
from openpyxl import Workbook, load_workbook

logs = logging.getLogger('django')


def is_file_exist(path):
    """ 判断文件或目录是否存在 """
    return os.path.exists(path)


def remove(path, fileName=None):
    """remove file from the filesystem"""
    if not fileName:
        fullpath = path
    else:
        fullpath = os.path.join(path, fileName)
        
    try:
        os.remove(fullpath)
        return True
    except OSError as e:
        logs.error("delete file %s error: %s" % (fullpath, e))
        return False


def save_file(file, base_dir, file_name):
    """保存文件
    @param file  传入的文件参数, request.FILES中获取的数据对象, file需要先经过rename处理, 以便获取到file.name
    @param file_name  保存的目标文件名
     """
    
    if not file: return ''
    try:
        dest = open('%s/%s/%s' % (settings.MEDIA_ROOT, base_dir, file_name), 'wb+')
        for chunk in file.chunks():
            dest.write(chunk)
        dest.close()
    except Exception as e:
        logs.exception(e)
        dest.close()

    return file_name

#
# def read_sheet_with_header(ws, header_dict: dict):
#     """
#     读取单个sheet数据，带表头
#     :param ws: Worksheet对象
#     :param header_dict: 表头字典，K:键，一般为model属性；V:对应表头单元格数据
#     :return: 返回一个List对象，该List对象由一组Dictionary对象构成
#     """
#     sheet_data = list()
#     if ws:
#         ws_rows_len = ws.max_row
#         ws_column_len = len(header_dict)
#
#         # 读取首行数据
#         header_data = list()
#         for col in range(1, ws_column_len+1):
#             header_data.append(ws.cell(1, col).value)
#
#         header_keys = list() # 表头顺序对应的关键字列表
#         # 判断首行数据是否和指定的标准一致，如果一致，按顺序封装表头关键字；否则抛出异常
#         for item in header_dict.items():
#             for hdata in header_data:
#                 if item[1] == hdata:
#                     header_keys.append(item[0])
#                     break
#
#         if len(header_keys) != len(header_dict):
#             print(header_keys)
#             raise Exception('表单的表头数据和指定的标准不一致，请检查')
#
#         # 读取业务数据
#         for row in range(2, ws_rows_len+1):
#             row_data = {}
#             for col in range(1,ws_column_len+1):
#                 key = header_keys[col-1]
#                 value = ws.cell(row=row, column=col).value
#                 row_data[key]= value
#             sheet_data.append(row_data)
#
#     return sheet_data


def get_file_extension(path):
    return os.path.splitext(path)[1]


class ExcelBasedOXL(object):
    """
    基于Openpyxl库的excel封装
    """

    workbook = None

    @staticmethod
    def open_excel(path):
        """
        打开excel
        :param path: the path to open or a file-like object
        :type path: string or a file-like object open in binary mode c.f., :class:`zipfile.ZipFile`
        :return: 返回Workbook对象，即excel文件对象
        """
        global workbook
        if not path:
            return None
        workbook = load_workbook(path)
        return workbook

    @staticmethod
    def get_sheet(sheet_name):
        """
        获取Worksheet对象
        :return: 返回Worksheet对象
        """
        global workbook
        return workbook[sheet_name]

    @staticmethod
    def get_rows_len(sheet):
        """
        获取sheet的最大行数
        :param sheet: Worksheet对象
        :return: 返回行数
        """
        if not sheet:
            return None
        return sheet.max_row

    @staticmethod
    def get_cell_value(sheet, row, col):
        """
        获取单元格中内容
        :param sheet: Worksheet对象
        :param row: 行序列号，默认1是首行
        :param col: 列序列号，默认1是首列
        :return:
        """
        if not sheet:
            return None
        return sheet.cell(row, col).value

    @staticmethod
    def close():
        """
        关闭Workbook对象
        :return:
        """
        global workbook
        workbook.close()

    @staticmethod
    def read_excel_with_header(wb: Workbook, header_dict: Dict)->List[Dict[str, str]]:
        """
        读取单个excel文件数据，带表头
        :param wb: Workbook对象
        :param header_dict: 表头字典，K:键，一般为model属性；V:对应表头单元格数据
        :return:
        """
        excel_data = []
        for sheet_name in wb.sheetnames:
            sheet_data = ExcelBasedOXL.read_sheet_with_header(wb[sheet_name], header_dict)
            if sheet_data:
                excel_data.append(sheet_data)
        return excel_data

    @staticmethod
    def read_sheet_with_header(ws: Worksheet, header_dict: Dict)->List[Dict[str, str]]:
        """
        读取单个sheet数据，带表头
        :param ws: Worksheet对象
        :param header_dict: 表头字典，K:键，一般为model属性；V:对应表头单元格数据
        :return: 返回一个List对象，该List对象由一组Dictionary对象构成
        """
        sheet_data: List[Dict[str, str]] = []
        if ws:
            ws_rows_len = ws.max_row
            ws_column_len = len(header_dict)

            # 读取首行数据
            header_data = []
            for col in range(1, ws_column_len+1):
                header_data.append(ws.cell(1, col).value)

            header_keys = []  # 表头顺序对应的关键字列表
            # 判断首行数据是否和指定的标准一致，如果一致，按顺序封装表头关键字；否则抛出异常
            for item in header_dict.items():
                for hdata in header_data:
                    if item[1] == hdata:
                        header_keys.append(item[0])
                        break

            if len(header_keys) != len(header_dict):
                # 抛出“表单的表头数据和指定的标准不一致，请检查”异常
                raise Exception('ExcelHeaderNotMatched')

            # 读取业务数据
            for row in range(2, ws_rows_len+1):
                row_data = {}
                for col in range(1, ws_column_len+1):
                    key = header_keys[col-1]
                    value: str = ws.cell(row=row, column=col).value
                    row_data[key] = value
                sheet_data.append(row_data)

        return sheet_data




