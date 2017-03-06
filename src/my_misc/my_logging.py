#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang # This file is cited online

import sys
import logging
import os


def create_logger(logger_name=__name__, log_file='log_this.txt', log_lvl='DEBUG'):
	logger = logging.getLogger(logger_name)

	if logger.handlers:
		return logger
	else:
		logger = logging.getLogger(logger_name)

		log_level = getattr(logging, log_lvl.upper(), logging.INFO)

		logger.setLevel(log_level)

		# create file handler
		fh = logging.FileHandler(log_file, mode='a')
		fh.setLevel(log_level)

		# create console handler
		ch = logging.StreamHandler(stream=sys.stdout)
		ch.setLevel(log_level)

		# create formatter and add it to the handlers
		# formatter = logging.Formatter('[%(asctime)s] %(levelname)8s --- %(message)s' +
		#                                '(%(filename)s:%(lineno)s)', datefmt='%Y-%m-%d %H:%M:%S')

		fmt = '[%(asctime)s] %(levelname)8s --- \n%(message)s'
		fmt_date = '%Y-%m-%d %H:%M:%S'
		formatter = logging.Formatter(fmt, fmt_date)

		fh.setFormatter(formatter)
		ch.setFormatter(formatter)

		# add the handlers to the logger
		logger.addHandler(ch)
		logger.addHandler(fh)

		if logger.name == 'root':
			logger.warning('Running: %s %s',
			               os.path.basename(sys.argv[0]),
			               ' '.join(sys.argv[1:]))

		return logger
