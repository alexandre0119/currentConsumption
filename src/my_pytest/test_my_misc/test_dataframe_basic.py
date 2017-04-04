#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import src.my_misc.dataframe_basic as dataframe_basic

import pandas as pd
import numpy as np

my_idx = ['1-1', '2-2', '3-3', '4-4', '5-5']
my_col = ['A', 'B', 'C', 'D']
my_content = [[0.338693, 1.388285, 0.095741, 0.780868],
              [-0.419889, -0.574683, -1.438844, 0.386572],
              [-1.597007, 0.009910, 0.508083, -0.338481],
              [- 2.250240, 0.702286, 0.375996, 0.509667],
              [0.943222, 0.769680, 0.954546, -0.965786]]
# df_sample = pd.DataFrame(np.random.randn(5, 4), index=my_idx, columns=my_col)
df_sample = pd.DataFrame(my_content, index=my_idx, columns=my_col)

print(df_sample)

def test_get_col():
	# print(dataframe_basic.get_col(df_sample))
	assert dataframe_basic.get_col(df_sample)[0] == 'A'
	assert dataframe_basic.get_col(df_sample)[1] == 'B'
	assert dataframe_basic.get_col(df_sample)[2] == 'C'
	assert dataframe_basic.get_col(df_sample)[3] == 'D'
	assert dataframe_basic.get_col(df_sample).tolist() == ['A', 'B', 'C', 'D']


def test_get_idx():
	# print(dataframe_basic.get_idx(df_sample))
	assert dataframe_basic.get_idx(df_sample)[0] == '1-1'
	assert dataframe_basic.get_idx(df_sample)[1] == '2-2'
	assert dataframe_basic.get_idx(df_sample)[2] == '3-3'
	assert dataframe_basic.get_idx(df_sample)[3] == '4-4'
	assert dataframe_basic.get_idx(df_sample)[4] == '5-5'
	assert dataframe_basic.get_idx(df_sample).tolist() == ['1-1', '2-2', '3-3', '4-4', '5-5']

def test_get_col_value():
	# print(dataframe_basic.get_col_value(df_sample, 'A'))
	assert dataframe_basic.get_col_value(df_sample, 'A') == 0.338693
	assert dataframe_basic.get_col_value(df_sample, 'B') == 1.388285
	assert dataframe_basic.get_col_value(df_sample, 'C') == 0.095741
	assert dataframe_basic.get_col_value(df_sample, 'D') == 0.780868
