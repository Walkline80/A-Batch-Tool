#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, shutil


REMOVE_DIRS = ['ampy_batch_tool.egg-info', 'build', 'dist']

print('removing build folders...\n')

for dir in REMOVE_DIRS:
	shutil.rmtree(dir)

print('building packages...\n')
os.system('python setup.py sdist bdist_wheel')

print('\nchecking packages...\n')
os.system('twine check dist/*')

while True:
	try:
		result = input('upload packages now? [Y/n]')

		assert result in ('', 'Y', 'y', 'n')

		if result in ('', 'Y', 'y'):
			os.system('twine upload --repository-url https://upload.pypi.org/legacy/ dist/*')

		break
	except KeyboardInterrupt:
		exit(0)
	except:
		pass

print('\ndone')
