import adi
import numpy as np
import matplotlib.pyplot as plt
import time
import multiprocessing

from Transmit.driver_config import UsbDriver
from Transmit.tx_single_tone import Transmit
from Transmit.receiver_display import ReceiverPlot

class SDRSession:
    def __init__(self):
        session = UsbDriver()
        self.sdr = session.establish_AD9364_usb_connection()
        
        transmitter_process = multiprocessing.Process(target=self.start_transmitter, args=(self.sdr, 1090e6))
 
        time.sleep(1)
        reception = ReceiverPlot(1090e6, 20e6, self.sdr) 
        reception.plot_receiver()
    
    def start_transmitter(self, freq):
        transmission = Transmit(self.sdr)
        transmission.transmit_single_tone(freq)



