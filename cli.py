#!/usr/bin/env python
# -*- coding: utf-8 -*-
# cli.py


import threading
import argparse
import click
import json
import sys

from escpos import *
from tsclib import *


def book(p, books):
    for b in books:
        b = dict(b)
        p.text(u'\n绘本：' + b.get("name", u'无'))
        p.text(u'\n编号：' + b.get("code", u'无'))


# 打印配送单
def ps(data_list):
    try:
        p = Escpos()
        p.hw('init')
        for item in data_list:
            item = dict(item)
            title = item.get("title", u'配送单')
            code128 = item.get("code128", None)
            address = item.get("address", u'暂无')
            mobile = item.get("mobile", u'暂无')
            time = item.get("time", u'暂无')
            note = item.get("note", u'暂无')
            send = item.get("send", [])  # ["name"] ["code"]
            take = item.get("take", [])
            sign = item.get("sign", u'祝您阅读愉快！')
            # 开始排版
            p.set('center', 'a', 'b', 2, 2)
            p.text(u'※※' + title + u'※※\n\n')
            if code128:
                p.barcode(code128, 'code128')
            p.set('left')  # 左对齐
            p.text(u'\n配送地址：' + address)
            p.text(u'\n联系电话：' + mobile)
            p.text(u'\n配送时间：' + time)
            p.text(u'\n是否塑封：' + note)
            p.text('\n')
            if len(send) > 0:
                p.set('center')
                p.text(u'\n* * * * * * 借 书 * * * ' + str(len(send)) + u'本')
            p.set('left')
            book(p, send)
            p.text('\n')
            if len(take) > 0:
                p.set('center')
                p.text(u'\n* * * * * * 还 书 * * * ' + str(len(take)) + u'本')
            p.set('left')
            book(p, take)
            p.text('\n')
            p.set('center')  # 居中
            p.text(u'\n' + sign)
            p.text(u'\n\n--------剪--切--线--------\n\n\n')
        p.close()
    except Exception, e:
        raise e


# 打印出库单
def hub(book_list):
    try:
        p = Escpos()
        p.hw('init')
        for item in book_list:
            item = dict(item)
            title = item.get("title", u'出库单')
            hubs = item.get("hub", u'')
            club = item.get("club", u'')
            send = item.get("send", [])  # ["name"] ["code"]
            sign = item.get("sign", u'')
            # 开始排版
            p.set('center', 'a', 'b', 2, 2)
            p.text(u'※※' + title + u'※※\n\n')
            p.set('left')  # 左对齐
            p.text(u'\n来自：' + hubs)
            p.text(u'\n送往：' + club)
            book(p, send)
            p.text(u'\n\n' + sign)
            # 居中
            p.set('center')
            p.text(u'\n\n--------剪--切--线--------\n\n\n')
        p.close()
    except Exception, e:
        raise e


# 打印绘本标签
def lab(book_info):
    try:
        p = TSCLib()
        item = dict(book_info)
        code = item.get("code", '00000000')
        code_show = item.get("code_show", 'Error')
        club = item.get("club", u'亦启读绘本')
        # 开始排版
        p.barcode(code)
        p.text(code_show, x=100, y=180)
        p.text(club, x=100, y=230)
        p.close()
    except Exception, e:
        raise e


def print_tsc(p, print_arr, line_spacing):
    y = 0
    for item in print_arr:
        item = dict(item)
        t = item.get("t", 'line')
        v = item.get("v", '')
        h = item.get("h", 10)
        x = item.get("x", 50)
        # 开始排版
        y += h
        size = h - line_spacing
        if t == 'text':
            p.text(v, x=x, y=y, height=size)
        elif t == 'code':
            tmp_y = y - (size / 2)
            p.barcode(v, x=x, y=tmp_y, height=size)
        else:
            pass


def get_len(source):
    str_len = len(source)
    for ch in source:
        if u'\u4e00' <= ch <= u'\u9fff':
            str_len += 1
    return str_len


def split_str_by_len(source, line):
    tmp, str_len = '', 0
    str_arr = []
    for ch in source:
        tmp += ch
        if u'\u4e00' <= ch <= u'\u9fff':
            str_len += 2
        else:
            str_len += 1
        # 分割
        if str_len >= line:
            str_arr.append(tmp)
            tmp, str_len = '', 0
    str_arr.append(tmp)
    return str_arr


