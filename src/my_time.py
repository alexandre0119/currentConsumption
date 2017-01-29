#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import time
import datetime


def now():
	"""
	Get current date and time using datetime
	:return: current date and time not formatted
	"""
	now_info = datetime.datetime.now()
	return now_info


def time_zone():
	"""
	Get current time zone using datetime
	:return: current time zone as str
	"""
	time_zone_info = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
	return str(time_zone_info)


def now_formatted():
	"""
	Get current date and time formatted using datetime
	:return: current date and time formatted
	"""
	format = "%A %m-%d-%Y %H:%M:%S"
	now_formatted_info = datetime.datetime.now().strftime(format) + ' ' + time_zone()
	return now_formatted_info


def sleep(t):
	"""
	sleep for t second(s)
	:param t: time for sleep in second
	:return: t
	"""
	time.sleep(t)
	return t


def time_delta(start_time, end_time):
	"""
	Get time duration between start time and end time
	:param start_time: start time
	:param end_time: end time
	:return: delta from start time to end time
	"""
	delta = end_time - start_time
	return delta

# # Examples
# print(now())
# print(time_zone())
# print(now_formatted())
#
# start_time = now()
# sleep(1)
# end_time = now()
# print(time_delta(start_time, end_time))
