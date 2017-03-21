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
	:param col: excel column number
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


def create_single_row(col_start, row_num, col_span):
	"""
	Create single row of Excel cell
	:param col_start: Column start point
	:param row_num: Row number
	:param col_span: Column span range
	:return: Row cell number list
	"""
	row_list = []
	for i in range(int(col_span)):
		row_list.append('{0}{1}'.format(excel_col2str(excel_col2num(col_start) + i), row_num))
	return row_list


def create_single_col(col_num, row_start, row_span):
	"""
	Create single column of Excel cell
	:param col_num: Column number
	:param row_start: Row start point
	:param row_span: Row span range
	:return: Column cell number list
	"""
	col_list = []
	for i in range(int(row_span)):
		col_list.append('{0}{1}'.format(col_num, int(row_start) + i))
	return col_list


def create_array(col_start, row_start, col_span, row_span):
	"""
	Create array of Excel cell
	:param col_start: column start point
	:param row_start: row start point
	:param col_span: column span range
	:param row_span: row span range
	:return: array list
	"""
	single_list = []
	array_list = []
	for i_index in range(int(row_span)):
		for i_column in range(int(col_span)):
			single_list.append('{0}{1}'.format(excel_col2str(excel_col2num(col_start) + i_column),
			                                   int(row_start) + i_index))
		array_list.append(single_list)
		single_list = []
	return array_list
