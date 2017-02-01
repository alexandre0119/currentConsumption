#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import configparser

def load_config(config_name):
	config = configparser.ConfigParser()
	config.read(config_name)
	return config