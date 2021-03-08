import time
import traceback
from adb.fastboot import FastbootCommands
from . import ui


def handle_exception(e: Exception, message: str):
    ui.error(message)
    traceback.print_exc()
    exit(1)


class Fastboot:
    def connect(self):
        self.fb_dev = FastbootCommands()
        while True:
            devs = self.fb_dev.Devices()
            if len(list(devs)):
                time.sleep(1)
                break
        self.fb_dev.ConnectDevice()

    def write_nvme(self, prop: str, data: bytes):
        try:
            self.fb_dev._protocol.SendCommand(b'getvar', b'nve:' + prop + b'@' + data)
        except Exception as e:
            handle_exception(e, 'Failed to write NVME prop')

    def reboot(self):
        try:
            self.fb_dev.Reboot()
            self.fb_dev.Close()
        except Exception as e:
            handle_exception(e, 'Failed to reboot device')

    def reboot_bootloader(self):
        try:
            self.fb_dev.RebootBootloader()
            self.fb_dev.Close()
        except Exception as e:
            handle_exception(e, 'Failed to reboot device')

    def unlock(self, code: str):
        try:
            response = self.fb_dev.Oem('unlock %s' % code)
            print(response)
        except Exception as e:
            handle_exception(e, "Failed to unlock bootloader")
