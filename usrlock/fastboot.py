from time import sleep
import traceback
from . import ui
from fastbootpy import FastbootDevice, FastbootManager

def handle_exception(e: Exception, message: str):
    ui.error(message)
    traceback.print_exc()
    exit(1)


class Fastboot:
    def connect(self):
        ui.info("Waiting for fastboot device")
        while True:
            devices = FastbootManager.devices()
            if len(devices) == 1:
                self.fb_dev = FastbootDevice.connect(devices[0])
                ui.info(f"Connected to device {devices[0]}")
                break
            elif len(devices) > 1:
                ui.error("More than one fastboot device is connected!")

    def write_nvme(self, prop: str, data: bytes):
        cmd = f"getvar:nve:{prop}@".encode('UTF-8')
        print(cmd.decode("utf-8"))
        cmd += data
        ui.info(f"Command: {cmd}")
        result = self.fb_dev.send(cmd)
        ui.info(f"Getvar result: {result}")

    def reboot(self):
        result = self.fb_dev.reboot()
        ui.info(f"Reboot result: {result}")
    
    def reboot_bootloader(self):
        result = self.fb_dev.reboot_bootloader()
        ui.info(f"Reboot bootloader result: {result}")
    
