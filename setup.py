import ab
from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as file:
	long_description = file.read()

setup(
	name = 'ampy-batch-tool',
	packages = ['ab'],
	version = ab.__version__,
	author = ab.__author__,
	author_email = ab.__email__,
	description = 'An adafruit-ampy batch tool',
	long_description = long_description,
	long_description_content_type = 'text/markdown',
	url = 'https://gitee.com/walkline/a-batch-tool',
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: Microsoft :: Windows',\
		'Environment :: Console',
	],
	provides = ['ab'],
	entry_points = {
		'console_scripts': [
			'ab = ab.__main__:main'
		],
	},
	install_requires = [
		'pyserial',
		'adafruit-ampy',
		'pyminifier'
	]
)

# python setup.py sdist upload

# pip install -U twine wheel setuptools
# python setup.py sdist bdist_wheel
# twine check dist/*
# twine upload --repository-url https://upload.pypi.org/legacy/ dist/*