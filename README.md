<h1 align="center">AMPY Batch Tool</h1>

<p align="center"><img src="https://img.shields.io/badge/Licence-MIT-green.svg?style=for-the-badge" /></p>

### 项目介绍

[AMPY Batch Tool](https://pypi.org/project/ampy-batch-tool/) 简称`ab`，可以批量将项目中指定的文件夹或文件上传到`MicroPython`开发板

### 如何安装

#### 在线安装（推荐）

```bash
# 安装
$ pip install ampy-batch-tool

# 更新
$ pip install --upgrade ampy-batch-tool
```

#### 离线安装

首先克隆或下载项目源文件压缩包并解压缩，然后进入项目文件夹运行命令

```bash
$ python setup.py install
```

```bash
# for local develop
$ pip install -e .
```

### 如何上传文件

* 在你的项目文件夹下新建`abconfig`文件（`ab`工具默认查找该配置文件，也可以手动指定其它文件）

* 配置文件中填写需要上传的文件夹或文件，每行一个，以`#`号开头的行表示需要排除的文件夹或文件，例如：

	```doc
	drivers/
	services/
	main.py
	not_exists/

	# services/websocket.py
	# .git/
	```
* 在需要上传项目文件的时候执行如下命令即可

	```bash
	$ ab
	```

* 如果找不到或者未手动指定配置文件，则显示使用说明

* 完整输出内容

	```docs
	Port List:
        [1] COM8 - Silicon Labs CP210x USB to UART Bridge (COM8)
        [2] COM1 - 通信端口 (COM1)
	Choose a port: 1

	File List (3):
	- drivers/button.py
	- services/mqtt.py
	- main.py

	Dir List (3)
	- drivers
	- drivers/others
	- services

	Not Found List (1)
	- not_exists

	Making dirs on board...
	- drivers exist
	- drivers/others exist
	- services exist

	Upload files to board...
	- uploading drivers/button.py (1/3)
	- uploading services/mqtt.py (2/3)
	- uploading main.py (3/3)

	Upload Finished
	```

### 如何进入`repl`模式

```bash
$ ab --repl
Port List:
    [1] COM3 - Silicon Labs CP210x USB to UART Bridge (COM3)
    [2] COM1 - 通信端口 (COM1)
Choose a port: 1

Miniterm for MicroPython REPL
    Ctrl-Z - Quit
    Ctrl-N - Help
    Ctrl-X - Kill main.py
    Ctrl-Y - Serial Info
    Ctrl-L - Run last file
    Ctrl-R - Run local file
    Ctrl-T - Run board file
    Ctrl-G - Run clipboard code

>>> help()
Welcome to MicroPython on the ESP32!

For generic online docs please visit http://docs.micropython.org/
>>>
```
#### `repl`模式快捷键

* <kbd>Ctrl</kbd> + <kbd>Z</kbd>：退出`repl`
* <kbd>Ctrl</kbd> + <kbd>X</kbd>：一键删除`main.py`文件
* <kbd>Ctrl</kbd> + <kbd>G</kbd>：将剪贴板中的代码粘贴到`repl`中
* <kbd>Ctrl</kbd> + <kbd>Y</kbd>：显示串口相关设置
* <kbd>Ctrl</kbd> + <kbd>O</kbd>：显示快捷键说明
* <kbd>Ctrl</kbd> + <kbd>R</kbd>：运行本地文件
* <kbd>Ctrl</kbd> + <kbd>T</kbd>：运行远程文件
* <kbd>Ctrl</kbd> + <kbd>L</kbd>：再次运行上次的本地文件

#### 一键删除`main.py`文件

有些时候由于在代码中写入死循环，导致无法删除或者重新上传文件的情况，可以尝试使用快捷键<kbd>Ctrl</kbd> + <kbd>X</kbd>对`main.py`文件进行删除

#### 运行本地`.py`文件

快捷键为：<kbd>Ctrl</kbd> + <kbd>R</kbd>

```docs
>>> Run local file
    [1] upload_to_pypi.py
    [2] setup.py
    [3] local.py
    [4] ab\__main__.py
    [5] ab\__init__.py
    [6] ab\pyboard.py
    [7] ab\miniterm.py
Choose a file: 3

boot.py - FILE
client - PATH
drivers - PATH
onboard.py - FILE

this is a local py file
>>>
```

#### 运行远程`py`文件

也就是运行开发板上的文件，快捷键为：<kbd>Ctrl</kbd> + <kbd>T</kbd>

```docs
>>>
Run onboard file
    [1] /boot.py
    [2] /drivers/ssd1306.py
    [3] /onboard.py
Choose a file: 3

this is a onboard py file
>>>
```

#### 运行剪贴板中的代码段

快捷键为：<kbd>Ctrl</kbd> + <kbd>G</kbd>

> 需要注意复制的代码段的缩进

```docs
>>> Run clipboard code

HZK Info: //client/combined.bin
    file size : 303520
  font height : 16
    data size : 32
    scan mode : Horizontal
   byte order : LSB
   characters : 8932

slave id: 60
>>>
```

#### 重新运行之前的文件

快捷键为：<kbd>Ctrl</kbd> + <kbd>L</kbd>

> 注意：只能重新运行上一次的**本地文件**
>
> 因为开发板上文件的运行方式不同，所以暂不支持一键重新运行

### 参数说明

* `-h`：显示使用说明
* ~~`-m`：使用`minify`工具压缩代码（功能未实现）~~
* `-q`：屏蔽操作过程中的相关提示
* `-s`：模拟操作过程，不实际上传文件
* `--repl`：进入`repl`模式
* `--readme`：在网页中显示使用说明

### 已知问题

1. ~~调用`ampy`工具新建文件夹的时候如果文件夹已存在，则会抛出异常且无法捕捉~~

2. 偶尔出现无法进入`raw_repl`模式的问题，重新运行一次即可解决

### 更新记录

* `v0.5`：
	* 调整了`repl`模式下的快捷键
	* `repl`模式增加运行本地文件功能
	* `repl`模式增加运行远程文件功能
	* 美化`repl`模式提示内容
* `v0.4.2`：`repl`模式增加一键删除`main.py`文件功能
* `v0.4.1`：`repl`模式增加粘贴代码功能
* `v0.4`：增加进入`repl`模式菜单和相关功能
* `v0.3.2`：修复由于`v0.3.1`导致的分隔路径错误问题
* `v0.3.1`：修复上传文件时字符转义的问题
* `v0.3`：
	* 重构了获取所有文件和文件夹列表功能
	* 增加了显示网页版使用说明的参数
	* `enter_raw_repl()`中增加延时，尝试解决`已知问题2`

* `v0.2.2`：修复某些开发板不能读取串口数据的问题（如`安信可 ESP32C3 系列开发板`）
* `v0.2.1`：修复导入模块路径问题
* `v0.2`：
	* 使用 [pyboard.py](https://github.com/micropython/micropython/blob/master/tools/pyboard.py) 替代`ampy`以提升文件上传效率，并解决`已知问题 1`
	* 禁用了代码压缩功能，使用 [pyminifier](http://liftoff.github.io/pyminifier/index.html) 压缩代码会出现问题
	* 删除指定临时目录参数

* `v0.1.1`：尝试上传到 [PyPI](https://pypi.org/)
* `v0.1`：完成基本功能

### 附录：`repl`快捷键汇总

排除掉`MicroPython`已经使用的，以及与各种编辑器和终端发生冲突的，而且只能使用字母键，所以实际可用的按键其实并不多，凑合选择了一组，就是现在使用的这些

```bash
# 不可用的
Ctrl +:
	A - raw repl mode
	B - soft reset / exit raw repl
	C - interrupt run / cancel paste mode
	D - soft reset / finish paste mode
	E - paste mode
	I - list imported modules
	J, M - enter key
	P - up key
	V - mostly paste

# 之前使用的
Ctrl +:
	L - show serial port info
	O - show help
	R - run local pyfile
	T - run onboard pyfile
	U - run code in clipboard
	] - quit
	[ - delete onboard file main.py

# 现在使用的
Ctrl +:
	Z - quit
	X - delete onboard file main.py
	N - show help
	Y - show serial port info
	L - run last pyfile (local / onboard)
	R - run local pyfile
	T - run onboard pyfile
	G - run code in clipboard

# 可用的 (闲置的)
Ctrl +:
	F - vsc 冲突
	G
	H - bs 冲突
	K
	N
	Q
	S
	W
	X
	Y
	Z
```

### 合作交流

* 联系邮箱：<walkline@163.com>
* QQ 交流群：
	* 走线物联：163271910
	* 扇贝物联：31324057

<p align="center"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_walkline.png" width="300px" alt="走线物联"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_bigiot.png" width="300px" alt="扇贝物联"></p>
