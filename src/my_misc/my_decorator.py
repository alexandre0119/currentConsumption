#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import functools
from src.my_misc.my_logging import create_logger

# Logger for decorator
log_decorator = create_logger(logger_name=__name__, fmt='%(message)s')


def enter_hci_header_footer():
	"""
	Decorator to indicate enter BT HCI cmd
	:return: decorator
	"""
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kw):
			# print('Begin {0} call {1}():'.format(cmd_num, func.__name__))
			log_decorator.info('\n---------------------Enter Hcitool cmd---------------------')
			now = func(*args, **kw)
			# print('End {0} call {1}():'.format(cmd_num, func.__name__))
			log_decorator.info('============================================================\n')
			return now

		return wrapper

	return decorator


def hci_return_header_footer():
	"""
	Decorator to indicate BT HCI cmd returns
	:return: decorator
	"""
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kw):
			# print('Begin {0} call {1}():'.format(cmd_num, func.__name__))
			log_decorator.info('\n---------------------Hcitool cmd return---------------------')
			now = func(*args, **kw)
			# print('End {0} call {1}():'.format(cmd_num, func.__name__))
			log_decorator.info('============================================================\n')
			return now

		return wrapper

	return decorator
