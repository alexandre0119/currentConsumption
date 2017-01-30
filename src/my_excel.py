#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

from pandas import ExcelWriter


def open_excel(excel_name):
	my_excel = ExcelWriter(excel_name)
	return my_excel


def save_excel(obj):
	obj.save()


def write_excel(excel_obj, content, sheet_name, index):
	content.T.to_excel(excel_obj, sheet_name=sheet_name, index=index)


