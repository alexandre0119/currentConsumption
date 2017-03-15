#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

from collections import OrderedDict

from pandas import DataFrame


def get_col(dataframe_content):
	"""
	Get dataframe column value
	:param dataframe_content: dataframe
	:return: dataframe column value
	"""
	return dataframe_content.columns.values


def get_idx(dataframe_content):
	"""
	Get dataframe index value
	:param dataframe_content: dataframe
	:return: dataframe index value
	"""
	return dataframe_content.index.values


def get_col_value(dataframe_content, dataframe_column):
	"""
	Get dataframe value in certain column
	:param dataframe_content: dataframe
	:param dataframe_column: column
	:return: value
	"""
	return dataframe_content[dataframe_column].values[0]


def get_idx_col_value(datafram_content, datafram_idx, dataframe_col):
	"""
	Get dataframe value based on index and column
	:param datafram_content: dataframe
	:param dataframe_col: column
	:param datafram_idx: index
	:return: cel content
	"""
	return datafram_content.get_value(datafram_idx, dataframe_col)