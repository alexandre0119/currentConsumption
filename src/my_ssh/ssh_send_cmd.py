#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import src.my_ssh.ssh_basic as ssh_basic
import src.my_bt_case.bt_case as bt_case
import src.my_config.config_basic as config_basic
import time


# ssh_basic.open_connection_ssh().send_command('whoami')
# ssh_basic.open_connection_ssh().send_command('ls -l; pwd')
# dir_run = 'cd' + ' ' + str(config['Directory'].get('BluetoothScriptDirectory')) + ';ls;' + './'


def bt_init():
	"""
	Init BT test Init class
	:return: Init class
	"""
	chip_version = config_basic.config_chip_version()
	dut = config_basic.config_dut()
	ref = config_basic.config_ref()
	return bt_case.Init(chip_version, dut, ref)


def bt_power_init():
	"""
	Init BT test power level setting class
	:return: BT Power level class
	"""
	chip_version = config_basic.config_chip_version()
	dut = config_basic.config_dut()
	ref = config_basic.config_ref()
	return bt_case.PowerLevel(chip_version, dut, ref)


def bt_bt_init():
	"""
	Init BT related test cases
	:return: BT test case class
	"""
	chip_version = config_basic.config_chip_version()
	dut = config_basic.config_dut()
	ref = config_basic.config_ref()
	return bt_case.BT(chip_version, dut, ref)


def bt_ble_init():
	"""
	Init BLE related test cases
	:return: BLE test case class
	"""
	chip_version = config_basic.config_chip_version()
	dut = config_basic.config_dut()
	ref = config_basic.config_ref()
	return bt_case.BLE(chip_version, dut, ref)


def cc_bt_reset(hci):
	ssh_basic.open_connection_ssh().send_command(bt_bt_init().bt_reset(hci))


def cc_bt_deepsleep():
	ssh_basic.open_connection_ssh().send_command(bt_bt_init().bt_deepsleep())


def cc_bt_noscan():
	ssh_basic.open_connection_ssh().send_command(bt_bt_init().bt_noscan())


def cc_bt_set_power_level(power_level):
	ssh_basic.open_connection_ssh().send_command(bt_power_init().bt_set_power_level(power_level))


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
	ssh_basic.open_connection_ssh().send_command(bt_bt_init().bt_idle())
	time.sleep(2)


def cc_bt_pscan(hci_dut, hci_ref, power_level):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	ssh_basic.open_connection_ssh().send_command(bt_bt_init().bt_pscan())
	time.sleep(2)


def cc_bt_iscan(hci_dut, hci_ref, power_level):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	ssh_basic.open_connection_ssh().send_command(bt_bt_init().bt_iscan())
	time.sleep(2)


def cc_bt_piscan(hci_dut, hci_ref, power_level):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	ssh_basic.open_connection_ssh().send_command(bt_bt_init().bt_piscan())
	time.sleep(2)


def cc_bt_acl_sniff_1dot28s_master(hci_dut, dut_addr, hci_ref, ref_addr, power_level):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	ssh_basic.open_connection_ssh().send_command(bt_bt_init().bt_acl_sniff_1dot28s_master(dut_addr, ref_addr))
	time.sleep(2)


def cc_bt_acl_sniff_0dot5s_master(hci_dut, dut_addr, hci_ref, ref_addr, power_level):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	ssh_basic.open_connection_ssh().send_command(bt_bt_init().bt_acl_sniff_0dot5s_master(dut_addr, ref_addr))
	time.sleep(2)


def cc_bt_sco_hv3(hci_dut, dut_addr, hci_ref, ref_addr, power_level):
	cc_bt_acl_sniff_1dot28s_master(hci_dut, dut_addr, hci_ref, ref_addr, power_level)
	time.sleep(1)
	ssh_basic.open_connection_ssh().send_command(bt_bt_init().bt_sco_hv3(ref_addr))
	time.sleep(5)


def cc_bt_sco_ev3(hci_dut, dut_addr, hci_ref, ref_addr, power_level):
	cc_bt_acl_sniff_1dot28s_master(hci_dut, dut_addr, hci_ref, ref_addr, power_level)
	time.sleep(1)
	ssh_basic.open_connection_ssh().send_command(bt_bt_init().bt_sco_ev3(ref_addr))
	time.sleep(5)


def cc_ble_adv_1dot28s_3channel(hci_dut='hci0', hci_ref='hci1', power_level='0', enable_ble_adv=1):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	ssh_basic.open_connection_ssh().send_command(bt_ble_init().ble_adv_1dot28s_3channel(enable_ble_adv))
	time.sleep(2)


def cc_ble_scan_1dot28s(hci_dut='hci0', hci_ref='hci1', power_level=0, enable_ble_scan=1):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	ssh_basic.open_connection_ssh().send_command(bt_ble_init().ble_scan_1dot28s(enable_ble_scan))
	time.sleep(2)


def cc_ble_scan_1s(hci_dut='hci0', hci_ref='hci1', power_level=0, enable_ble_scan=1):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	ssh_basic.open_connection_ssh().send_command(bt_ble_init().ble_scan_1s(enable_ble_scan))
	time.sleep(2)


def cc_ble_scan_10ms(hci_dut='hci0', hci_ref='hci1', power_level=0, enable_ble_scan=1):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	ssh_basic.open_connection_ssh().send_command(bt_ble_init().ble_scan_10ms(enable_ble_scan))
	time.sleep(2)


def cc_ble_connection_1dot28s(hci_dut='hci0', hci_ref='hci1', ref_addr='11.22.33.44.55.66', power_level='0'):
	cc_bt_init_status(hci_dut, hci_ref, power_level)
	time.sleep(1)
	ssh_basic.open_connection_ssh().send_command(bt_ble_init().ble_connection_1dot28s(ref_addr))
	time.sleep(10)
