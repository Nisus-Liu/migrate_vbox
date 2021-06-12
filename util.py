import os


def pick_virtual_box_xml_path(virtual_box_xml):
    if virtual_box_xml is None:
        # userdir + .VirtualBox + VirtualBox.xml
        virtual_box_xml = os.path.join(os.path.expanduser('~'), '.VirtualBox', 'VirtualBox.xml')
        # 提示用户 vbxml 是否正确
        p = input('Please confirm VirtualBox.xml is corrected: `' + virtual_box_xml +
                  '`\nOK: [Enter]; Other: [input your VirtualBox.xml]\n>')
        if p !='':
            virtual_box_xml = p
    return virtual_box_xml