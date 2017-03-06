#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang # This file is cited online

import sys
import logging


def create_logger(logger_name=__name__, log_file='log_this.txt'):
	logger = logging.getLogger(logger_name)

	if logger.handlers:
		return logger
	else:
		logger = logging.getLogger(logger_name)
		logger.setLevel(logging.DEBUG)

		# create file handler
		fh = logging.FileHandler(log_file, mode='a')
		fh.setLevel(logging.DEBUG)

		# create console handler
		ch = logging.StreamHandler(stream=sys.stdout)
		ch.setLevel(logging.DEBUG)

		# create formatter and add it to the handlers
		# formatter = logging.Formatter('[%(asctime)s] %(levelname)8s --- %(message)s' +
		#                                '(%(filename)s:%(lineno)s)', datefmt='%Y-%m-%d %H:%M:%S')

		formatter = logging.Formatter('[%(asctime)s] %(levelname)8s --- %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

		fh.setFormatter(formatter)
		ch.setFormatter(formatter)

		# add the handlers to the logger
		logger.addHandler(ch)
		logger.addHandler(fh)

		return logger
