#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang


def format_title_one(workbook):
	"""
	Format level one title
	:param workbook: workbook name
	:return: format object
	"""
	my_format = workbook.add_format()

	my_format.set_bold()

	my_format.set_border()
	my_format.set_border_color('#2DA2BF')

	my_format.set_font_color('#FFFFFF')
	my_format.set_font_name('Calibri')
	my_format.set_font_size('20')

	my_format.set_bg_color('#22798E')

	my_format.set_align('center')
	my_format.set_align('vcenter')

	return my_format


def format_title_two(workbook):
	"""
	Format level two title
	:param workbook: workbook name
	:return: format object
	"""
	my_format = workbook.add_format()

	my_format.set_bold()

	my_format.set_border()
	my_format.set_border_color('#2DA2BF')

	my_format.set_font_color('#FFFFFF')
	my_format.set_font_name('Calibri')
	my_format.set_font_size('14')

	my_format.set_bg_color('#22798E')

	my_format.set_align('center')
	my_format.set_align('vcenter')

	return my_format


def format_index_one(workbook):
	"""
	Format level one index
	:param workbook: workbook name
	:return: format object
	"""
	my_format = workbook.add_format()

	my_format.set_bold()

	my_format.set_border()
	my_format.set_border_color('#2DA2BF')

	my_format.set_font_color('#464646')
	my_format.set_font_name('Calibri')
	my_format.set_font_size('12')

	my_format.set_bg_color('#DCE6F1')

	my_format.set_align('right')
	my_format.set_align('vcenter')

	return my_format


def format_content_one(workbook):
	"""
	Format level one cell content
	:param workbook: workbook name
	:return: format object
	"""
	my_format = workbook.add_format()

	my_format.set_bold(False)

	my_format.set_border()
	my_format.set_border_color('#2DA2BF')

	my_format.set_font_color('#464646')
	my_format.set_font_name('Calibri')
	my_format.set_font_size('12')

	my_format.set_bg_color('#FFFFFF')

	my_format.set_align('left')
	my_format.set_align('vcenter')

	return my_format


def format_content_two(workbook):
	"""
	Format level two content
	:param workbook: workbook name
	:return: format object
	"""
	my_format = workbook.add_format()

	my_format.set_bold(False)

	my_format.set_border()
	my_format.set_border_color('#2DA2BF')

	my_format.set_font_color('#464646')
	my_format.set_font_name('Calibri')
	my_format.set_font_size('12')

	my_format.set_bg_color('#FFFFFF')

	my_format.set_align('center')
	my_format.set_align('vcenter')

	return my_format


def set_column_width(worksheet, start, end, width):
	"""
	Format column width
	:param worksheet: worksheet name
	:param start: start column
	:param end: end column
	:param width: width in integer
	:return: None
	"""
	worksheet.set_column('{0}:{1}'.format(start, end), width)
