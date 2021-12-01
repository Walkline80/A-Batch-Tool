"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/a-batch-tool
"""
from optparse import OptionParser
from serial.tools.list_ports import comports
import os
import shutil, tempfile

try:
	from pyboard import Pyboard, stdout_write_bytes
except ModuleNotFoundError:
	from .pyboard import Pyboard, stdout_write_bytes

try:
	from __init__ import __version__
except ModuleNotFoundError:
	from . import __version__


DEFAULT_CONFIG_FILE = 'abconfig'
EXCLUDE_PREFIX = '#'
RUN_AFTER_UPLOAD_PREFIX = '!'

CMD_MKDIRS = \
'''
for dir in {}:
  try:
    import os
    os.mkdir(dir)
  except OSError as ose:
    if str(ose) == '[Errno 17] EEXIST':
      if not {}:
        print('- {{}} exist'.format(dir))
    else:
      print(ose)
'''

parser = None

def list_all_files_and_dirs(includes, excludes):
	dir_list = []
	file_list = []
	bad_list = []

	for include in includes:
		if not os.path.exists(include):
			bad_list.append(include)
			continue

		if os.path.isdir(include):
			for root, _, files in os.walk(include):
				if root in excludes:
					continue

				for file in files:
					full_path = os.path.join(root, file)

					if full_path not in excludes:
						file_list.append(full_path)
		else:
			if include not in excludes:
				file_list.append(include)

	for file in file_list:
		splited_path = os.path.split(file)[0].split(os.path.sep)

		for index in range(len(splited_path) + 1):
			full_path = os.path.sep.join(splited_path[:index])

			if full_path not in dir_list and full_path:
				dir_list.append(full_path)

	for items in [file_list, dir_list, bad_list]:
		for index, item in enumerate(items):
			items[index] = item.replace('\\', '/')

	file_list.sort()
	dir_list.sort()
	bad_list.sort()

	if 'main.py' in file_list:
		file_list.remove('main.py')
		file_list.append('main.py')

	return file_list, dir_list, bad_list

def choose_a_port():
	port_list = [str(port) for port in comports()]

	print('Port List:')
	for index, port in enumerate(port_list, start=1):
		if index == 1:
			print(f'\x1b[32m    [{index}] {port}\033[0m')
		else:
			print(f'    [{index}] {port}')

	selected_port = None

	while True:
		try:
			selected_port = input('Choose a port: ')
			
			if selected_port == '':
				return port_list[0].split(' - ')[0]

			selected_port = int(selected_port)

			assert type(selected_port) is int and 0 < selected_port <= len(port_list)
			
			return port_list[selected_port - 1].split(' - ')[0]
		except KeyboardInterrupt:
			exit()
		except:
			pass

def parse_config_file(config_file):
	includes = []
	excludes = []
	run_file = None

	with open(config_file, 'r') as config:
		lines = config.read().splitlines()

	for line in lines:
		if line:
			if line.startswith(EXCLUDE_PREFIX):
				excludes.append(os.path.normpath(line.strip(EXCLUDE_PREFIX + '/\\').strip()))
			elif line.startswith(RUN_AFTER_UPLOAD_PREFIX):
				run_file_temp = os.path.normpath(line.strip(RUN_AFTER_UPLOAD_PREFIX + '/\\').strip())
				includes.append(run_file_temp)

				if os.path.exists(run_file_temp) and not os.path.isdir(run_file_temp) and run_file_temp != 'main.py': run_file = run_file_temp
			else:
				includes.append(os.path.normpath(line.strip('/\\')))

	return includes, excludes, run_file

def ab(options, files):
	global parser

	config_file = DEFAULT_CONFIG_FILE if not files else files[0]

	if not os.path.exists(config_file):
		parser.print_help()
		exit(0)

	if options.simulate:
		options.quiet = False

	includes, excludes, _ = parse_config_file(config_file)
	include_files, include_dirs, bad_list = list_all_files_and_dirs(includes, excludes)

	if not include_files:
		print('Nothing to do!')
		exit(0)

	port = '' if options.simulate else choose_a_port()

	if not options.quiet:
		print(f'\nFile List ({len(include_files)}):')
		print('{}'.format('\n'.join([f'- {file}' for file in include_files])))

		if include_dirs:
			print(f'\nDir List ({len(include_dirs)})')
			print('{}'.format('\n'.join([f'- {dir}' for dir in include_dirs])))

		if bad_list:
			print(f'\nNot Found List ({len(bad_list)})')
			print('{}'.format('\n'.join([f'- {dir_or_file}' for dir_or_file in bad_list])))

		print('\nMaking dirs on board...')

	if options.simulate:
		print('Upload files to board...')
		print('Simulate finished')
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
			print(f'- uploading {file} ({index}/{len(include_files)})')

		pyboard.fs_put(os.path.join(temp_dir.name if temp_dir else '', file), file)

	pyboard.exit_raw_repl()

	if temp_dir:
		temp_dir.cleanup()

	print('\nUpload Finished')

def main():
	global parser

	usage = \
'''%prog [OPTIONS] [CONFIG FILE]

  ampy batch tool - MicroPython files upload tool'''

	parser = OptionParser(usage, version=f'ampy batch tool ({__version__})')
	parser.disable_interspersed_args()

	# parser.add_option(
	# 	'-m', '--minify',
	# 	action = 'store_true',
	# 	dest = 'minify',
	# 	default = False,
	# 	help = 'minify .py files which put to board'
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
	parser.add_option(
		'--repl',
		action = 'store_true',
		dest = 'repl',
		default = False,
		help = 'enter raw repl mode'
	)
	parser.add_option(
		'--flash',
		action = 'store_true',
		dest = 'flash',
		help = 'an esptool shell'
	)
	parser.add_option(
		'--readme',
		action = 'store_true',
		dest = 'readme',
		help = 'show readme manual in web browser'
	)

	options, files = parser.parse_args()

	if options.readme:
		import webbrowser
		webbrowser.open('https://gitee.com/walkline/a-batch-tool')
	elif options.repl:
		try:
			from .miniterm import main
		except ImportError:
			from miniterm import main
		port = choose_a_port()
		main(default_port=port)
	elif options.flash:
		try:
			from .flash import run_esptool_shell
		except ImportError:
			from flash import run_esptool_shell
		run_esptool_shell()
	else:
		ab(options, files)


if __name__ == '__main__':
	main()
