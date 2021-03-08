import binascii
import itertools
import serial
import serial.tools.list_ports
import sys
import os
import time
from . import ui

def calc_crc(data, crc=0):
    for char in data:
        crc = ((crc << 8) | char) ^ binascii.crc_hqx(bytes([(crc >> 8) & 0xFF]), 0)
    for i in range(0,2):
        crc = ((crc << 8) | 0) ^ binascii.crc_hqx(bytes([(crc >> 8) & 0xFF]), 0)
    return crc & 0xFFFF


BOOT_HEAD_LEN = 0x4F00
MAX_DATA_LEN = 0x400
IDT_BAUDRATE = 115200
IDT_VID=0x12D1
IDT_PID=0x3609


class ImageFlasher:
    def __init__(self):
        self.serial = None
        self.headframe = bytes([0xFE, 0x00, 0xFF, 0x01])
        self.dataframe = bytes([0xDA])
        self.tailframe = bytes([0xED])
        self.ack = bytes([0xAA])

    def send_frame(self, data):
        crc = calc_crc(data)
        data += crc.to_bytes(2, byteorder="big", signed=False)
        try:
            self.serial.reset_output_buffer()
            self.serial.reset_input_buffer()
            self.serial.write(data)
            ack = self.serial.read(1)
            if ack and ack != self.ack:
                ui.error(f"Invalid ACK from device! Read: {hex(ack)}, excepted: {hex(self.ack[0])}", critical=True)
        except Exception as e:
            ui.error(str(e), critical=True)

    def send_head_frame(self, length, address):
        self.serial.timeout = 0.09
        ui.debug("Sending header frame")
        data = self.headframe
        data += length.to_bytes(4, byteorder="big", signed=False)
        data += address.to_bytes(4, byteorder="big", signed=False)
        self.send_frame(data)

    def send_data_frame(self, n, data):
        self.serial.timeout = 0.45
        ui.debug("Sending data frame")
        head = bytearray(self.dataframe)
        head.append(n & 0xFF)
        head.append((~ n) & 0xFF)
        self.send_frame(bytes(head) + data)

    def send_tail_frame(self, n):
        if self.serial:
            self.serial.timeout = 0.01
        ui.debug("Sending tail frame")
        data = bytearray(self.tailframe)
        data.append(n & 0xFF)
        data.append((~ n) & 0xFF)
        self.send_frame(bytes(data))

    def send_data(self, data, length, address):
        if isinstance(data, bytes):
            length = len(data)
        n_frames = length // MAX_DATA_LEN + (1 if length % MAX_DATA_LEN > 0 else 0)
        self.send_head_frame(length, address)
        n = 0
        while length > MAX_DATA_LEN:
            if isinstance(data, bytes):
                f = data[n * MAX_DATA_LEN:(n + 1) * MAX_DATA_LEN]
            else:
                f = data.read(MAX_DATA_LEN)
            self.send_data_frame(n + 1, f)
            n += 1
            length -= MAX_DATA_LEN
            ui.progress(value=n, max_value=n_frames)
        if length:
            if isinstance(data, bytes):
                f = data[n * MAX_DATA_LEN:]
            else:
                f = data.read()
            self.send_data_frame(n + 1, f)
            n += 1
        ui.progress(value=100)
        self.send_tail_frame(n + 1)
        time.sleep(0.5)

    def download_from_disk(self, fil, address):
        if fil == "-":
            f = sys.stdin
        else:
            f = open(fil, "rb")
        self.send_data(f, os.stat(fil).st_size, address)

    def connect_serial(self, device=None):
        if not device:
            ports = serial.tools.list_ports.comports(include_links=False)
            for port in ports:
                if port.vid == IDT_VID and port.pid == IDT_PID:
                    ui.info(f"Autoselecting {port.hwid} aka {port.description} at {port.device}")
                    if device:
                        ui.error("Multiple devices detected in IDT mode", critical=True)
                    else:
                        device = port.device
        if not device:
            ui.error("Need a device in IDT mode plugged in to this computer", critical=True)
        self.serial = serial.Serial(dsrdtr=True, rtscts=True, port=device.replace("COM", r"\\.\COM"), baudrate=IDT_BAUDRATE, timeout=1)

    def close(self):
        try:
            self.serial.close()
        except:
            pass
