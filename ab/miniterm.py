#!/usr/bin/env python
#
# Very simple serial terminal
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C)2002-2020 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# Modified by Walkline Wang (https://walkline.wang)
# Gitee: https://gitee.com/walkline/a-batch-tool

from __future__ import absolute_import

import codecs
import os
import sys
import threading
import time
import win32clipboard as clip


import serial
from serial.tools import hexlify_codec

# pylint: disable=wrong-import-order,wrong-import-position

codecs.register(lambda c: hexlify_codec.getregentry() if c == 'hexlify' else None)
ANSI_COLOR_YELLOW = b'\x1b[33m'
ANSI_COLOR_RED = b'\x1b[31m'
ANSI_COLOR_GREEN = b'\x1b[32m'
ANSI_COLOR_RESET = b'\x1b[0m'
ANSI_UNDERLINE = b'\033[4m'
ANSI_CLOSE = b'\033[0m'
ABCONFIG_FILE_PREFIX = 'abc'

help = \
b'''
\033[1;37mMiniterm for MicroPython REPL\033[0m
    \033[3;32mCtrl-Z - Quit
    Ctrl-N - Help
    Ctrl-X - Kill main.py
    Ctrl-Y - Serial Info
    Ctrl-L - Run last file
    Ctrl-R - Run local file
    Ctrl-T - Run board file
    Ctrl-G - Run clipboard code
    Ctrl-U - Upload files to board\033[0m
'''

command_list_onboard_files = \
b'''
import os,sys
file_list=[]
def list_files(root='/'):
  files=[]
  for dir in os.listdir(root):
    fullpath = ('' if root=='/' else root)+'/'+dir
    if os.stat(fullpath)[0] & 0x4000 != 0:
      files.extend(list_files(fullpath))
    else:
      if dir.endswith('.py'):
        files.append(fullpath)
  return files
file_list = list_files()
if len(file_list)>0:
  print('\033[1;36mRun onboard file\033[0m')
  for index,file in enumerate(file_list,start=1):
    print('    [{}] {}'.format(index, file))
  selected=None
  while True:
    try:
      selected=int(input('Choose a file: '))
      print('')
      assert type(selected) is int and 0 < selected <= len(file_list)
      break
    except KeyboardInterrupt:
      print('')
      break
    except:
      pass
  #print(file_list[selected-1])
  if selected:
    exec(open(file_list[selected-1]).read(), globals())
else:
  print('\033[1;33mNo py file on board\033[0m')
'''

try:
    raw_input
except NameError:
    # pylint: disable=redefined-builtin,invalid-name
    raw_input = input   # in python3 it's "raw"
    unichr = chr


def key_description(character):
    """generate a readable description for a key"""
    ascii_code = ord(character)
    if ascii_code < 32:
        return 'Ctrl+{:c}'.format(ord('@') + ascii_code)
    else:
        return repr(character)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class ConsoleBase(object):
    """OS abstraction for console (input/output codec, no echo)"""

    def __init__(self):
        if sys.version_info >= (3, 0):
            self.byte_output = sys.stdout.buffer
        else:
            self.byte_output = sys.stdout
        self.output = sys.stdout

    def setup(self):
        """Set console to read single characters, no echo"""

    def cleanup(self):
        """Restore default console settings"""

    def getkey(self):
        """Read a single key from the console"""
        return None

    def write_bytes(self, byte_string):
        """Write bytes (already encoded)"""
        self.byte_output.write(byte_string)
        self.byte_output.flush()

    def write(self, text):
        """Write string"""
        self.output.write(text)
        self.output.flush()

    def cancel(self):
        """Cancel getkey operation"""

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # context manager:
    # switch terminal temporary to normal mode (e.g. to get user input)

    def __enter__(self):
        self.cleanup()
        return self

    def __exit__(self, *args, **kwargs):
        self.setup()


