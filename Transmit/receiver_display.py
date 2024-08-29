import adi
import typing
import matplotlib.pyplot as plt
import numpy as np

from Transmit.driver_config import UsbDriver 

class ReceiverPlot:
    def __init__(self, rx_lo, rf_bandwidth, sdr: adi.Pluto=None, buffer_size=1024) -> None:
        self.rx_lo = int(rx_lo)
        self.rf_bandwidth = int(rf_bandwidth)
        
        if sdr == None:
            session = UsbDriver()
            self.sdr = session.establish_AD9364_usb_connection()
        else:
            self.sdr = sdr

        self.buffer_size = buffer_size        

    # Private #
    def _receive_samples(self) -> np.ndarray:
        rx_samples = self.sdr.rx()
        return np.array(rx_samples)

    def plot_receiver(self) -> None:
        plt.figure()
        rx_samples = self._receive_samples()
        plt.plot(np.real(rx_samples), label='I')
        plt.plot(np.imag(rx_samples), label='Q')
        plt.xlabel('Sample')
        plt.ylabel('Amplitude')
        plt.title('Received Signal')
        plt.legend()
        plt.show()  
