import ab
from setuptools import setup


setup(
	name = 'ampy_batch',
	packages = ['ab'],
	version = ab.__version__,
	author = ab.__author__,
	description = 'An AMPY batch tool',
	url = 'https://gitee.com/walkline/a-batch-tool',
	license = 'MIT',
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
