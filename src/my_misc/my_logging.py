#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang # This file is cited online

import sys
import os
import logging
import platform


# now we patch Python code to add color support to logging.StreamHandler
def add_coloring_to_emit_windows(fn):
	# add methods we need to the class
	def _out_handle(self):
		import ctypes
		return ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)

	# out_handle = property(_out_handle)

	def _set_color(self, code):
		import ctypes
		# Constants from the Windows API
		self.STD_OUTPUT_HANDLE = -11
		hdl = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
		ctypes.windll.kernel32.SetConsoleTextAttribute(hdl, code)

	setattr(logging.StreamHandler, '_set_color', _set_color)

	def new(*args):
		FOREGROUND_BLUE = 0x0001  # text color contains blue.
		FOREGROUND_GREEN = 0x0002  # text color contains green.
		FOREGROUND_RED = 0x0004  # text color contains red.
		# FOREGROUND_INTENSITY = 0x0008  # text color is intensified.
		FOREGROUND_WHITE = FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_RED
		# winbase.h
		# STD_INPUT_HANDLE = -10
		# STD_OUTPUT_HANDLE = -11
		# STD_ERROR_HANDLE = -12

		# wincon.h
		FOREGROUND_BLACK = 0x0000
		FOREGROUND_BLUE = 0x0001
		FOREGROUND_GREEN = 0x0002
		FOREGROUND_CYAN = 0x0003
		FOREGROUND_RED = 0x0004
		FOREGROUND_MAGENTA = 0x0005
		FOREGROUND_YELLOW = 0x0006
		FOREGROUND_GREY = 0x0007
		FOREGROUND_INTENSITY = 0x0008  # foreground color is intensified.

		BACKGROUND_BLACK = 0x0000
		BACKGROUND_BLUE = 0x0010
		BACKGROUND_GREEN = 0x0020
		BACKGROUND_CYAN = 0x0030
		BACKGROUND_RED = 0x0040
		BACKGROUND_MAGENTA = 0x0050
		BACKGROUND_YELLOW = 0x0060
		BACKGROUND_GREY = 0x0070
		BACKGROUND_INTENSITY = 0x0080  # background color is intensified.

		levelno = args[1].levelno
		if levelno >= 70:
			color = FOREGROUND_RED
		elif levelno >= 60:
			color = FOREGROUND_GREEN
		elif levelno >= 50:
			color = BACKGROUND_YELLOW | FOREGROUND_RED | FOREGROUND_INTENSITY | BACKGROUND_INTENSITY
		elif levelno >= 40:
			color = FOREGROUND_RED | FOREGROUND_INTENSITY
		elif levelno >= 30:
			color = FOREGROUND_YELLOW | FOREGROUND_INTENSITY
		elif levelno >= 20:
			color = FOREGROUND_CYAN
		elif levelno >= 10:
			color = FOREGROUND_MAGENTA
		else:
			color = FOREGROUND_WHITE
		args[0]._set_color(color)

		ret = fn(*args)
		args[0]._set_color(FOREGROUND_WHITE)
		# print "after"
		return ret

	return new


def add_coloring_to_emit_ansi(fn):
	# add methods we need to the class
	def new(*args):
		levelno = args[1].levelno
		if levelno >= 70:
			color = '\x1b[31m'  # red
		elif levelno >= 60:
			color = '\x1b[32m'  # green
		elif levelno >= 50:
			color = '\x1b[31m'  # red
		elif levelno >= 40:
			color = '\x1b[31m'  # red
		elif levelno >= 30:
			color = '\x1b[33m'  # yellow
		elif levelno >= 20:
			color = '\x1b[32m'  # green
		elif levelno >= 10:
			color = '\x1b[35m'  # pink
		else:
			color = '\x1b[0m'  # normal
		args[1].msg = color + args[1].msg + '\x1b[0m'  # normal
		# print "after"
		return fn(*args)

	return new


if platform.system() == 'Windows':
	# Windows does not support ANSI escapes and we are using API calls to set the console color
	logging.StreamHandler.emit = add_coloring_to_emit_windows(logging.StreamHandler.emit)
