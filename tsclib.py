#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from ctypes import *


class TSCLib:
    """ TSC Printer object """
    handle = None

    def __init__(self, width=60, height=40, paper='label'):
        """ 纸张类型 paper = label or thermal """
        if self.handle is None:
            self.handle = WinDLL('TSCLib.dll')
        # 定义函数 - openport: 打开 打印机的端口
        # public static extern int openport(string printername);
        self.Open = self.handle.openport
        self.Open.restype = c_int  # 定义返回值类型
        self.Open.argtypes = [c_char_p]  # 定义参数类型
        # 定义函数 - setup: 设置 打印机
        # public static extern int setup(string width, string height,
        #          string speed, string density,
        #          string sensor, string vertical,
        #          string offset);
        self.set = self.handle.setup
        self.set.restype = c_int  # 定义返回值类型
        self.set.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]  # 定义参数类型
        # 定义函数 - clearbuffer: 清除
        # public static extern int clearbuffer();
        self.clear = self.handle.clearbuffer
        self.clear.restype = c_int  # 定义返回值类型
        # 定义函数 - barcode: 使用條碼機內建條碼列印
        # public static extern int barcode(string x, string y, string type,
        #          string height, string readable, string rotation,
        #          string narrow, string wide, string code);
        self._barcode = self.handle.barcode
        self._barcode.restype = c_int  # 定义返回值类型
        self._barcode.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p,
                                  c_char_p]  # 定义参数类型
        # 定义函数 - windowsfont: 使用 Windows TTF 字型列印文字
        # public static extern int windowsfont(int x, int y, int fontheight,
        #          int rotation, int fontstyle, int fontunderline,
        #          string szFaceName, string content);
        self._font = self.handle.windowsfont
        self._font.restype = c_int  # 定义返回值类型
        self._font.argtypes = [c_int, c_int, c_int, c_int, c_int, c_int, c_char_p, c_char_p]  # 定义参数类型
        # 定义函数 - printlabel: 列印標籤內容
        # public static extern int printlabel(string set, string copy);
        self.label = self.handle.printlabel
        self.label.restype = c_int  # 定义返回值类型
        self.label.argtypes = [c_char_p, c_char_p]  # 定义参数类型
        # 定义函数 - closeport: 關閉指定的電腦端輸出埠
        # public static extern int closeport();
        self._close = self.handle.closeport
        self._close.restype = c_int  # 定义返回值类型
        # 初始化 打开 USB
        self.device = self.Open('USB')
        # 设置打印机
        width = str(width)
        height = str(height)
        if paper == 'label':
            # 参数    宽度   高度    速度   浓度  sensor 垂直间距 偏移
            self.set(width, height, "1.0", "8", "0",   "2",    "0")
        elif paper == 'thermal':
            # 参数    宽度   高度    速度   浓度  sensor 垂直间距 偏移
            self.set(width, height, "2.0", "8", "1",   "0",    "0")
        else:
            raise Error('error paper type')
        self.clear()
        if self.device == 0:
            raise NoUSBPrinterError()

    def barcode(self, code, x=120, y=50, height=120):
        """ Print barcode """
        if type(code) == unicode:
            msg = code.encode('gbk')
            code = c_char_p(msg)
        x = c_char_p(str(x))
        y = c_char_p(str(y))
        height = c_char_p(str(height))
        self._barcode(x, y, "128", height, "0", "0", "2", "2", code)

    def text(self, txt, x=100, y=100, height=40, rotation=0, style=0, underline=0):
        """ Print alpha-numeric text """
        if type(txt) == unicode:
            msg = txt.encode('gbk')
            txt = c_char_p(msg)
        self._font(x, y, height, rotation, style, underline, "Microsoft Yahei", txt)

    def close(self):
        # 关闭
        self.label("1", "1")
        self._close()


# Errors
class Error(Exception):
    """ Base class for errors """
    def __init__(self, msg, status=None):
        Exception.__init__(self)
        self.msg = msg
        self.resultcode = 1
        if status is not None:
            self.resultcode = status

    def __str__(self):
        return self.msg


# Result/Exit codes
# 0  = success
# 10 = No Barcode type defined
# 20 = Barcode size values are out of range
# 30 = Barcode text not supplied
# 40 = Image height is too large
# 50 = No string supplied to be printed
# 60 = Invalid pin to send Cash Drawer pulse
# 70 = 未找到 USB 打印机 可能 未开启、未插电、计算机未识别、、、


class NoUSBPrinterError(Error):
    def __init__(self, msg=""):
        Error.__init__(self, msg)
        # self.msg = u"未找到 USB 打印机 可能 未开启、未插电、计算机未识别"
        self.msg = "Not Found USB Printer"
        self.resultcode = 70

    def __str__(self):
        # return u"未找到 USB 打印机 可能 未开启、未插电、计算机未识别"
        return "Not Found USB Printer"


class BarcodeTypeError(Error):
    def __init__(self, msg=""):
        Error.__init__(self, msg)
        self.msg = "No Barcode type is defined"
        self.resultcode = 10

    def __str__(self):
        return "No Barcode type is defined"
