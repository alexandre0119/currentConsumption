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


def format_title(workbook):
	format = workbook.add_format()

	format.set_bold()

	format.set_border()
	format.set_border_color('#2DA2BF')

	format.set_font_color('#FFFFFF')
	format.set_font_name('Calibri')
	format.set_font_size('20')

	format.set_bg_color('#22798E')

	format.set_align('center')
	format.set_align('vcenter')

	return format


def format_item_subject(workbook):
	format = workbook.add_format()

	format.set_bold()

	format.set_border()
	format.set_border_color('#2DA2BF')

	format.set_font_color('#464646')
	format.set_font_name('Calibri')
	format.set_font_size('12')

	format.set_bg_color('#DCE6F1')

	format.set_align('right')
	format.set_align('vcenter')

	return format


def format_item_content(workbook):
	format = workbook.add_format()

	format.set_bold(False)

	format.set_border()
	format.set_border_color('#2DA2BF')

	format.set_font_color('#464646')
	format.set_font_name('Calibri')
	format.set_font_size('12')

	format.set_bg_color('#FFFFFF')

	format.set_align('left')
	format.set_align('vcenter')

	return format


def set_column_width(worksheet, start, end, width):
	worksheet.set_column('{0}:{1}'.format(start, end), width)


def write_excel(excel_obj, content, sheet_name='sheet_1'):
	# Convert the dataframe to an XlsxWriter Excel object.
	return content.T.to_excel(excel_obj, sheet_name=sheet_name, startrow=1, startcol=1, index=True, header=True)


def close_workbook(writer_obj):
	writer_obj.close()


def close_excel(writer_obj):
	writer_obj.save()
	writer_obj.close()