else:
	# all non-Windows platforms are supporting ANSI escapes so we use them
	logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)
# log = logging.getLogger()
# log.addFilter(log_filter())
# //hdlr = logging.StreamHandler()
# //hdlr.setFormatter(formatter())


class DispatchingFormatter:
	"""Dispatch formatter for logger and it's sub logger."""
	def __init__(self, formatters, default_formatter):
		self._formatters = formatters
		self._default_formatter = default_formatter

	def format(self, record):
		# Search from record's logger up to it's parents:
		logger = logging.getLogger(record.name)
		while logger:
			# Check if suitable formatter for current logger exists:
			if logger.name in self._formatters:
				formatter = self._formatters[logger.name]
				break
			else:
				logger = logger.parent
		else:
			# If no formatter found, just use default:
			formatter = self._default_formatter
		return formatter.format(record)


# create logger, write to a file
def create_logger_append(logger_name, log_file):
	logging.PASS = 60
	logging.addLevelName(logging.PASS, "PASS")
	logging.Logger.PASS = lambda inst, msg, *args, **kwargs: inst.log(logging.PASS, msg, *args, **kwargs)
	# logger = logging.getLogger("foo")
	# logger.log(logging.PASS, "blah blah blah blah blah!")
	logging.FAIL = 70
	logging.addLevelName(logging.FAIL, "FAIL")
	logging.Logger.FAIL = lambda inst, msg, *args, **kwargs: inst.log(logging.FAIL, msg, *args, **kwargs)


	logger_append = logging.getLogger(logger_name)
	logger_append.setLevel(logging.DEBUG)

	# create file handler which logs even debug messages
	fh = logging.FileHandler(log_file, mode='a')
	fh.setLevel(logging.DEBUG)

	# create console handler with a higher log level
	ch = logging.StreamHandler(stream=sys.stdout)
	# ch.setLevel(logging.CRITICAL)
	ch.setLevel(logging.DEBUG)

	# create formatter and add it to the handlers
	# formatter = logging.Formatter('[%(asctime)s] %(levelname)8s --- %(message)s ' +
	#                               '(%(filename)s:%(lineno)s)', datefmt='%Y-%m-%d %H:%M:%S')
	formatter = logging.Formatter()

	# fh.setFormatter(formatter)
	fh.setFormatter(DispatchingFormatter({
		'info': logging.Formatter('[%(asctime)s]%(levelname)8s => %(message)s', datefmt='%Y-%m-%d %H:%M:%S'),
		'info.detail': logging.Formatter('[%(asctime)s]%(levelname)8s => %(message)s', datefmt='%Y-%m-%d %H:%M:%S'), },
		logging.Formatter(), ))
	ch.setFormatter(DispatchingFormatter({
        'info': logging.Formatter('[%(asctime)s]%(levelname)8s => %(message)s', datefmt='%Y-%m-%d %H:%M:%S'),
        'info.detail': logging.Formatter('[%(asctime)s]%(levelname)8s => %(message)s', datefmt='%Y-%m-%d %H:%M:%S'),},
		logging.Formatter(),))

	# add the handlers to the logger
	logger_append.addHandler(ch)
	logger_append.addHandler(fh)

	return logger_append

current_dir = os.getcwd()
logger_append = create_logger_append('default', current_dir + r'\logs\log_this.txt')
logger_append_info = create_logger_append('info', current_dir + r'\logs\log_this.txt')
logger_append_info_detail = create_logger_append('info.detail', current_dir + r'\logs\log_this.txt')

# logger.log(logging.NOTSET,   "NOTSET   Message - 0")
# logger.log(logging.DEBUG,    "DEBUG    Message - 10")
# logger.log(logging.INFO,     "INFO     Message - 20")
# logger.log(logging.WARNING,  "WARNING  Message - 30")
# logger.log(logging.ERROR,  "WARNING  Message - 30")
# logger.log(logging.CRITICAL, "CRITICAL Message - 40")

# logging.debug("a debug")
# logging.info("some info")
# logging.warn("a warning")
# logging.error("some error")
# logging.critical("some critical")
