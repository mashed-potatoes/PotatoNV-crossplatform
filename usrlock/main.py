import sys
import chalk
import argparse
import hashlib
import xml.etree.ElementTree as ET
from os import path
from glob import glob
from . import ui
from InquirerPy import prompt

try:
    from . import imageflasher, fastboot
except Exception as e:
    ui.error("Failed to import some dependencies.")
    ui.error(str(e))
    ui.tip("Install dependencies with pip:", chalk.blue("python3.%d -m pip install -r requirements.txt" % sys.version_info[1]))
    exit(1)


def setup():
    parser = argparse.ArgumentParser(epilog="""Copyright 2020 mashed-potatoes
Copyright 2019 Penn Mackintosh
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.""")
    parser.add_argument("--skip-bootloader", "-s", action="store_true", help="Skip bootloader flashing")
    parser.add_argument("--skip-write-key", "-S", action="store_true", help="Skip NVME writing")
    parser.add_argument("--key", "-k", help="What key should be set?")
    parser.add_argument("--fblock", "-f", help="Set FBLOCK")
    parser.add_argument("--bootloader", "-b", help="Specify bootloader name")
    args = parser.parse_args()

    if not args.skip_bootloader:
        if not args.bootloader:
            args.bootloader = prompt({
                'type': 'list',
                'name': 'bootloader',
                'message': 'Select bootloader:',
                'choices': list(map(lambda x: path.basename(path.split(x)[-2]), glob('bootloaders/*/manifest.xml')))
            })['bootloader']

        args.manifest = f"./bootloaders/{args.bootloader}/manifest.xml"

        if not path.isfile(args.manifest):
            ui.error("Bootloader is invalid or not found!", critical=True)

    if not args.skip_write_key:
        if not args.key:
            args.key = prompt({
                'type': 'input',
                'name': 'key',
                'message': 'What key should be set?',
                'validate': lambda val: len(val) == 16 or 'Excepted 16 symbols'
            })['key']

        if len(args.key) != 16:
            ui.error("Invalid key length!", critical=True)
    
    return args

def flash_images(data: dict):
    flasher = imageflasher.ImageFlasher()
    flasher.connect_serial()
    for image in data["images"]:
        ui.progress(title="Flashing {}".format(image['role']))
        flasher.download_from_disk("./bootloaders/{}/{}"
                                   .format(data['name'], image['path']), int(image['address'], 16))
    ui.success("Bootloader uploaded.")


def write_nvme(key: str):
    m = hashlib.sha256()
    m.update(key.encode())
    fb = fastboot.Fastboot()
    fb.connect()
    fb.write_nvme("USRKEY", m.digest())
    fb.write_nvme("WVLOCK", key.encode())
    ui.success("Bootloader code updated")
    ui.info("Rebooting device...")
    fb.reboot()


def main():
    args = setup()
    if not args.skip_bootloader:
        xmltree = ET.parse(args.manifest)
        bootloader = xmltree.getroot()

        data = bootloader.attrib
        data["images"] = list(map(lambda img: img.attrib, bootloader.findall('image')))
        data["name"] = args.bootloader

        flash_images(data)

    if not args.skip_write_key:
        write_nvme(args.key)
