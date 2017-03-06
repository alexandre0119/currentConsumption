#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import functools
from src.my_misc.my_logging import create_logger

log = create_logger()


def enter_hci_header_footer():
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kw):
			# print('Begin {0} call {1}():'.format(cmd_num, func.__name__))
			log.info('\n---------------------Enter Hcitool cmd---------------------')
			now = func(*args, **kw)
			# print('End {0} call {1}():'.format(cmd_num, func.__name__))
			log.info('============================================================\n')
			return now

		return wrapper

	return decorator


def hci_return_header_footer():
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kw):
			# print('Begin {0} call {1}():'.format(cmd_num, func.__name__))
			log.info('\n---------------------Hcitool cmd return---------------------')
			now = func(*args, **kw)
			# print('End {0} call {1}():'.format(cmd_num, func.__name__))
			log.info('============================================================\n')
			return now

		return wrapper

	return decorator
