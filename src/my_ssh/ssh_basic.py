#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

from paramiko import client
import src.my_config.config_basic as config_basic
from src.my_misc.my_decorator import hci_return_header_footer
from src.my_misc.my_logging import create_logger

log = create_logger()


class SSH:
	client = None
	shell = None
	transport = None

	def __init__(self, address, username, password):
		self.address = address
		self.username = username
		self.userPassword = password
		self.rootPassword = password
		log.info("Connecting to server on ip address {0}".format(str(self.address)))
		self.client = client.SSHClient()
		self.client.set_missing_host_key_policy(client.AutoAddPolicy())
		self.client.connect(self.address, username=self.username, password=self.userPassword, look_for_keys=False)

	@hci_return_header_footer()
	def send_command(self, command):
		if self.client:
			stdin, stdout, stderr = self.client.exec_command(command, get_pty=True)
			# stdin, stdout, stderr = self.client.exec_command('sudo ' + command)
			# stdin.write(self.rootPassword + '\n')
			stdin.flush()
			stdin.close()
			data = stdout.read().splitlines()
			data_filter = filter(None, data)  # remove all empty strings from a list of strings
			error = stderr.read().splitlines()
			error_filter = filter(None, error)  # remove all empty strings from a list of strings
			# data = stdout.readlines()
			# print(data)
			data_return = []
			error_return = []

			for line in data_filter:
				# print(str(line, 'utf8'))
				data_return.append(str(line, 'utf8'))
			# print(data_return)
			if len(data_return) != 0:
				log.info('\n'.join(data_return))

			for line in error_filter:
				error_return.append(str(line, 'utf8'))
			if len(error_return) != 0:
				log.info('\n'.join(error_return))

			while not stdout.channel.exit_status_ready():
				# Print data when available
				if stdout.channel.recv_ready():
					alldata = stdout.channel.recv(1024)
					prevdata = b"1"
					while prevdata:
						prevdata = stdout.channel.recv(1024)
						alldata += prevdata
					log.info(str(alldata, "utf8"))
			return data_return, error_return
		else:
			log.info("Connection not opened.")


def open_connection_ssh():
	"""
	Open SSH connection based on server, username and password
	:return: SSH connection
	"""
	ssh_server = config_basic.config_ssh_server()
	ssh_username = config_basic.config_ssh_username()
	ssh_password = config_basic.config_ssh_password()
	connection = SSH(ssh_server, ssh_username, ssh_password)
	return connection


"""
I finally figured out that .execute_command() is basically a single session,
so doing a .execute_command('cd scripts') and then executing the script with
another .execute_command() reverts back to your default directory.
The alternatives are to send all the commands at once separated
by a ; .execute_command('cd scripts; ./myscript.sh'),
or to use the .interactive() shell support.
Since I only needed to fire off this script I used the first solution.
"""