# 打印配送单 by tsc
def ps_tsc(data_list):
    max_len = 40  # 可打印文本最大长度 汉字 2 英文 1
    line_spacing = 8  # 行间距
    setup_height = 0  # init
    print_arr = []
    for item in data_list:
        item = dict(item)
        # 加个空行
        print_arr.append({'t': 'line', 'h': 32, 'v': ''})
        title = item.get("title", u'配送单')
        print_arr.append({'t': 'text', 'h': 48, 'v': u'※※' + title + u'※※'})
        code128 = item.get("code128", None)
        if code128 is not None:
            print_arr.append({'t': 'code', 'h': 96, 'v': code128})
        # 加个空行
        print_arr.append({'t': 'line', 'h': 32, 'v': ''})
        address = u'配送地址：' + item.get("address", u'暂无')
        if get_len(address) > max_len:
            tmp_arr = split_str_by_len(address, max_len)
            for li in tmp_arr:
                print_arr.append({'t': 'text', 'h': 40, 'v': li})
        else:
            print_arr.append({'t': 'text', 'h': 40, 'v': address})
        mobile = u'联系电话：' + item.get("mobile", u'暂无')
        print_arr.append({'t': 'text', 'h': 40, 'v': mobile})
        time = u'配送时间：' + item.get("time", u'暂无')
        print_arr.append({'t': 'text', 'h': 40, 'v': time})
        note = u'是否塑封：' + item.get("note", u'暂无')
        print_arr.append({'t': 'text', 'h': 40, 'v': note})
        # 加个空行
        print_arr.append({'t': 'line', 'h': 32, 'v': ''})
        # 借书
        send = item.get("send", [])  # ["name"] ["code"]
        if len(send) > 0:
            print_arr.append({'t': 'text', 'h': 40, 'v': u'* * * * * * 借 书 * * * ' + str(len(send)) + u'本'})
        for b in send:
            b = dict(b)
            book_name = u'绘本：' + b.get("name", u'无')
            book_code = u'编号：' + b.get("code", u'无')
            if get_len(book_name) > max_len:
                tmp_arr = split_str_by_len(book_name, max_len)
                for li in tmp_arr:
                    print_arr.append({'t': 'text', 'h': 40, 'v': li})
            else:
                print_arr.append({'t': 'text', 'h': 40, 'v': book_name})
            print_arr.append({'t': 'text', 'h': 40, 'v': book_code})
        # 加个空行
        print_arr.append({'t': 'line', 'h': 32, 'v': ''})
        take = item.get("take", [])
        if len(take) > 0:
            print_arr.append({'t': 'text', 'h': 40, 'v': u'* * * * * * 还 书 * * * ' + str(len(take)) + u'本'})
        for b in take:
            b = dict(b)
            book_name = u'绘本：' + b.get("name", u'无')
            book_code = u'编号：' + b.get("code", u'无')
            if get_len(book_name) > max_len:
                tmp_arr = split_str_by_len(book_name, max_len)
                for li in tmp_arr:
                    print_arr.append({'t': 'text', 'h': 40, 'v': li})
            else:
                print_arr.append({'t': 'text', 'h': 40, 'v': book_name})
            print_arr.append({'t': 'text', 'h': 40, 'v': book_code})
        # 加个空行
        print_arr.append({'t': 'line', 'h': 32, 'v': ''})
        sign = item.get("sign", u'祝您阅读愉快！')
        print_arr.append({'t': 'text', 'h': 40, 'v': u'' + sign})
        # 加个空行
        print_arr.append({'t': 'line', 'h': 80, 'v': ''})
    # 计算打印纸张的高度 单位 mm 注：200 DPI 的打印机 1 mm = 8 point
    for i in print_arr:
        i = dict(i)
        setup_height += i.get('h', 0)
    try:
        setup_height /= 8
        p = TSCLib(width=80, height=setup_height, paper='thermal')
        print_tsc(p, print_arr, line_spacing)
        p.close()
    except Exception, e:
        raise e


