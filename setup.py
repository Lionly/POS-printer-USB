# setup.py
# python setup.py py2exe

from distutils.core import setup
import py2exe
import os

# setup(service=["wind"])


setup(console=["cli.py"], zipfile=None, data_files=[("", ['TSCLib.dll', 'JsPrinter.dll'])])
os.rename('dist/cli.exe', 'dist/print.exe')
