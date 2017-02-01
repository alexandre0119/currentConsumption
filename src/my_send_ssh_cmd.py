#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import src.my_ssh as my_ssh
import src.my_bt_case as my_bt_case
import src.my_config as my_config


def bt_init():
	config = my_config.load_config('config.ini')
	chip_version = str(config['BASIC'].get('Select_ChipVersion'))
	dut = str(config['BASIC'].get('Dut'))
	ref = str(config['BASIC'].get('Ref'))
	return my_bt_case.Init(chip_version, dut, ref)


def bt_power_init():
	config = my_config.load_config('config.ini')
	chip_version = str(config['BASIC'].get('Select_ChipVersion'))
	dut = str(config['BASIC'].get('Dut'))
	ref = str(config['BASIC'].get('Ref'))
	return my_bt_case.PowerLevel(chip_version, dut, ref)


def bt_bt_init():
	config = my_config.load_config('config.ini')
	chip_version = str(config['BASIC'].get('Select_ChipVersion'))
	dut = str(config['BASIC'].get('Dut'))
	ref = str(config['BASIC'].get('Ref'))
	return my_bt_case.BT(chip_version, dut, ref)


def bt_ble_init():
	config = my_config.load_config('config.ini')
	chip_version = str(config['BASIC'].get('Select_ChipVersion'))
	dut = str(config['BASIC'].get('Dut'))
	ref = str(config['BASIC'].get('Ref'))
	my_bt_case.BLE(chip_version, dut, ref)


def cc_bt_reset(hci):
	my_ssh.open_connection_ssh().send_command(bt_bt_init().bt_reset(hci))


def cc_bt_deepsleep():
	my_ssh.open_connection_ssh().send_command(bt_bt_init().bt_deepsleep())


def cc_bt_noscan():
	my_ssh.open_connection_ssh().send_command(bt_bt_init().bt_noscan())


def cc_bt_set_power_level(power_level):
	my_ssh.open_connection_ssh().send_command(bt_power_init().bt_set_power_level(power_level))


def cc_bt_init_status(hci_dut, hci_ref, power_level):
	cc_bt_reset(hci_dut)
	cc_bt_reset(hci_ref)
	cc_bt_deepsleep()
	cc_bt_noscan()
	cc_bt_set_power_level(power_level)