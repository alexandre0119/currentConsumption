#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import src.my_ssh as my_ssh
import src.my_bt_case as my_bt_case
import src.my_config as my_config
import time


# my_ssh.open_connection_ssh().send_command('whoami')
# my_ssh.open_connection_ssh().send_command('ls -l; pwd')
# dir_run = 'cd' + ' ' + str(config['Directory'].get('BluetoothScriptDirectory')) + ';ls;' + './'


def bt_init():
	"""
	Init BT test Init class
	:return: Init class
	"""
	chip_version = my_config.config_chip_version()
	dut = my_config.config_dut()
	ref = my_config.config_ref()
	return my_bt_case.Init(chip_version, dut, ref)


def bt_power_init():
	"""
	Init BT test power level setting class
	:return: BT Power level class
	"""
	chip_version = my_config.config_chip_version()
	dut = my_config.config_dut()
	ref = my_config.config_ref()
	return my_bt_case.PowerLevel(chip_version, dut, ref)


def bt_bt_init():
	"""
	Init BT related test cases
	:return: BT test case class
	"""
	chip_version = my_config.config_chip_version()
	dut = my_config.config_dut()
	ref = my_config.config_ref()
	return my_bt_case.BT(chip_version, dut, ref)


def bt_ble_init():
	"""
	Init BLE related test cases
	:return: BLE test case class
	"""
	chip_version = my_config.config_chip_version()
	dut = my_config.config_dut()
	ref = my_config.config_ref()
	return my_bt_case.BLE(chip_version, dut, ref)


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
	time.sleep(1)
	cc_bt_reset(hci_ref)
	time.sleep(1)
	cc_bt_deepsleep()
	time.sleep(1)
	cc_bt_noscan()
	time.sleep(1)
	cc_bt_set_power_level(power_level)
	time.sleep(1)


def cc_bt_idle(hci_dut, hci_ref, power_level):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	my_ssh.open_connection_ssh().send_command(bt_bt_init().bt_idle())
	time.sleep(2)


def cc_bt_pscan(hci_dut, hci_ref, power_level):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	my_ssh.open_connection_ssh().send_command(bt_bt_init().bt_pscan())
	time.sleep(2)


def cc_bt_iscan(hci_dut, hci_ref, power_level):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	my_ssh.open_connection_ssh().send_command(bt_bt_init().bt_iscan())
	time.sleep(2)


def cc_bt_piscan(hci_dut, hci_ref, power_level):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	my_ssh.open_connection_ssh().send_command(bt_bt_init().bt_piscan())
	time.sleep(2)


def cc_bt_acl_sniff_1dot28s_master(hci_dut, dut_addr, hci_ref, ref_addr, power_level):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	my_ssh.open_connection_ssh().send_command(bt_bt_init().bt_acl_sniff_1dot28s_master(dut_addr, ref_addr))
	time.sleep(1)
