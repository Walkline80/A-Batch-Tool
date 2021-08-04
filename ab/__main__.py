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
import shutil

try:
	from pyboard import Pyboard, stdout_write_bytes
except ModuleNotFoundError:
	from .pyboard import Pyboard, stdout_write_bytes

try:
	from __init__ import __version__
except ModuleNotFoundError:
	from . import __version__

try:
	stdout = sys.stdout.buffer
except AttributeError:
	stdout = sys.stdout


CONFIG_FILE = 'abconfig'

CMD_MKDIRS = \
'''
for dir in {}:
  try:
    import os
    os.mkdir(dir)
  except OSError as ose:
    if str(ose) == '[Errno 17] EEXIST':
      if not {}:
        print('    {{}}/ exist'.format(dir))
    else:
      print(ose)
'''


parser = None

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

def choose_a_port():
	port_list = [str(port) for port in comports()]

	print('Port List:')
	for index, port in enumerate(port_list, start=1):
		print(f'    [{index}] {port}')
	
	selected_port = None

	while True:
		try:
			selected_port = int(input('Choose a port: '))

			assert type(selected_port) is int and 0 < selected_port <= len(port_list)
			
			return port_list[selected_port - 1].split(' - ')[0]
		except KeyboardInterrupt:
			exit()
		except:
			pass

def parse_config_file(config_file):
	includes = []
	excludes = []

	with open(config_file, 'r') as config:
		lines = config.read().splitlines()

	for line in lines:
		if line:
			if line.startswith('# '):
				excludes.append(line.split()[1])
			else:
				includes.append(line)

	return includes, excludes

def filter_files_and_dirs(includes, excludes):
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

	if 'main.py' in include_files:
		include_files.remove('main.py')
		include_files.append('main.py')

	return include_files, include_dirs

def ab(options, files):
	global parser

	config_file = CONFIG_FILE if not files else files[0]

	if not os.path.exists(config_file):
		parser.print_help()
		exit(0)

	if options.simulate:
		options.quiet = False

	port = '' if options.simulate else choose_a_port()

	includes, excludes = parse_config_file(config_file)
	include_files, include_dirs = filter_files_and_dirs(includes, excludes)

	if not options.quiet:
		print(f'\nFile List ({len(include_files)}):')
		print('{}'.format('\n'.join([f'    {file}' for file in include_files])))
		
		print(f'\nDir List ({len(include_dirs)})')
		print('{}'.format('\n'.join([f'    {dir}/' for dir in include_dirs])))

		print('\nMaking dirs on board...')

	if options.simulate:
		print('Upload files to board...')
		print('Upload finished')

		exit(0)

	pyboard = Pyboard(port)
	pyboard.enter_raw_repl()

	cmd = CMD_MKDIRS.format(include_dirs, options.quiet)
	pyboard.exec(cmd, data_consumer=stdout_write_bytes)

	temp_dir = None

	# if options.minify:
	# 	temp_dir = tempfile.TemporaryDirectory(prefix='ab_')

	# 	for dir in include_dirs:
	# 		dest_dir = os.path.join(temp_dir.name, dir)
	# 		if not os.path.exists(dest_dir):
	# 			os.mkdir(dest_dir)
	
	# 	for file in include_files:
	# 		dest_file = os.path.join(temp_dir.name, file)
	# 		shutil.copyfile(file, dest_file)

	print('{}'.format('\nUpload files to board...' if not options.quiet else ''))

	for index, file in enumerate(include_files, start=1):
		if not options.quiet:
			print(f'    uploading {file} ({index}/{len(include_files)})')

		pyboard.fs_put(os.path.join(temp_dir.name if temp_dir else '', file), file)

	pyboard.exit_raw_repl()

	if temp_dir:
		temp_dir.cleanup()

	print('\nUpload Finished')

def main():
	global parser

	usage = '%prog [options] [config_file]'

	parser = OptionParser(usage, version=f'ampy batch tool ({__version__})')
	parser.disable_interspersed_args()

	# parser.add_option(
	# 	'-m', '--minify',
	# 	action = 'store_true',
	# 	dest = 'minify',
	# 	default = False,
	# 	help = 'minify .py files which put to board'
	# )
	# parser.add_option(
	# 	'-t', '--temp-path',
	# 	dest = 'temp_path',
	# 	default = None,
	# 	metavar = '<temp_path>',
	# 	help = 'put all files into a specified path'
	# )
	parser.add_option(
		'-q', '--quiet',
		action = 'store_true',
		dest = 'quiet',
		default = False,
		help = 'no relevant information output'
	)
	parser.add_option(
		'-s', '--simulate',
		action = 'store_true',
		dest = 'simulate',
		default = False,
		help = 'just print command lines for review'
	)

	options, files = parser.parse_args()

	ab(options, files)


if __name__ == '__main__':
	main()
