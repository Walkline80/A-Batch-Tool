"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/a-batch-tool
"""
from optparse import OptionParser
from serial.tools.list_ports import comports
import os, sys
import tempfile
from time import sleep

try:
	from __init__ import __version__
except ModuleNotFoundError:
	from . import __version__


CONFIG_FILE = 'abconfig'
TEMP_PATH = 'temp'

parser = None

def get_serial_ports():
	return [str(port) for port in comports()]

def list_all_files(root, dir=False):
	dir_or_files = []

	if os.path.isfile(root):
		if not dir:
			dir_or_files.append(root.strip('/'))
	else:
		if dir:
			dir_or_files.append(root.strip('/'))

		for path in os.listdir(root):
			full_path = os.path.join(root, path)

			if os.path.isdir(full_path):
				if dir:
					dir_or_files.append(full_path.strip('/'))

				dir_or_files.extend(list_all_files(full_path))
			elif os.path.isfile(full_path) and not dir:
				dir_or_files.append(full_path)

	return dir_or_files

def ab(options, files):
	global parser

	config_file = CONFIG_FILE if not files else files[0]

	if not os.path.exists(config_file):
		parser.print_help()
		exit(0)

	includes = []
	excludes = []

	with open(config_file, 'r') as config:
		lines = config.readlines()

	for line in lines:
		line = line.strip('\n')

		if line:
			if line.startswith('# '):
				excludes.append(line.split()[1])
			else:
				includes.append(line)

	include_files = []
	excluede_files = []
	include_dirs = []
	excluede_dirs = []

	for include in includes:
		include_files.extend(list_all_files(include))
	
	for exclude in excludes:
		excluede_files.extend(list_all_files(exclude))
	
	for include in includes:
		include_dirs.extend(list_all_files(include, True))

	for exclude in excludes:
		excluede_dirs.extend(list_all_files(exclude, True))

	include_files = list(set(include_files) - set(excluede_files))
	include_dirs = list(set(include_dirs) - set(excluede_dirs))

	include_files.sort()
	include_dirs.sort()

	print(f'include_files: {include_files}')
	print(f'include_dirs: {include_dirs}')

	port_list = get_serial_ports()

	print('Port List:')
	for index, port in enumerate(port_list, start=1):
		print(f'    [{index}] {port}')
	
	selected_port = None
	while True:
		try:
			selected_port = int(input('Choose a port: '))

			assert type(selected_port) is int and 0 < selected_port <= len(port_list)
			break
		except KeyboardInterrupt:
			exit()
		except:
			pass

	selected_port = port_list[selected_port - 1].split(' - ')[0]

	for dir in include_dirs:
		# os.system(f'ampy -p {selected_port} -b 115200 -d 0.2 mkdir {dir}')
		print(f'ampy -p {selected_port} -b 115200 -d 0.2 mkdir {dir}')

		sleep(0.2)
	
	if not options.minify:
		if not options.temp_path:
			options.temp_path = TEMP_PATH

		if not os.path.exists(options.temp_path):
			os.mkdir(options.temp_path)
	else:
		for index, file in enumerate(include_files, start=1):
			print(f'upload {index}/{len(include_files)}')
			# os.system(f'ampy -p {selected_port} -b 115200 -d 0.2 put {file}')
			print(f'ampy -p {selected_port} -b 115200 -d 0.2 put {file}')
			sleep(0.2)
		
		print('upload finished')

def main():
	global parser

	usage = '%prog [options] [config_file]'

	parser = OptionParser(usage, version=__version__)
	parser.disable_interspersed_args()

	parser.add_option(
		'-m', '--minify',
		action = 'store_true',
		dest = 'minify',
		default = True,
		help = 'minify .py files which put to board'
	)
	parser.add_option(
		'-t', '--temp-path',
		dest = 'temp_path',
		default = None,
		metavar = '<temp_path>',
		help = 'put all files into a specified path'
	)

	options, files = parser.parse_args()

	ab(options, files)


if __name__ == '__main__':
	class Options:
		def __init__(self, args_dict):
			self.minify = True
			self.temp_path = None

		def __str__(self):
			return str({'minify': self.minify, 'temp_path': self.temp_path})

	options = Options({'minify': True, 'temp_path': None})
	files = []

	ab(options, files)

