#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

from pandas import ExcelWriter

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