#!/usr/bin/env python
# -*- coding: utf-8 -*-


from ctypes import *
from ctypes import wintypes
from commands import *


class Escpos:
    """ ESC/POS Printer object """
    handle = None
    device = None

    def __init__(self):
        if self.handle == None:
            self.handle = WinDLL('JsPrinter.dll')
        # 定义函数 - OpenUsb: 打开 USB 打印机的端口
        self.OpenUsb = self.handle.OpenUsb
        self.OpenUsb.restype = wintypes.HANDLE  # 定义返回值类型
        # 定义函数 - WriteUsb: 写入数据 或 命令
        self.WriteUsb = self.handle.WriteUsb
        self.WriteUsb.restype = wintypes.BOOL  # 定义返回值类型
        self.WriteUsb.argtypes = [wintypes.HANDLE, c_char_p, wintypes.DWORD, POINTER(wintypes.DWORD)]  # 定义参数类型
        # 定义函数 - CloseUsb: 关闭 USB 打印机的端口
        self.CloseUsb = self.handle.CloseUsb
        self.CloseUsb.restype = wintypes.BOOL  # 定义返回值类型
        self.CloseUsb.argtypes = [wintypes.HANDLE]  # 定义参数类型
        # 打开 USB
        INVALID_HANDLE_VALUE = c_void_p(-1).value
        self.device = self.OpenUsb()
        if (self.device == INVALID_HANDLE_VALUE):
            # windll.user32.MessageBoxW(0, u'未找到打印机，请等待 Windows 识别设备完成', u'提示', 0)
            raise NoUSBPrinterError()

    def _raw(self, msg):
        """ Print any of the commands above, or clear text """
        if type(msg) == unicode:
            msg = msg.encode('gbk')
        cmd = c_char_p(msg)
        size = wintypes.DWORD(len(msg))
        tmp = byref(wintypes.DWORD())
        self.WriteUsb(self.device, cmd, size, tmp)

    def barcode(self, code, type, width=64, height=4, pos='BLW', font='A'):
        """ Print Barcode """
        # Align Bar Code()
        self._raw(TXT_ALIGN_CT)
        # Height
        if height >= 2 or height <= 6:
            self._raw(BARCODE_HEIGHT)
        else:
            raise BarcodeSizeError()
        # Width
        if width >= 1 or width <= 255:
            self._raw(BARCODE_WIDTH)
        else:
            raise BarcodeSizeError()
        # Font
        if font.upper() == "B":
            self._raw(BARCODE_FONT_B)
        else:  # DEFAULT FONT: A
            self._raw(BARCODE_FONT_A)
        # Position
        if pos.upper() == "OFF":
            self._raw(BARCODE_TXT_OFF)
        elif pos.upper() == "BOTH":
            self._raw(BARCODE_TXT_BTH)
        elif pos.upper() == "ABOVE":
            self._raw(BARCODE_TXT_ABV)
        else:  # DEFAULT POSITION: BELOW
            self._raw(BARCODE_TXT_BLW)
        # Type
        if type.upper() == "UPC-A":
            self._raw(BARCODE_UPC_A)
        elif type.upper() == "UPC-E":
            self._raw(BARCODE_UPC_E)
        elif type.upper() == "EAN13":
            self._raw(BARCODE_EAN13)
        elif type.upper() == "EAN8":
            self._raw(BARCODE_EAN8)
        elif type.upper() == "CODE39":
            self._raw(BARCODE_CODE39)
        elif type.upper() == "ITF":
            self._raw(BARCODE_ITF)
        elif type.upper() == "NW7":
            self._raw(BARCODE_NW7)
        elif type.upper() == "CODE128":
            self._raw(BARCODE_CODE128)
            code = self._code128(code)
        else:
            raise BarcodeTypeError()
        # Print Code
        if code:
            self._raw(code)
        else:
            raise BarcodeCodeError()

    def _code128(self, msg):
        # 长度 2-16
        size = len(msg)
        if (size < 2 or size > 16 or (size % 2) != 0):
            return False
        # 纯数字 双数
        m = ''
        i = 1
        code = BARCODE_CODE128_C
        for d in msg:
            if i == 1:
                m = d
                i = 2
                continue
            if i == 2:
                i = 1
                code = code + chr(int(m + d))
        return chr(len(code)) + code
        pass

    def text(self, txt):
        """ Print alpha-numeric text """
        if txt:
            self._raw(txt)
        else:
            raise TextError()

    def set(self, align='left', font='a', type='normal', width=1, height=1):
        """ Set text properties """
        # Align
        if align.upper() == "CENTER":
            self._raw(TXT_ALIGN_CT)
        elif align.upper() == "RIGHT":
            self._raw(TXT_ALIGN_RT)
        elif align.upper() == "LEFT":
            self._raw(TXT_ALIGN_LT)
        # Font
        if font.upper() == "B":
            self._raw(TXT_FONT_B)
        else:  # DEFAULT FONT: A
            self._raw(TXT_FONT_A)
        # Type
        if type.upper() == "B":
            self._raw(TXT_BOLD_ON)
            self._raw(TXT_UNDERL_OFF)
        elif type.upper() == "U":
            self._raw(TXT_BOLD_OFF)
            self._raw(TXT_UNDERL_ON)
        elif type.upper() == "U2":
            self._raw(TXT_BOLD_OFF)
            self._raw(TXT_UNDERL2_ON)
        elif type.upper() == "BU":
            self._raw(TXT_BOLD_ON)
            self._raw(TXT_UNDERL_ON)
        elif type.upper() == "BU2":
            self._raw(TXT_BOLD_ON)
            self._raw(TXT_UNDERL2_ON)
        elif type.upper == "NORMAL":
            self._raw(TXT_BOLD_OFF)
            self._raw(TXT_UNDERL_OFF)
        # Width
        if width == 2 and height != 2:
            self._raw(TXT_NORMAL)
            self._raw(TXT_2WIDTH)
        elif height == 2 and width != 2:
            self._raw(TXT_NORMAL)
            self._raw(TXT_2HEIGHT)
        elif height == 2 and width == 2:
            self._raw(TXT_2WIDTH)
            self._raw(TXT_2HEIGHT)
        else:  # DEFAULT SIZE: NORMAL
            self._raw(TXT_NORMAL)

    def cut(self, mode=''):
        """ Cut paper """
        # Fix the size between last line and cut
        # TODO: handle this with a line feed
        self._raw("\n\n\n\n\n\n")
        if mode.upper() == "PART":
            self._raw(PAPER_PART_CUT)
        else:  # DEFAULT MODE: FULL CUT
            self._raw(PAPER_FULL_CUT)

    def cashdraw(self, pin):
        """ Send pulse to kick the cash drawer """
        if pin == 2:
            self._raw(CD_KICK_2)
        elif pin == 5:
            self._raw(CD_KICK_5)
        else:
            raise CashDrawerError()

    def hw(self, hw):
        """ Hardware operations """
        if hw.upper() == "INIT":
            self._raw(HW_INIT)
            self._raw(TXT_ZH_CN)
        elif hw.upper() == "SELECT":
            self._raw(HW_SELECT)
        elif hw.upper() == "RESET":
            self._raw(HW_RESET)
        else:  # DEFAULT: DOES NOTHING
            pass

    def control(self, ctl):
        """ Feed control sequences """
        if ctl.upper() == "LF":
            self._raw(CTL_LF)
        elif ctl.upper() == "FF":
            self._raw(CTL_FF)
        elif ctl.upper() == "CR":
            self._raw(CTL_CR)
        elif ctl.upper() == "HT":
            self._raw(CTL_HT)
        elif ctl.upper() == "VT":
            self._raw(CTL_VT)

    def close(self):
        # 关闭
        self.CloseUsb(self.device)
        # windll.user32.MessageBoxW(0, u'开始打印，请等待打印完成', u'提示', 0)


# Errors

class Error(Exception):
    """ Base class for ESC/POS errors """

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


class BarcodeSizeError(Error):
    def __init__(self, msg=""):
        Error.__init__(self, msg)
        self.msg = "Barcode size is out of range"
        self.resultcode = 20

    def __str__(self):
        return "Barcode size is out of range"


class BarcodeCodeError(Error):
    def __init__(self, msg=""):
        Error.__init__(self, msg)
        self.msg = "Code was not supplied"
        self.resultcode = 30

    def __str__(self):
        return "Code was not supplied"


class ImageSizeError(Error):
    def __init__(self, msg=""):
        Error.__init__(self, msg)
        self.msg = msg
        self.resultcode = 40

    def __str__(self):
        return "Image height is longer than 255px and can't be printed"


class TextError(Error):
    def __init__(self, msg=""):
        Error.__init__(self, msg)
        self.msg = "Text string must be supplied to the text() method"
        self.resultcode = 50

    def __str__(self):
        return "Text string must be supplied to the text() method"


class CashDrawerError(Error):
    def __init__(self, msg=""):
        Error.__init__(self, msg)
        self.msg = msg
        self.resultcode = 60

    def __str__(self):
        return "Valid pin must be set to send pulse"
