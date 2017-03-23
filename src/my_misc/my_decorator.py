#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang
# Time related
import src.my_misc.my_time as my_time

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


def main_flow_starter(enable_print=1):
	"""
	Main flow starter
	:param enable_print: 1 to enable logging/print
	:return: not formatted and formatted time when enable is non 1
	"""
	start_str = '''
	================================================================
	Program starts @ {0}
	----------------------------------------------------------------
	'''
	if enable_print == 1:
		start_time = my_time.now()
		final_str = start_str.format(my_time.now_formatted(start_time))
		# print(final_str)
		log_decorator.info(final_str)
	else:
		start_time = my_time.now()
		return start_time, my_time.now_formatted(start_time)


def main_flow_ender(enable_print=1):
	"""
	Main flow ender
	:param enable_print: 1 to enable logging/print
	:return: not formatted and formatted time when enable is non 1
	"""
	end_str = '''
	----------------------------------------------------------------
	Program ends @ {0}
	================================================================
	'''
	if enable_print == 1:
		end_time = my_time.now()
		final_str = end_str.format(my_time.now_formatted(end_time))
		# print(final_str)
		log_decorator.info(final_str)
	else:
		end_time = my_time.now()
		return end_time, my_time.now_formatted(end_time)


def main_flow_run_time(start_time, end_time, enable_print=1):
	"""
	Main flow run time
	:param start_time: start time
	:param end_time: end time
	:param enable_print: 1 to enable logging/print
	:return: time value when enable is non 1
	"""
	run_time_str = '''
	----------------------------------------------------------------
	Program total running time: {0}
	================================================================
	'''
	if enable_print == 1:
		delta_time = my_time.time_delta(start_time, end_time)
		final_str = run_time_str.format(delta_time)
		# print(final_str)
		log_decorator.info(final_str)
	else:
		delta_time = my_time.time_delta(start_time, end_time)
		return delta_time
