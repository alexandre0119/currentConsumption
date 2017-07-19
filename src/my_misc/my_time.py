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


def now_formatted(now_time):
	"""
	Get current date and time formatted using datetime
	:return: current date and time formatted
	"""
	format_str = "%H:%M:%S %m-%d-%Y %A"
	now_formatted_info = now_time.strftime(format_str) + ' ' + time_zone()
	return now_formatted_info


def sleep(t):
	"""
	sleep for t second(s)
	:param t: time for sleep in second
	:return: t
	"""
	time.sleep(t)
	return t


def strfdelta(t_delta, fmt):
	d = {"days": t_delta.days}
	d["hours"], rem = divmod(t_delta.seconds, 3600)
	d["minutes"], d["seconds"] = divmod(rem, 60)
	return fmt.format(**d)


def time_delta(start_time, end_time):
	"""
	Get time duration between start time and end time
	:param start_time: start time
	:param end_time: end time
	:return: delta from start time to end time
	"""
	delta = end_time - start_time
	delta_formatted = strfdelta(delta, "{hours}:{minutes}:{seconds} {days} days")
	return delta_formatted
