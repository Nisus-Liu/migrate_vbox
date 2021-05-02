#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 60906 2020/6/12
import os

# from migrate_vagrant import migrate_vagrant
# from migrate_vbox import migrate_vbox

def let_user_pick(options):
    print("Please choose:")
    for idx, element in enumerate(options):
        print("{}) {}".format(idx+1,element))
    res = None
    while res is None:
        i = input("Enter number: ")
        if i == '':
            # exit
            return -1
        try:
            if 0 < int(i) <= len(options):
                res = int(i)
                break
        except:
            pass
    return res


if __name__ == "__main__":
    # migrate_vbox("E:\\Work\\Vagrant\\VMs\\ws-docker", "C:\\Users\\60906\\.VirtualBox\\VirtualBox.xml")
    # migrate_vagrant("E:\Work\Vagrant\ws-docker", "E:\Work\Vagrant\VMs", "C:\\Users\\60906\\.VirtualBox\\VirtualBox.xml")
    # os.makedirs("./a/b", exist_ok=True)
    # with open("./a/b/c.txt", "w") as vidf:
    #     vidf.write("vboxId")
    # print(os.path.dirname("E:\\Work\\Vagrant\\Kits\\migrate_vbox\\a\\b\\c.txt"))
    # print(os.path.dirname("./a/b/c.txt"))
    p = input("路径正确吗?")
    if p=='':
        print("对的")
    else:
        print("新的路径: " + p)
