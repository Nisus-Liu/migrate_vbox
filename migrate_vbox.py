#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 60906 2020/6/12
"""
迁移已有 virtual box (含 x.vbox, x.vmdk ), 注册到新的 VirtualBox 中.

适用场景:
case 1: 别处复制过来VB镜像文件, 想要放到当前电脑的VB中复用;
case 2: VB重装了, 旧的虚机信息丢失. 但磁盘文件还在, 还是可以复用的;

使用:

`migrate_vbox.py --vm <your vm dir> --vbxml <VirtualBox.xml>`

查看 help :
`python migrate_vbox.py -h`
"""
# TODO 自动查找 VB xml 位置, 交互提示用户确认.

import os
import logging
from xml.dom import minidom
from xml.dom.minidom import  parse as parse
import psutil
import sys, getopt
import argparse

logging.basicConfig(level=logging.INFO)

# ==由于minidom默认的writexml()函数在读取一个xml文件后，修改后重新写入如果加了newl='\n',会将原有的xml中写入多余的行
#　 ==因此使用下面这个函数来代替
def fixed_writexml(self, writer, indent="", addindent="", newl=""):
    # indent = current indentation
    # addindent = indentation to add to higher levels
    # newl = newline string
    writer.write(indent+"<" + self.tagName)

    attrs = self._get_attributes()
    a_names = attrs.keys()
    # a_names.sort()

    for a_name in a_names:
        writer.write(" %s=\"" % a_name)
        minidom._write_data(writer, attrs[a_name].value)
        writer.write("\"")
    if self.childNodes:
        if len(self.childNodes) == 1 \
                and self.childNodes[0].nodeType == minidom.Node.TEXT_NODE:
            writer.write(">")
            self.childNodes[0].writexml(writer, "", "", "")
            writer.write("</%s>%s" % (self.tagName, newl))
            return
        writer.write(">%s"%(newl))
        for node in self.childNodes:
            if node.nodeType is not minidom.Node.TEXT_NODE:
                node.writexml(writer,indent+addindent,addindent,newl)
        writer.write("%s</%s>%s" % (indent,self.tagName,newl))
    else:
        writer.write("/>%s"%(newl))

minidom.Element.writexml = fixed_writexml

def isVBoxRunning():
    pidList = psutil.pids()
    for pid in pidList:
        pName = psutil.Process(pid).name()
        # VBoxSVC.exe VBoxSDS.exe
        if pName.startswith(("VBox", "vbox")):
            return True
    return False



def registry(virtualBoxXml, vbox, vboxId, hdId, hdFile, hdFormat):
    VbXml = parse(virtualBoxXml)
    vbXmlRoot = VbXml.documentElement
    globalDom = vbXmlRoot.getElementsByTagName("Global")[0]
    # 没有任何虚机时, 也有 <MachineRegistry/>
    machineRegistryDom = globalDom.getElementsByTagName("MachineRegistry")[0]
    machineEntrys = machineRegistryDom.getElementsByTagName("MachineEntry")
    flag = False
    for e in machineEntrys:
        # 已有, 则更新 src
        if e.getAttribute("uuid")[1:-1] == vboxId:
            e.setAttribute("src", vbox)
            flag = True
            break
    if not flag:
        newMe = VbXml.createElement("MachineEntry")
        newMe.setAttribute("uuid", "{" + vboxId + "}")
        newMe.setAttribute("src", vbox)
        machineRegistryDom.appendChild(newMe)
    mediaRegistryList = globalDom.getElementsByTagName("MediaRegistry")
    # 没有任何注册的hd时, MediaRegistry 可能就被 VB 干掉了
    mediaRegistryDom = None
    if len(mediaRegistryList)>0:
        mediaRegistryDom = mediaRegistryList[0]
    else:
        mediaRegistryDom = VbXml.createElement("MediaRegistry")
        hds = VbXml.createElement("HardDisks")
        mediaRegistryDom.appendChild(hds)
        globalDom.insertBefore(mediaRegistryDom, machineRegistryDom.nextSibling)

    hardDisksDom = mediaRegistryDom.getElementsByTagName("HardDisks")[0]
    hdList = hardDisksDom.getElementsByTagName("HardDisk")
    flag1 = False
    for hd in hdList:
        if hd.getAttribute("uuid")[1:-1] == hdId:
            hd.setAttribute("location", hdFile)
            # hd.setAttribute("format", hdFormat)
            flag1 = True
            break
    if not flag:
        newHd = VbXml.createElement("HardDisk")
        newHd.setAttribute("uuid", "{" + hdId + "}")
        newHd.setAttribute("location", hdFile)
        newHd.setAttribute("format", hdFormat)
        newHd.setAttribute("type", "Normal")
        hardDisksDom.appendChild(newHd)

    return VbXml


