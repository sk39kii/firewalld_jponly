#! /bin/python
# -*- coding: utf-8 -*-
u"""firewalldのゾーンファイルに日本のIPv4をsourceとして書き込む
"""

import os
import shutil
from xml.etree.ElementTree import Element, SubElement, ElementTree
import xml.etree.ElementTree as ET
from xml.dom import minidom


def read_jptxt():
    u"""日本のIPv4が記載されたファイルを読み込み"""
    iplist = []
    # IPが記載されたファイル(jp.txt)からIPを取得しコマンドを生成
    with open('jp.txt', 'r') as fr:
        for line in fr:
            cidr = line.strip()
            if len(cidr) > 0 and cidr.startswith('#') is False:
                iplist.append(cidr)
    return iplist


def create_firewallcmd_sh(iplist):
    u"""firewall-cmdのシェルを生成"""
    # 生成したコマンドをファイルに書き込み
    outfile = 'firewall-cmd-jponly.sh'
    with open(outfile, 'w') as fw:
        # シェバンの書き込み
        fw.write('#!/bin/sh' + os.linesep)
        # firewall-cmdの書き込み
        zone = 'jponly'
        cmdstr = 'firewall-cmd --permanent --add-source='
        for ip in iplist:
            cmd = '{0:s}{1:s} --zone={2:s}'.format(cmdstr, ip, zone)
            fw.write(cmd + os.linesep)
        # 最後にhttpサービスの設定を書き込み
        cmd = 'firewall-cmd --permanent --add-service=http --zone=jponly'
        fw.write(cmd + os.linesep)


def upd_zonexml(input_zonefile, iplist=None):
    u"""ゾーンのXMLファイルを直接編集"""

    # 元のoldファイルは削除
    backup_zonefile = input_zonefile+'.old'
    if os.path.exists(backup_zonefile):
        os.remove(backup_zonefile)
    # バックアップ
    shutil.copyfile(input_zonefile, backup_zonefile)

    # ゾーンの読み込み
    tree = ET.parse(input_zonefile)
    root = tree.getroot()
    # sourceタグを削除
    for source in root.findall('source'):
        root.remove(source)
    # IPアドレスを<source address="ip address" />として追加
    if iplist is not None:
        for ip in iplist:
            ET.SubElement(root, 'source').set('address', ip)

    # 書き込み
    # tree.write(input_zonefile,
    #            encoding='utf-8',
    #            xml_declaration=True)

    # 読み易いように変換してから書き込む
    newtree = ET.fromstring(prettify(root))
    ElementTree(newtree).write(input_zonefile,
                               encoding='utf-8',
                               xml_declaration=True)


def prettify(elem):
    u"""読み易いように修正
    http://ja.pymotw.com/2/xml/etree/ElementTree/create.html
    Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def main():
    # 日本のIPアドレスをファイルから読み込み
    iplist = read_jptxt()

    # firewall-cmdのシェルを作成
    create_firewallcmd_sh(iplist)

    # ゾーンファイルを直接編集
    input_zonefile = '/etc/firewalld/zones/jponly.xml'
    upd_zonexml(input_zonefile, iplist)


if __name__ == "__main__":
    main()