if os.name == 'nt':  # noqa
    import msvcrt
    import ctypes
    import platform

    class Out(object):
        """file-like wrapper that uses os.write"""

        def __init__(self, fd):
            self.fd = fd

        def flush(self):
            pass

        def write(self, s):
            os.write(self.fd, s)

    class Console(ConsoleBase):
        navcodes = {
            'H': '\x1b[A',  # UP
            'P': '\x1b[B',  # DOWN
            'K': '\x1b[D',  # LEFT
            'M': '\x1b[C',  # RIGHT
            'G': '\x1b[H',  # HOME
            'O': '\x1b[F',  # END
            'R': '\x1b[2~',  # INSERT
            'S': '\x1b[3~',  # DELETE
            'I': '\x1b[5~',  # PGUP
            'Q': '\x1b[6~',  # PGDN        
        }
        
        def __init__(self):
            super(Console, self).__init__()
            self._saved_ocp = ctypes.windll.kernel32.GetConsoleOutputCP()
            self._saved_icp = ctypes.windll.kernel32.GetConsoleCP()
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            ctypes.windll.kernel32.SetConsoleCP(65001)
            # ANSI handling available through SetConsoleMode since Windows 10 v1511 
            # https://en.wikipedia.org/wiki/ANSI_escape_code#cite_note-win10th2-1
            if platform.release() == '10' and int(platform.version().split('.')[2]) > 10586:
                ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                import ctypes.wintypes as wintypes
                if not hasattr(wintypes, 'LPDWORD'): # PY2
                    wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)
                SetConsoleMode = ctypes.windll.kernel32.SetConsoleMode
                GetConsoleMode = ctypes.windll.kernel32.GetConsoleMode
                GetStdHandle = ctypes.windll.kernel32.GetStdHandle
                mode = wintypes.DWORD()
                GetConsoleMode(GetStdHandle(-11), ctypes.byref(mode))
                if (mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING) == 0:
                    SetConsoleMode(GetStdHandle(-11), mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
                    self._saved_cm = mode
            self.output = codecs.getwriter('UTF-8')(Out(sys.stdout.fileno()), 'replace')
            # the change of the code page is not propagated to Python, manually fix it
            sys.stderr = codecs.getwriter('UTF-8')(Out(sys.stderr.fileno()), 'replace')
            sys.stdout = self.output
            self.output.encoding = 'UTF-8'  # needed for input

        def __del__(self):
            ctypes.windll.kernel32.SetConsoleOutputCP(self._saved_ocp)
            ctypes.windll.kernel32.SetConsoleCP(self._saved_icp)
            try:
                ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), self._saved_cm)
            except AttributeError: # in case no _saved_cm
                pass

        def sendkey(self, key):
            msvcrt.putch(key)

        def getkey(self):
            while True:
                z = msvcrt.getwch()
                if z == unichr(13):
                    return unichr(10)
                elif z is unichr(0) or z is unichr(0xe0):
                    try:
                        code = msvcrt.getwch()
                        return self.navcodes[code]
                    except KeyError:
                        pass
                else:
                    return z

        def cancel(self):
            # CancelIo, CancelSynchronousIo do not seem to work when using
            # getwch, so instead, send a key to the window with the console
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            ctypes.windll.user32.PostMessageA(hwnd, 0x100, 0x0d, 0)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Transform(object):
    """do-nothing: forward all data unchanged"""
    def rx(self, text):
        """text received from serial port"""
        return text

    def tx(self, text):
        """text to be sent to serial port"""
        return text

    def echo(self, text):
        """text to be sent but displayed on console"""
        return text


class CRLF(Transform):
    """ENTER sends CR+LF"""

    def tx(self, text):
        return text.replace('\n', '\r\n')

class NoTerminal(Transform):
    """remove typical terminal control codes from input"""
    def rx(self, text):
        return text

    echo = rx

EOL_TRANSFORMATIONS = {
    'crlf': CRLF
}

