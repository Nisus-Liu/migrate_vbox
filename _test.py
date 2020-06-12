#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 60906 2020/6/12
from migrate_vagrant import migrate_vagrant
from migrate_vbox import migrate_vbox




if __name__ == "__main__":
    # migrate_vbox("E:\\Work\\Vagrant\\VMs\\ws-docker", "C:\\Users\\60906\\.VirtualBox\\VirtualBox.xml")
    migrate_vagrant("E:\Work\Vagrant\ws-docker", "E:\Work\Vagrant\VMs", "C:\\Users\\60906\\.VirtualBox\\VirtualBox.xml")