# 打印出库单 by tsc
def hub_tsc(book_list):
    max_len = 40  # 可打印文本最大长度 汉字 2 英文 1
    line_spacing = 8  # 行间距
    setup_height = 0  # init
    print_arr = []
    for item in book_list:
        item = dict(item)
        # 加个空行
        print_arr.append({'t': 'line', 'h': 32, 'v': ''})
        title = item.get("title", u'出库单')
        print_arr.append({'t': 'text', 'h': 48, 'v': u'※※' + title + u'※※'})
        hubs = u'来自：' + item.get("hub", u'')
        print_arr.append({'t': 'text', 'h': 48, 'v': hubs})
        club = u'送往：' + item.get("club", u'')
        print_arr.append({'t': 'text', 'h': 48, 'v': club})
        send = item.get("send", [])  # ["name"] ["code"]
        for b in send:
            b = dict(b)
            book_name = u'绘本：' + b.get("name", u'无')
            book_code = u'编号：' + b.get("code", u'无')
            if get_len(book_name) > max_len:
                tmp_arr = split_str_by_len(book_name, max_len)
                for li in tmp_arr:
                    print_arr.append({'t': 'text', 'h': 40, 'v': li})
            else:
                print_arr.append({'t': 'text', 'h': 40, 'v': book_name})
            print_arr.append({'t': 'text', 'h': 40, 'v': book_code})
        # 加个空行
        print_arr.append({'t': 'line', 'h': 48, 'v': ''})
        sign = item.get("sign", u'')
        print_arr.append({'t': 'text', 'h': 40, 'v': sign})
    # 计算打印纸张的高度 单位 mm 注：200 DPI 的打印机 1 mm = 8 point
    for i in print_arr:
        i = dict(i)
        setup_height += i.get('h', 0)
    try:
        setup_height /= 8
        p = TSCLib(width=80, height=setup_height, paper='thermal')
        print_tsc(p, print_arr, line_spacing)
        p.close()
    except Exception, e:
        raise e


def main():
    encoding = sys.stdin.encoding
    if encoding is None:
        encoding = 'gbk'
    parser = argparse.ArgumentParser(description=u'亦启读打印服务', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("job", choices=['hub', 'ps', 'lab', 'ps_tsc', 'hub_tsc'], help="print job")
    JSON_doc = u"""list data ( JSON string )
1、打印配送单：./print ps list  # list 必须包含字段:
title code128 address mobile time note send [(name, code)] take(int) sign
2、打印出库单：./print hub list  # list 必须包含字段:
title hub club send [(name, code)] sign
3、打印绘本标签：./print lab list  # list 必须包含字段:
code code_show club
示例代码：
<pre>
list = [{
    "title": "亦启读出库单",
    "hub": "调配中心-1",
    "club": "亦启读-理想城店",
    "send": [{
        "name": "记忆的项链",
        "code": "A0005-04-09-3688-1"
    }],
    "sign": "签字：__________________"
}]
list_str = JSON.stringify(list)
sh : ./print hub list_str
sh : ./print hub_tsc list_str
</pre>"""
    parser.add_argument("list", help=JSON_doc)
    args = parser.parse_args()
    if not args.list:
        print {'code': -9, 'msg': 'empty list'}
        return
    json_list = json.loads(args.list.decode(encoding))
    if not args.job:
        print {'code': -8, 'msg': 'empty print job'}
        return
    print_job = args.job
    try:
        ui = ' msg ; lion ly \'s house , code '
        if print_job == 'hub':
            t = threading.Thread(target=hub(json_list))
        elif print_job == 'ps':
            t = threading.Thread(target=ps(json_list))
        elif print_job == 'lab':
            t = threading.Thread(target=lab(json_list))
        elif print_job == 'ps_tsc':
            t = threading.Thread(target=ps_tsc(json_list))
        elif print_job == 'hub_tsc':
            t = threading.Thread(target=hub_tsc(json_list))
        else:
            print {'code': -2, 'msg': 'print type error'}
            return
        t.start()
        print {'code': 1, 'msg': 'OK'}
    except NoUSBPrinterError, e:
        print {'code': -8, 'msg': e.msg}
    except BarcodeCodeError, e:
        print {'code': -7, 'msg': e.msg}
    except BarcodeTypeError, e:
        print {'code': -6, 'msg': e.msg}
    except BarcodeSizeError, e:
        print {'code': -5, 'msg': e.msg}
    except KeyError, e:
        print {'code': -4, 'msg': 'not find key: ' + e.message}
    except UnicodeEncodeError, e:
        print {'code': -3, 'msg': e.reason}
    finally:
        return


@click.command()
@click.argument('x')
@click.argument('y')
@click.argument('z')
def show(x, y, z):
    click.echo('x: %s, y: %s, z:%s' % (x, y, z))


if __name__ == "__main__":
    # main()
    # p = TSCLib(width=80, height=50, paper='thermal')
    show()