def parseHdFileInfo(oldVmDir):
    hdFile = ""
    hdFormat = ""
    for file in os.listdir(oldVmDir):
        if file.endswith(".vmdk"):
            hdFile = os.path.join(oldVmDir, file)
            hdFormat = "VMDK"
            break
        if file.endswith(".vdi"):
            hdFile = os.path.join(oldVmDir, file)
            hdFormat = "VDI"
            break
    return hdFile, hdFormat


def parseVboxInfo(oldVmDir):
    """

    :rtype: tuple (.vbox 全路径, vboxId, hard disk id)
    """
    vbox = os.path.basename(oldVmDir) + '.vbox'
    vbox = os.path.join(oldVmDir, vbox)
    logging.info("vbox file name: " + vbox)
    domTree = parse(vbox)
    vbDom = domTree.documentElement
    machine = vbDom.getElementsByTagName("Machine")[0]
    vboxId = machine.getAttribute("uuid")
    vboxId = vboxId[1:-1]
    logging.info("vboxId: " + vboxId)
    hdId = machine.getElementsByTagName("StorageControllers")[0].getElementsByTagName("StorageController")[0] \
               .getElementsByTagName("AttachedDevice")[0].getElementsByTagName("Image")[0].getAttribute("uuid")[1:-1]
    logging.info("hard disk id: " + hdId)

    return vbox, vboxId, hdId


def migrate_vbox(vmDir, virtualBoxXml):
    #
    # 获取 vbox 文件的 uuid vmdk id
    #
    vbox, vboxId, hdId = parseVboxInfo(vmDir)

    #
    # oldVmDir 下搜索 vmdk, vdi 等磁盘文件, 找到一个即停止
    #
    hdFile, hdFormat = parseHdFileInfo(vmDir)
    logging.info("hard disk file: "+hdFile)
    logging.info("hard disk format: "+hdFormat)

    #
    # 注册
    #
    # vbox hardDisk
    VbXml = registry(virtualBoxXml, vbox, vboxId, hdId, hdFile, hdFormat)

    with open(virtualBoxXml, 'w') as f:
        # 缩进 - 换行 - 编码
        VbXml.writexml(f, addindent='  ', newl='\n', encoding='utf-8')
        logging.info("writexml success!")

    return vboxId


if __name__ == '__main__':
    # vagrantWs = 'E:\\Work\\Vagrant\\ws-docker'
    # vmDir = 'E:\\Work\\Vagrant\\VMs\\ws-docker'
    # virtualBoxXml = 'C:\\Users\\60906\\.VirtualBox\\VirtualBox.xml'
    # --vm /path/to/my_vm
    # --vbxml /home/you/.VirtualBox/VirtualBox.xml

    parser = argparse.ArgumentParser(usage = 'migrate_vbox.py --vm <your vm dir> --vbxml <VirtualBox.xml>', description="迁移已有 virtual box (含 x.vbox, x.vmdk ), 注册到新的 VirtualBox 中.")
    parser.add_argument('--vm', type=str, required=True, help='path of your virtual machine, includes `x.vbox` and `x.vmdk`')
    parser.add_argument('--vbxml', type=str, help='Optional, VirtualBox.xml , may like "C:/Users/<user name>/.VirtualBox/VirtualBox.xml"')
    args = parser.parse_args()
    vmDir = args.vm
    virtualBoxXml = args.vbxml
    if virtualBoxXml is None:
        # userdir + .VirtualBox + VirtualBox.xml
        virtualBoxXml = os.path.join(os.path.expanduser('~'), '.VirtualBox', 'VirtualBox.xml')
        # 提示用户 vbxml 是否正确
        p = input('Please confirm VirtualBox.xml is corrected: `' + virtualBoxXml +
                  '`\nOK: [Enter]; Other: [input your VirtualBox.xml]\n>')
        if p !='':
            virtualBoxXml = p

    print("VM dir: ", vmDir)
    print("VirtualBox xml: ", virtualBoxXml)

    exit()

    #
    # 判断 VB 是否在运行
    #
    if isVBoxRunning():
        raise AssertionError("Please exit VirtualBox process first! (It may take a few seconds)")


    if not os.path.exists(vmDir):
        raise FileExistsError(vmDir)
    if not os.path.exists(virtualBoxXml):
        raise FileExistsError(virtualBoxXml)


    # ---- START --------------------------------------------------
    migrate_vbox(vmDir, virtualBoxXml)



# trash #
# getopt 处理参数
# vmDir = ""
# virtualBoxXml = ""
# argv = sys.argv[1:]
# usage = 'migrate_vbox.py --vm <your vm dir> --vbxml <VirtualBox.xml>'
# try:
#     opts, args = getopt.getopt(argv,"",["vm=","vbxml="])
# except getopt.GetoptError as e:
#     print(usage)
#     sys.exit(2)
#
# if(len(opts)<2):
#     print(usage)
#     sys.exit(2)
#
# for opt, arg in opts:
#     if opt in ("--vm"):
#         vmDir = arg
#     elif opt in ("--vbxml"):
#         virtualBoxXml = arg
# print("VM dir: ", vmDir)
# print("VirtualBox xml: ", virtualBoxXml)