TRANSFORMATIONS = {
    'direct': Transform,    # no transformation
    'default': NoTerminal
}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Miniterm(object):
    """\
    Terminal application. Copy data from serial port to console and vice versa.
    Handle special keys from the console to show menu etc.
    """

    def __init__(self, serial_instance, echo=False, eol='crlf', filters=['default']):
        self.console = Console()
        self.serial = serial_instance
        self.echo = echo
        self.raw = False
        self.input_encoding = 'UTF-8'
        self.output_encoding = 'UTF-8'
        self.eol = eol
        self.filters = filters
        self.update_transformations()
        self.exit_character = unichr(0x1a)  # GS/CTRL+]
        #self.menu_character = unichr(0x14)  # Menu: CTRL+T
        self.alive = None
        self._reader_alive = None
        self._pause_reader = False
        self.receiver_thread = None
        self.rx_decoder = None
        self.tx_decoder = None
        self.last_run = None

    def _start_reader(self):
        """Start reader thread"""
        self._reader_alive = True
        # start serial->console thread
        self.receiver_thread = threading.Thread(target=self.reader, name='rx')
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def _stop_reader(self):
        """Stop reader thread only, wait for clean exit of thread"""
        self._reader_alive = False
        if hasattr(self.serial, 'cancel_read'):
            self.serial.cancel_read()
        self.receiver_thread.join()

    def start(self):
        """start worker threads"""
        self.alive = True
        self._start_reader()
        # enter console->serial loop
        self.transmitter_thread = threading.Thread(target=self.writer, name='tx')
        self.transmitter_thread.daemon = True
        self.transmitter_thread.start()
        self.console.setup()

    def stop(self):
        """set flag to stop worker threads"""
        self.alive = False

    def join(self, transmit_only=False):
        """wait for worker threads to terminate"""
        self.transmitter_thread.join()
        if not transmit_only:
            if hasattr(self.serial, 'cancel_read'):
                self.serial.cancel_read()
            self.receiver_thread.join()

    def close(self):
        self.serial.close()

    def update_transformations(self):
        """take list of transformation classes and instantiate them for rx and tx"""
        transformations = [EOL_TRANSFORMATIONS[self.eol]] + [TRANSFORMATIONS[f]
                                                             for f in self.filters]
        self.tx_transformations = [t() for t in transformations]
        self.rx_transformations = list(reversed(self.tx_transformations))

    def set_rx_encoding(self, encoding, errors='replace'):
        """set encoding for received data"""
        self.input_encoding = encoding
        self.rx_decoder = codecs.getincrementaldecoder(encoding)(errors)

    def set_tx_encoding(self, encoding, errors='replace'):
        """set encoding for transmitted data"""
        self.output_encoding = encoding
        self.tx_encoder = codecs.getincrementalencoder(encoding)(errors)

    def dump_port_settings(self):
        """Write current settings to sys.stderr"""
        sys.stderr.write("\n--- Settings: {p.name}  {p.baudrate},{p.bytesize},{p.parity},{p.stopbits}\n".format(
            p=self.serial))
        sys.stderr.write('--- RTS: {:8}  DTR: {:8}  BREAK: {:8}\n'.format(
            ('active' if self.serial.rts else 'inactive'),
            ('active' if self.serial.dtr else 'inactive'),
            ('active' if self.serial.break_condition else 'inactive')))
        try:
            sys.stderr.write('--- CTS: {:8}  DSR: {:8}  RI: {:8}  CD: {:8}\n'.format(
                ('active' if self.serial.cts else 'inactive'),
                ('active' if self.serial.dsr else 'inactive'),
                ('active' if self.serial.ri else 'inactive'),
                ('active' if self.serial.cd else 'inactive')))
        except serial.SerialException:
            # on RFC 2217 ports, it can happen if no modem state notification was
            # yet received. ignore this error.
            pass
        sys.stderr.write('--- software flow control: {}\n'.format('active' if self.serial.xonxoff else 'inactive'))
        sys.stderr.write('--- hardware flow control: {}\n'.format('active' if self.serial.rtscts else 'inactive'))
        sys.stderr.write('--- serial input encoding: {}\n'.format(self.input_encoding))
        sys.stderr.write('--- serial output encoding: {}\n'.format(self.output_encoding))
        sys.stderr.write('--- EOL: {}\n'.format(self.eol.upper()))
        sys.stderr.write('--- filters: {}'.format(' '.join(self.filters)))

    def reader(self):
        """loop and copy serial->console"""
        try:
            while self.alive and self._reader_alive:
                # read all that is there or wait for one byte
                data = self.serial.read(self.serial.in_waiting or 1)
                if data:
                    if self._pause_reader:
                        continue
                    if self.raw:
                        self.console.write_bytes(data)
                    else:
                        text = self.rx_decoder.decode(data)
                        for transformation in self.rx_transformations:
                            text = transformation.rx(text)
                        self.console.write(text)
        except serial.SerialException:
            self.alive = False
            self.console.cancel()
            raise       # XXX handle instead of re-raise?

    def send_tx_enter(self):
        '''(新增函数)
        发送一个模拟键盘输入的回车，用途是在换行时显示 repl 提示符前缀，也就是 >>>
        '''
        text = unichr(10)
        for transformation in self.tx_transformations:
            text = transformation.tx(text)
        self.serial.write(self.tx_encoder.encode(text))

    def list_files(self, root='.', levels=2, for_py=True):
        '''
        递归获取指定目录及默认 2 层子目录下的 py 文件
        '''
        files = []
        if levels == 0:
            return files

        for dir in os.listdir(root):
            fullpath = os.path.join(root, dir)
            if os.path.isdir(fullpath):
                files.extend(self.list_files(fullpath, levels - 1))
            else:
                if for_py:
                    if fullpath.endswith('.py'):
                        files.append(fullpath.replace('.\\', ''))
                else:
                    if fullpath.split('\\')[-1].startswith(ABCONFIG_FILE_PREFIX):
                        files.append(fullpath.replace('.\\', ''))

        return files

    def get_local_pyfile(self) -> str or None:
        '''(新增函数)
        获取用户选择的本地 py 文件，文件以列表形式供用户选择，列表文件选取范围是当前目录及 2 层子目录下的 py 文件
        '''
        file_list = list(reversed(self.list_files()))

        if len(file_list) > 0:
            self.show_title('Run local file')
            for index, file in enumerate(file_list, start=1):
                print(f'    [{index}] {file}')

            selected = None
            while True:
                try:
                    selected = int(input('Choose a file: '))
                    assert type(selected) is int and 0 < selected <= len(file_list)
                    break
                except EOFError:
                    self.run_board_file(b'\n')
                    return
                except:
                    pass

            return file_list[selected - 1]
        else:
            self.show_tips('No local py file found')

    def run_local_file(self, pyfile=None):
        '''(新增函数)
        运行指定的本地 py 文件。
        运行方式为 repl paste 模式（ctrl-e 进入， ctrl-d 完成）
        '''
        pyfile = self.get_local_pyfile() if pyfile is None else pyfile

        if pyfile:
            with open(pyfile, 'rb') as file:
                pyfile_data = file.read()

            self._pause_reader = True
            time.sleep(0.02)
            self.serial.write(b"\x05")
            time.sleep(0.02)

            start_time = time.time()
            for i in range(0, len(pyfile_data), 256):
                self.serial.write(pyfile_data[i : min(i + 256, len(pyfile_data))])
                time.sleep(0.01)

            time.sleep(round(time.time() - start_time, 3))
            self.serial.write(b"\x04")
            time.sleep(0.02)
            self._pause_reader = False
            time.sleep(0.02)
            self.console.write_bytes(b'\r\n')
            time.sleep(0.02)

            self.last_run = ('local', pyfile)

    def run_clipboard_code(self):
        '''(新增函数)
        运行剪贴板中复制的代码。
        运行方式为 repl paste 模式（ctrl-e 进入， ctrl-d 完成）
        '''
        self.show_title('Run clipboard code')
        self._pause_reader = True
        time.sleep(0.02)
        self.serial.write(b'\x05')
        clip.OpenClipboard()
        for line in clip.GetClipboardData().split('\r\n'):
            if line.strip('\t').startswith('#'):
                continue
            self.serial.write(line.replace('\t', '    ').encode() + b'\r')
            self.serial.flush()
            time.sleep(0.002)
        clip.CloseClipboard()
        self.serial.write(b'\x04')
        time.sleep(0.02)
        self._pause_reader = False
        time.sleep(0.02)
        self.console.write_bytes(b'\r\n')
        time.sleep(0.02)

    def run_board_file(self, onboard_code=command_list_onboard_files):
        '''(新增函数)
        运行指定的远程（开发板） py 文件，开发板上的目录结构相对简单所以会列出所有目录下的 py 文件。
        运行方式为 repl paste 模式（ctrl-e 进入， ctrl-d 完成）
        '''
        self._pause_reader = True
        self.serial.write(b'\x05')
        start_time = time.time()
        for i in range(0, len(onboard_code), 256):
            self.serial.write(onboard_code[i : min(i + 256, len(onboard_code))])
            time.sleep(0.02)

        time.sleep(round(time.time() - start_time, 3))

        self.serial.write(b"\x04")
        self._pause_reader = False

    def run_code_on_board(self, onboard_code):
        self.serial.write(b'\x05')
        time.sleep(0.02)
        lock = threading.Lock()
        with lock:
            for i in range(0, len(onboard_code), 256):
                self.serial.write(onboard_code[i : min(i + 256, len(onboard_code))])
                time.sleep(0.03)
        self.serial.write(b"\x04")
        time.sleep(0.02)

    def put_file(self, src, dest):
        self.run_code_on_board(bytes("f=open('%s','wb')\nw=f.write" % dest, 'utf-8'))

        with open(src, "rb") as f:
            while True:
                data = f.read(256)
                if not data:
                    break
                self.run_code_on_board(bytes("w(" + repr(data) + ")", 'utf-8'))
        self.run_code_on_board(b"f.close()")

    def show_title(self, title):
        '''(新增函数)
        打印蓝色的 title 字符串
        '''
        self.console.write('\033[1;36m{}\033[0m\n'.format(title))

    def show_tips(self, tips):
        '''(新增函数)
        打印黄色的 tips 字符串，并发送 repl 换行
        '''
        self.console.write('\033[1;33m{}\033[0m'.format(tips))
        self.send_tx_enter()

    def writer(self):
        """\
        Loop and copy console->serial until self.exit_character character is
        found. When self.menu_character is found, interpret the next key
        locally.
        """
        try:
            while self.alive:
                try:
                    c = self.console.getkey()
                except KeyboardInterrupt:
                    c = '\x03'
                if not self.alive:
                    break
                elif c == self.exit_character:
                    self.stop()             # exit app
                    os._exit(0)
                    break
                elif c == unichr(0x19):     # CTRL + Y
                    self.dump_port_settings()
                    self.send_tx_enter()
                elif c == unichr(0x0e):     # CTRL + N
                    self.console.write_bytes(help)
                    self.send_tx_enter()
                elif c == unichr(0x07):     # CTRL + G
                    self.run_clipboard_code()
                elif c == unichr(0x18):     # CTRL + X
                    # 一键删除开发板 main.py 文件
                    self._pause_reader = True
                    self.serial.write(b"\x05")
                    self.serial.write(b'import os\rtry:\r  os.remove("main.py")\rexcept:\r  pass\r')
                    self.serial.write(b'\x04')
                    time.sleep(0.2)
                    self._pause_reader = False
                    self.serial.write(b'\x04')
                elif c == unichr(0x12):     # CTRL + R
                    self.run_local_file()
                elif c == unichr(0x14):     # CTRL + T
                    self.run_board_file()
                elif c == unichr(0x15):      # CTRL + U
                    # upload files to board
                    self.show_title('Upload files')

                    abconfig_list = list(reversed(self.list_files(levels=1, for_py=False)))

                    if len(abconfig_list) == 1:
                        abconfig = abconfig_list[0]
                    elif len(abconfig_list) > 0:
                        for index, file in enumerate(abconfig_list, start=1):
                            print(f'    [{index}] {file}')

                        selected = None
                        while True:
                            try:
                                selected = int(input('Choose a config file: '))
                                assert type(selected) is int and 0 < selected <= len(abconfig_list)
                                break
                            except EOFError:
                                break
                            except:
                                pass

                        if not selected:
                            self.run_board_file(b'\n')
                            continue
                        abconfig = abconfig_list[selected - 1]
                    else:
                        self.show_tips('No ab config file found')
                        continue

                    from .__main__ import parse_config_file, list_all_files_and_dirs, CMD_MKDIRS

                    includes, excludes, run_file = parse_config_file(abconfig)
                    include_files, include_dirs, _ = list_all_files_and_dirs(includes, excludes)

                    if not include_files:
                        self.show_tips('Nothing to do!')
                        continue

                    cmd = CMD_MKDIRS.format(include_dirs, True)
                    self.run_board_file(bytes(cmd, 'utf-8'))
                    time.sleep(0.2)

                    self._pause_reader = True
                    time.sleep(0.2)
                    for index, file in enumerate(include_files, start=1):
                        print(f'- uploading {file} ({index}/{len(include_files)})')

                        src = os.path.join(file)
                        dest = file
                        self.put_file(src, dest)

                    self._pause_reader = False
                    time.sleep(0.2)

                    print('Upload Finished')
                    self.serial.write(b'\x04')
                    time.sleep(0.2)

                    if run_file in include_files:
                        self.show_title('Run onboard file: {}'.format(run_file))
                        self.run_board_file(open(run_file, 'rb').read())

                        self.last_run = ('board', run_file)
                elif c == unichr(0x0c):     # CTRL + L
                    if self.last_run:
                        site, pyfile = self.last_run
                        
                        if site == 'local':
                            self.show_title(f'Run local file: {pyfile}')
                            self.run_local_file(pyfile)
                        elif site == 'board':
                            self.show_title(f'Run onboard file: {pyfile}')
                            self.run_board_file(open(pyfile, 'rb').read())
                        elif site == 'clipboard':
                            self.run_clipboard_code()
                        else:
                            self.show_tips('Unknown last code identity')
                    else:
                        self.show_tips('Not run code yet')
                else:
                    #~ if self.raw:
                    text = c
                    for transformation in self.tx_transformations:
                        text = transformation.tx(text)
                    self.serial.write(self.tx_encoder.encode(text))
                # print(hex(ord(c)))
        except:
            self.alive = False
            raise

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# default args can be used to override when calling main() from an other script
# e.g to create a miniterm-my-device.py
def main(default_port=None, default_baudrate=115200, default_rts=False, default_dtr=False):
    """Command line tool, entry point"""
    while True:
        try:
            serial_instance = serial.serial_for_url(
                default_port,
                default_baudrate,
                parity='N',
                rtscts=False,
                xonxoff=False,
                do_not_open=True)

            if not hasattr(serial_instance, 'cancel_read'):
                # enable timeout for alive flag polling if cancel_read is not available
                serial_instance.timeout = 1

            serial_instance.dtr = default_dtr
            serial_instance.rts = default_rts

            if isinstance(serial_instance, serial.Serial):
                serial_instance.exclusive = True

            serial_instance.open()
        except serial.SerialException as e:
            sys.stderr.write('{}\n'.format(e))
            sys.exit(1)
        else:
            break

    miniterm = Miniterm(serial_instance)
    miniterm.raw = False
    miniterm.set_rx_encoding('UTF-8')
    miniterm.set_tx_encoding('UTF-8')
    miniterm.start()
    miniterm.console.write_bytes(help)
    miniterm.send_tx_enter()

    try:
        miniterm.join(True)
    except KeyboardInterrupt:
        pass
    miniterm.join()
    miniterm.close()

if __name__ == '__main__':
    main()
