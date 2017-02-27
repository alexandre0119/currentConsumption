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
	# Convert the dataframe to an XlsxWriter Excel object.
	return content.T.to_excel(excel_obj, sheet_name=sheet_name, startrow=1, startcol=1, index=True, header=True)


def close_workbook(writer_obj):
	writer_obj.close()


def close_excel(writer_obj):
	writer_obj.save()
	writer_obj.close()
