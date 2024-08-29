"""
This class provides functionality to control USB drivers 
on the host PC and check COM ports until a working one is found.

This class iterates through available COM ports and attempts to 
establish a connection with the ADALM-Pluto device. The USB connection 
path is identified using the format 'usb:bus.port.device', where:
- 'usb' specifies that the device is connected via USB.
- 'bus' is the USB bus number.
- 'port' is the USB port number on the bus.
- 'device' is the device number on the port.

For example, 'usb:1.7.5' uniquely identifies the USB connection 
path for the ADALM-Pluto device on your system. 
This information is useful for ensuring that the correct 
device is being accessed, especially when multiple USB devices are connected.

The class will continue to check COM ports until a working one is 
found, allowing for robust and flexible device management.
"""

import adi
from typing import Optional

# Check pluto COM port with 'iio_info -s'

class UsbDriver:
    def __init__(self) -> None:
        self.usb_paths = ['usb:1.15.5', 'usb:1.8.5', 'usb:1.10.5', 'usb:1.12.5', 'usb:1.3.5','usb:1.4.5', 'usb:1.5.5', 'usb:1.7.5', 'usb.1.7.5']
        self.sdr = None

    def establish_default_usb_connection(self) -> adi.Pluto:
        for path in self.usb_paths:
            try:
                self.sdr = adi.Pluto(path)
                print(f"Pluto Object Create. Connected to {path}")
                self.sdr.rx_enabled_channels = [0]
                return self.sdr
            except Exception as e:
                print(f"Failed to connect to {path}: {e}")
        #print("No device found on any USB path.")
        raise Exception('FATAL: No Device Found on COM port')
    
    def establish_AD9361_usb_connection(self) -> adi.Pluto:
        for path in self.usb_paths:
            try:
                self.sdr = adi.ad9361(path)
                print(f"\nAD9361 Device Found. Connected to {path}")
                self.sdr.rx_enabled_channels = [0]
                return self.sdr
            except Exception as e:
                print(f"Failed to connect to {path}: {e}.... Checking next COM Port")
        #print("No device found on any USB path.")
        raise Exception('FATAL: No Device Found on COM port')

    def establish_AD9364_usb_connection(self) -> adi.Pluto:
        for path in self.usb_paths:
            try:
                self.sdr = adi.ad9364(path)
                print(f"\nAD9364 Device Found. Connected to {path}")
                self.sdr.rx_enabled_channels = [0]
                return self.sdr
            except Exception as e:
                print(f"Failed to connect to {path}: {e}.... Checking next COM Port")
        #print("No device found on any USB path.")
        raise Exception('FATAL: No Device Found on COM port') 