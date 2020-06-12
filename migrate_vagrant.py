#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 60906 2020/6/13
"""
迁移 vagrant

迁移vagrant使用的VB虚拟机, 并同步vagrant的虚机id元数据.
当, vagrant工作目录的id元数据没有变, VB虚机的id也没有改动时, 您仅仅使用 `migrate_vbox` 脚本, 迁移 vbox 即可.
一旦任何一方发生改变, 导致两者关联不上了. 就需要使用此脚本. 一步到位, 先迁移vbox, 再不同vagrant和VB.
"""
import getopt
import logging
import os
import sys

from migrate_vbox import migrate_vbox, isVBoxRunning

logging.basicConfig(level=logging.INFO)


def migrate_vagrant(vgws, vmsDir, virtualBoxXml, vmName=""):
    # 虚机字典
    vmDict = {} # 虚机名 -> 虚机名全路径
    for vm in os.listdir(vmsDir):
        vmDict[vm] = os.path.join(vmsDir, vm)


    # 单机目录样式: .vagrant\machines\default\virtualbox\id
    # 多机目录样式: machines\{机器名xxx}\virtualbox\id
    machinesPath = os.path.join(vgws, ".vagrant" + os.sep + "machines")
    machineNames = os.listdir(machinesPath)
    vagrantIdFileList = []
    vgwsName = os.path.basename(vgws)
    for m in machineNames:
        idfn = os.path.join(machinesPath, m, "virtualbox" + os.sep +"id")
        # 单虚机时, 名为'default' , 实际虚机名由Vagrant文件配置的, 这里不好获取. 没有指定时, 认为工作目录名就是虚机名.
        if m == "default":
            m = vmName if vmName != "" else vgwsName
            logging.info("'default' VM name: " + m)
        vagrantIdFileList.append((m, idfn)) # 虚机名, id文件全路径


    # 去虚机存储目录下, 找到对应虚机
    for vm, vidf in vagrantIdFileList:
        vmDir = vmDict[vm]
        # 迁移 vbox , i.e. 注册到新的 VB 上
        vboxId = migrate_vbox(vmDir, virtualBoxXml)
        # 同步 vagrant id 元数据, 以匹配 vbox id
        if not os.path.exists(vidf):
            logging.warning("vagrant id file of %s not exists: %s", vm, vidf)
        else:
            with open(vidf, "w") as vidf:
                vidf.write(vboxId)
        logging.info("=> migrate %s :: %s success", vgwsName, vm)


if __name__ == '__main__':
    # --ws /path/to/vagrant/my_vm  vagrant工作目录, 关联一台虚机时, 虚机目录名就是 my_vm ; 关联多态虚机时, 如管理了一个集群, 其下则会有多个虚机名目录.
    # --vms /path/vo/VirtualBox VMs  VB 默认的虚机存储目录. 默认可能如 C:\Users\60906\VirtualBox VMs . '管理>>全局设定>>常规' 可查看或修改.
    # --vbxml VB 虚机元数据文件, 如: /home/you/.VirtualBox/VirtualBox.xml
    # --vm-name 虚机名称, 如: my_vm . 单虚机时, 元数据下对应目录名'default' , 实际虚机名由Vagrant文件配置的, 这里不好获取. 当没有指定此选项时, 认为工作目录名就是虚机名.
    vgws = ""
    vmsDir = ""
    vmName = ""
    virtualBoxXml = ""
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv,"",["ws=", "vms=", "vbxml=", "vm-name="])
    except getopt.GetoptError as e:
        print('migrate_vagrant.py --ws <your vagrant workspace> --vms <your VMs dir> --vbxml <VirtualBox.xml> [--vm-name <VM mame>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("--ws"):
            vgws = arg
        elif opt in ("--vms"):
            vmsDir = arg
        elif opt in ("--vm-name"):
            vmName = arg
        elif opt in ("--vbxml"):
            virtualBoxXml = arg
    print("vagrant workspace: ", vgws)
    print("VMs dir: ", vmsDir)

    #
    # 判断 VB 是否在运行
    #
    if isVBoxRunning():
        raise AssertionError("Please exit VirtualBox process first! (it will waste a few seconds)")


    if not os.path.exists(vgws):
        raise FileExistsError(vgws)
    if not os.path.exists(vmsDir):
        raise FileExistsError(vmsDir)


    migrate_vagrant(vgws, vmsDir, virtualBoxXml, vmName)

    logging.info("migrate_vagrant success!")
