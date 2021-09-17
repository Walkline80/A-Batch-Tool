"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/a-batch-tool
"""
from serial.tools.list_ports import comports
import os

EXCLUDE_DIRS = ['.git', '.vscode', '__pycache__', 'build', 'dist']


def choose_an_option(title, options):
	print(f'\n{title} List:')
	for index, option in enumerate(options, start=1):
		if index == 1:
			print(f'\x1b[32m  [{index}] {option}\033[0m')
		else:
			print(f'  [{index}] {option}')

	selected = None

	while True:
		try:
			selected = input('Choose an option: ')

			if selected == '':
				return options[0]

			selected = int(selected)

			assert type(selected) is int and 0 < selected <= len(options)
			
			return options[selected - 1]
		except KeyboardInterrupt:
			exit()
		except:
			pass

def list_files(root='.', levels=2, extention='.bin'):
	'''
	递归获取指定目录及指定层数子目录下指定扩展名的文件
	'''
	global EXCLUDE_DIRS

	files = []

	if levels == 0:
		return files

	for dir in os.listdir(root):
		fullpath = os.path.join(root, dir)
		if os.path.isdir(fullpath):
			if dir in EXCLUDE_DIRS:
				continue
			files.extend(list_files(fullpath, levels - 1))
		else:
			if fullpath.endswith(extention):
				files.append(fullpath.replace('.\\', ''))

	return files

def run_esptool_shell():
	__CHIP_LIST = ['auto', 'esp8266', 'esp32', 'esp32c3', 'esp32s2', 'esp32s3beta2', 'esp32s3beta3', 'esp32c6beta']
	__CHIP = '--chip {}'
	__PORT = '--port {}'
	__BAUD = '--baud 921600'
	__BEFORE = '--before default_reset'
	__AFTER = '--after hard_reset'
	__MODE = '--flash_mode dio'
	__SIZE = '--flash_size detect'
	__FREQ = '--flash_freq 40m'
	__ADDR = ['0x1000', '0x0 - for esp32c3']

	print('An esptool shell')

	port_list = [str(port) for port in comports()]
	port = choose_an_option('Port', port_list)
	__PORT = __PORT.format(port.split(' - ')[0])

	chip = choose_an_option('Chip', __CHIP_LIST)
	__CHIP = __CHIP.format(chip)

	addr = choose_an_option('Address', __ADDR).split(' - ')[0]

	firmware_list = list_files()

	if len(firmware_list) < 0:
		print('no firmware file found')
		exit()

	firmware = choose_an_option('Firmware', firmware_list)
	
	earse_command = f'esptool {__PORT} {__BAUD} {__CHIP} erase_flash'
	write_command = f'esptool {__PORT} {__BAUD} {__CHIP} {__BEFORE} {__AFTER} write_flash {__MODE} {__SIZE} {__FREQ} {addr} {firmware}'
	
	try:
		if os.system(earse_command) == 0:
			os.system(write_command)
	except OSError as ose:
		print(ose)


if __name__ == '__main__':
	run_esptool_shell()
