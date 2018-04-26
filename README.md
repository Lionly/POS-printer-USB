# POS-printer-USB

两种 USB 接口打印机（ESC/POS，TSC 系列），使用 python 调用厂商提供 SDK 实现定制打印功能。

市面上常见的商用小票打印机，基本都通用，特别是 ESC/POS 系列，所有厂商提供的 SDK 都是一个 JsPrinter.dll。

关于 ESC/POS 的底层原理，可以参考 [这个](https://github.com/mosquito/python-escpos) 项目的实现。代码量不多，很易懂。


## 打包

> python setup.py py2exe

