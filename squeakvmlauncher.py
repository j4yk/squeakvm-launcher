#! python
import os
import struct
import subprocess
import configparser

CONFIG_FILE = os.path.join(os.environ['LOCALAPPDATA'], 'squeakvmlauncher.ini')
# TODO: make this platform independent
CONFIG_SECTION = 'VMs'

def launch_squeak(image_filename):
    with open(image_filename, 'rb') as f:
        image_version = read_magic_version_number(f)
    vm_executable = vm_executable_for_version(image_version)
    subprocess.call([vm_executable, image_filename])

def read_magic_version_number(file):
    magic_word, = struct.unpack('i', file.read(4))
    # TODO: add support for different endianness images
    # TODO: add support for 64 bit images
    return magic_word

def vm_executable_for_version(image_version):
    executable = lookup_executable(image_version)
    if not executable:
        executable = choose_with_gui(image_version)
        save_executable(image_version, executable)
    return executable

config_parser = configparser.RawConfigParser()

def lookup_executable(image_version):
    global config_parser
    config_parser.read(CONFIG_FILE)
    try:
        return config_parser.get(CONFIG_SECTION, str(image_version))
    except (configparser.NoSectionError, configparser.NoOptionError):
        return None

def choose_with_gui(image_version):
    import tkinter
    from tkinter import filedialog
    root = tkinter.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title='Choose a VM for image version ' + str(image_version))

def save_executable(image_version, executable):
    if not config_parser.has_section(CONFIG_SECTION):
        config_parser.add_section(CONFIG_SECTION)
    config_parser.set(CONFIG_SECTION, str(image_version), executable)
    with open(CONFIG_FILE, 'w') as config_file:
        config_parser.write(config_file)

if __name__ == '__main__':
    import sys
    launch_squeak(sys.argv[1])
