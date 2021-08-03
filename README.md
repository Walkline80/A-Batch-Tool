<h1 align="center">AMPY Batch Tool</h1>

<p align="center"><img src="https://img.shields.io/badge/Licence-MIT-green.svg?style=for-the-badge" /></p>

### 项目介绍

`AMPY Batch Tool`简称`ab`，借助 [adafruit-ampy](https://learn.adafruit.com/micropython-basics-load-files-and-run-code/install-ampy) 工具，可以批量将项目中指定的文件夹或文件上传到`MicroPython`开发板

### 如何安装

`ab`工具使用`pip`包方式安装

首先克隆或下载项目源文件压缩包并解压缩，然后进入项目文件夹运行命令即可

```bash
$ python setup.py install
```

### 如何使用

* 在你的项目文件夹下新建`abconfig`文件（`ab`工具默认查找该配置文件，也可以手动指定其它文件）

* 添加需要上传的文件夹或文件，每行一个，以`#`号开头的行表示需要排除的文件夹或文件，例如：

	```doc
	drivers/
	services/
	main.py

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
	    drivers/button.py
	    main.py
	    services/mqtt.py

	Dir List (3)
	    drivers
	    drivers/others
	    services

	Making dirs on board...

	Upload files to board...
	Uploading drivers/button.py (1/3)
	Uploading main.py (2/3)
	Uploading services/mqtt.py (3/3)

	Upload finished
	```

### 已知问题

* 调用`ampy`工具新建文件夹的时候如果文件夹已存在，则会抛出异常且无法捕捉

### 更新记录

* `v0.1.1`：尝试上传到[PyPI](https://pypi.org/)
* `v0.1`：完成基本功能

### 参数说明

* `-h`：显示使用说明
* `-m`：使用`minify`工具压缩代码，`默认：不压缩`（功能未实现）
* `-t`：如果压缩代码则需要指定一个临时目录，`默认：temp 目录`
* `-q`：屏蔽操作过程中的相关提示，`默认：显示提示`
* `-s`：模拟操作过程，只显示完整命令内容，不实际上传文件，`默认：上传`

### 合作交流

* 联系邮箱：<walkline@163.com>
* QQ 交流群：
	* 走线物联：163271910
	* 扇贝物联：31324057

<p align="center"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_walkline.png" width="300px" alt="走线物联"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_bigiot.png" width="300px" alt="扇贝物联"></p>
