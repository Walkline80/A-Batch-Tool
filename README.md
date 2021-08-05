<h1 align="center">AMPY Batch Tool</h1>

<p align="center"><img src="https://img.shields.io/badge/Licence-MIT-green.svg?style=for-the-badge" /></p>

### 项目介绍

[AMPY Batch Tool](https://pypi.org/project/ampy-batch-tool/) 简称`ab`，可以批量将项目中指定的文件夹或文件上传到`MicroPython`开发板

### 如何安装

#### 在线安装（推荐）

```bash
$ pip install ampy-batch-tool
```

#### 离线安装

首先克隆或下载项目源文件压缩包并解压缩，然后进入项目文件夹运行命令

```bash
$ python setup.py install
```

### 如何使用

* 在你的项目文件夹下新建`abconfig`文件（`ab`工具默认查找该配置文件，也可以手动指定其它文件）

* 配置文件中填写需要上传的文件夹或文件，每行一个，以`#`号开头的行表示需要排除的文件夹或文件，例如：

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
	    services/mqtt.py
	    main.py

	Dir List (3)
	    drivers/
	    drivers/others/
	    services/

	Making dirs on board...
	    drivers/ exist
	    drivers/others/ exist
	    services/ exist

	Upload files to board...
	    uploading drivers/button.py (1/3)
	    uploading services/mqtt.py (2/3)
	    uploading main.py (3/3)

	Upload Finished
	```

### 已知问题

1. ~~调用`ampy`工具新建文件夹的时候如果文件夹已存在，则会抛出异常且无法捕捉~~

### 更新记录

* `v0.2.2`：修复某些开发板不能读取串口数据的问题（如`安信可 ESP32C3 系列开发板`）
* `v0.2.1`：修复导入模块路径问题
* `v0.2`：
	* 使用 [pyboard.py](https://github.com/micropython/micropython/blob/master/tools/pyboard.py) 替代`ampy`以提升文件上传效率，并解决`已知问题 1`
	* 禁用了代码压缩功能，使用 [pyminifier](http://liftoff.github.io/pyminifier/index.html) 压缩代码会出现问题
	* 删除指定临时目录参数

* `v0.1.1`：尝试上传到 [PyPI](https://pypi.org/)
* `v0.1`：完成基本功能

### 参数说明

* `-h`：显示使用说明
* ~~`-m`：使用`minify`工具压缩代码（功能未实现）~~
* `-q`：屏蔽操作过程中的相关提示
* `-s`：模拟操作过程，不实际上传文件

### 合作交流

* 联系邮箱：<walkline@163.com>
* QQ 交流群：
	* 走线物联：163271910
	* 扇贝物联：31324057

<p align="center"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_walkline.png" width="300px" alt="走线物联"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_bigiot.png" width="300px" alt="扇贝物联"></p>
