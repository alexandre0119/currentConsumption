#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang # This file is cited online

import sys
import os
import logging

# create logger, write to a file
def create_logger(logger_name='default', log_file='log_this.txt'):

	logger = logging.getLogger(logger_name)
	logger.setLevel(logging.DEBUG)

	# create file handler
	fh = logging.FileHandler(log_file, mode='a')
	fh.setLevel(logging.DEBUG)

	# create console handler
	sh = logging.StreamHandler(stream=sys.stdout)
	sh.setLevel(logging.DEBUG)

	# create formatter and add it to the handlers
	formatter = logging.Formatter('[%(asctime)s] %(levelname)8s --- %(message)s ' +
	                               '(%(filename)s:%(lineno)s)', datefmt='%Y-%m-%d %H:%M:%S')

	fh.setFormatter(formatter)
	sh.setFormatter(formatter)

	# add the handlers to the logger
	logger.addHandler(sh)
	logger.addHandler(fh)

	return logger


