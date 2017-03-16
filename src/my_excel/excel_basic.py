#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

from pandas import ExcelWriter


def open_excel(excel_name):
	# Create a Pandas Excel writer using XlsxWriter as the engine.
	writer = ExcelWriter(excel_name, engine='xlsxwriter')
	return writer


# def excel_book(excel_name):
# 	return open_excel(excel_name).book
#
#
# def excel_sheet(excel_name, sheet_name):
# 	return open_excel(excel_name).sheets[sheet_name]


def write_excel(excel_obj, content, sheet_name='sheet_1'):
	"""
	Convert the dataframe to an XlsxWriter Excel object.
	:param excel_obj: excel_obj
	:param content: content
	:param sheet_name: sheet_name
	:return: None
	"""
	content.T.to_excel(excel_obj, sheet_name=sheet_name, startrow=1, startcol=1, index=True, header=True)


def write_excel_format(worksheet_obj, cell_destination, cell_content, format_obj):
	"""
	Write into excel cell with format
	:param worksheet_obj: worksheet_obj
	:param cell_destination: cell_destination
	:param cell_content: cell_content
	:param format_obj: format_obj
	:return: None
	"""
	worksheet_obj.write(cell_destination, cell_content, format_obj)


def close_workbook(writer_obj):
	"""
	Close workbook
	:param writer_obj: writer_obj
	:return: None
	"""
	writer_obj.close()


def close_excel(writer_obj):
	"""
	Save and close excel
	:param writer_obj: writer_obj
	:return: None
	"""
	writer_obj.save()
	writer_obj.close()


def excel_col2str(col):
	"""
	convert a column number (eg. 127) into an excel column (eg. AA)
	:param n: excel column number
	:return: excel column
	"""
	div = col
	string = ""
	while div > 0:
		module = (div - 1) % 26
		string = chr(65 + module) + string
		div = int((div - module) / 26)
	return string


def excel_col2num(col):
	"""
	Convert an excel or spreadsheet column letter (eg. AA) to its number (eg. 127)
	:param col: excel column
	:return: excel column number
	"""
	import string
	num = 0
	for c in col:
		if c in string.ascii_letters:
			num = num * 26 + (ord(c.upper()) - ord('A')) + 1
	return num


def create_single_row(row_num, start, range_span):
	row_list = []
	for i in range(int(range_span)):
		row_list.append('{0}{1}'.format(excel_col2str(excel_col2num(start) + i), row_num))
	return row_list


def create_single_col(col_num, start, range_span):
	col_list = []
	for i in range(int(range_span)):
		col_list.append('{0}{1}'.format(col_num, int(start) + i))
	return col_list


