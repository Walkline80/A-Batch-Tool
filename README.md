<h1 align="center">AMPY Batch Tool</h1>

<p align="center"><img src="https://img.shields.io/badge/Licence-MIT-green.svg?style=for-the-badge" /></p>

### 项目介绍

[AMPY Batch Tool](https://pypi.org/project/ampy-batch-tool/) 简称`ab`，可以批量将项目中指定的文件夹或文件上传到`MicroPython`开发板

### 痛点问题

使用`MicroPython`写代码玩板子的时候我遇到过一些看似可以忍受但内心不停在咆哮的痛点问题

比如最早使用`PyCharm`写代码，遇到的问题是上传文件太慢，这个是看似可以忍受的，但不能忍的是经常性的出现上传失败的问题，放弃

后来使用过`rshell-lite`，纯命令行工具，不支持批量文件和文件夹上传，这对只写单文件项目的人来说问题不大，不过我喜欢把项目文件分类保存，放弃

现在使用`VS Code`+`RT-Thread`插件，这个插件支持文件夹上传了，但速度依然很慢，而且不支持`排除文件、文件夹`功能，但最大的问题是它会在后台不停的运行一个串口检测程序，浪费内存可以忍，不能忍的是当打开第二个`VS Code`窗口的时候，前一个已经连接的串口会被强迫断开，而且作者已经停更了，这个不放弃，改改脚本还可以当做代码补全工具使用

上面说到上传速度慢的问题，归根结底是因为它们上传文件的模式有问题，大概流程是这样的：

1. 打开串口
2. 创建文件夹、上传文件
3. 关闭串口
4. 重复第一步，直到最后一个文件上传完毕

所以问题就出现在不停打开关闭串口上了，要解决问题也很简单，使用 [pyboard.py](https://github.com/micropython/micropython/blob/master/tools/pyboard.py) 替代`ampy`工具，然后：

1. 打开串口
2. 创建所有文件夹、上传所有文件
3. 关闭串口

简单粗暴，有效果！

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

* 在你的项目文件夹下新建`abconfig`配置文件（`ab`工具默认查找该配置文件，也可以手动指定其它文件）

* 配置文件中填写需要上传的文件夹或文件，每行一个，例如：

	```doc
	drivers/
	!test.py
	main.py
	!services/
	not_exists/

	#services/websocket.py
	# .git/
	```

	> 以`#`号开头的行：上传时排除的文件夹或文件
	>
	> 以`!`号开头的行：在`repl`模式下上传文件后立即运行该文件

* 在需要上传项目文件的时候执行如下命令即可

	```bash
	$ ab

	# 或

	$ ab abconfig
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

### REPL 模式使用说明

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
	Ctrl-U - Upload files to board

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
* <kbd>Ctrl</kbd> + <kbd>U</kbd>：上传配置文件中的文件，并运行指定文件

#### 一键删除`main.py`文件

有些时候由于在代码中写入死循环，导致无法删除或者重新上传文件的情况，可以尝试使用这个功能，快捷键为：<kbd>Ctrl</kbd> + <kbd>X</kbd>

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

#### 运行远程`.py`文件

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

> 注意：只能重新运行上一次的`本地文件`和使用快捷键 <kbd>Ctrl</kbd> + <kbd>U</kbd> 上传并运行的`远程文件`
>
> 因为开发板上文件的运行方式不同，所以暂不支持一键重新运行

#### 上传配置文件中指定的文件

省去每次上传文件都要退出`repl`模式的麻烦，快捷键为：<kbd>Ctrl</kbd> + <kbd>U</kbd>

> 上传时会查找根目录下以`abc`开头的文件作为配置文件

### 烧录固件

要烧录固件，可以使用如下命令并根据提示操作：

> 每个选择列表中第一项为默认值，可使用回车直接选择

```bash
$ ab --flash

An esptool shell

Port List:
  [1] COM3 - Silicon Labs CP210x USB to UART Bridge (COM3)
  [2] COM1 - 通信端口 (COM1)
Choose an option:

Chip List:
  [1] auto
  [2] esp8266
  [3] esp32
  [4] esp32c3
  [5] esp32s2
  [6] esp32s3beta2
  [7] esp32s3beta3
  [8] esp32c6beta
Choose an option:

Address List:
  [1] 0x1000
  [2] 0x0 - for esp32c3
Choose an option:

Firmware List:
  [1] wh_esp32_espnow_v1.17_20210912.bin
Choose an option:
```

### 参数说明

* `-h`：显示使用说明
* ~~`-m`：使用`minify`工具压缩代码（功能未实现）~~
* `-q`：屏蔽操作过程中的相关提示
* `-s`：模拟操作过程，不实际上传文件
* `--repl`：进入`repl`模式
* `--flash`：使用`esptool`烧录固件
* `--readme`：在网页中显示使用说明

### 已知问题

1. ~~调用`ampy`工具新建文件夹的时候如果文件夹已存在，则会抛出异常且无法捕捉~~
2. 偶尔出现无法进入`raw_repl`模式的问题，重新运行一次即可解决
3. 偶尔出现`repl`模式下无法输入的问题，重启开发板即可解决
4. `repl`模式下上传文件也许会出现文件不完整的问题，尝试重新上传可以解决
5. 使用烧录固件功能时如果提示类似找不到`esptool`的信息，卸载后重新安装一次即可

### 更新记录

* `v0.7.5`：一键删除`main.py`文件后执行硬重启，串口列表过滤掉`COM1`
* `v0.7.4`：`repl`模式使用回车键选择第一个端口
* `v0.7.3`：修复`v0.7.2`的 bug，无语。。。。
* `v0.7.2`：修改运行`esptool.py`为`esptool`。。。。
* `v0.7.1`：修改运行`esptool`为`esptool.py`
* `v0.7`：新增`--flash`参数，使用`esptool`烧录固件
* `v0.6.2`：再次尝试修复`v0.6.1`的问题，应该是串口写入等待时间不够，只能增加延时
* `v0.6.1`：修复`repl`模式下上传文件不完整和不能运行文件的问题
* `v0.6`：增加在`repl`模式下直接上传文件的功能
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
```

```bash
# 之前使用的
Ctrl +:
	L - show serial port info
	O - show help
	R - run local pyfile
	T - run onboard pyfile
	U - run code in clipboard
	] - quit
	[ - delete onboard file main.py
```

```bash
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
	U - upload files to board
```

```bash
# 可用的 (闲置的)
Ctrl +:
	F - vsc 冲突
	H - bs 冲突
	K - vsc 冲突
	Q - vsc 冲突
	S - vsc 冲突
	W - cmder 冲突
```

### 合作及交流

* 联系邮箱：<walkline@163.com>
* QQ 交流群：
	* 走线物联：[163271910](https://jq.qq.com/?_wv=1027&k=VlT7Bjs9)
	* 扇贝物联：[31324057](https://jq.qq.com/?_wv=1027&k=IQh2OLw9)

<p align="center"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_walkline.png" width="300px" alt="走线物联"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_bigiot.png" width="300px" alt="扇贝物联"></p>
