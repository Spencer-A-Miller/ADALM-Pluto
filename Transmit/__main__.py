from Transmit.driver_config import UsbDriver
from Transmit.tx_single_tone import Transmit
from Transmit.receiver_display import ReceiverPlot
from Transmit.transceiver import SDRSession
import threading

#from Transmit.driver_test import test_connection
'''
Summary:
The SDRSession class uses a Manager to share the SDR object between processes.
The start_transmitter method transmits a single tone indefinitely.
The ReceiverPlot class is used to receive and plot the signal.
The Transmit class is used to configure and transmit the tone.
The UsbDriver class handles the connection to the ADALM-Pluto device.

Goal:
Jam Out
1575 +- 10 MHz (L1) (20 MHz wide)
1227 +- 10 MHz (L2) (20 MHz Wide)
sweep both at the same time if possible

'''

def jam_L1_and_L2():
    print("jamming L1 & L2")
    sdr_session_one = UsbDriver()
    sdr_session_two = UsbDriver()

    sdr_one = sdr_session_one.establish_AD9364_usb_connection()
    sdr_two = sdr_session_two.establish_AD9364_usb_connection()

    session_one = Transmit(sdr_one)
    session_two = Transmit(sdr_two)

    thread1 = threading.Thread(target=session_one.power_sweep_single_tone, args=(1575e6, -50, 0, 10, 5))
    thread2 = threading.Thread(target=session_two.power_sweep_single_tone, args=(1227e6, -50, 0, 10, 5))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

def main():
    print("running")
    #jam_L1_and_L2()

    session = Transmit()
    session.chirp_linear_sweep_constant_gain(-50)
    #session.chirp_test()

    #session = Transmit()
    #session.power_sweep_single_tone(1575e6, -50, 10, 10, 5) # Rising in power
    #session.freq_sweep_constant_gain(-10, 1565e6, 1587e6, 2e6, 1)
    

    #session.test_chirp()
    #session.test_sinc()
    #session.transmit_sinc_tone(1300e6)
    #session.test_chirp()

    #session.transmit_single_tone(1090e6) # Single Tone testing
    #session.power_sweep_single_tone(1090e6)
    #session.freq_sweep_constant_gain(-10)
    #session.jam_spectrum()

    #session = ReceiverPlot(1090e6, 20e6, session.sdr)
    #session.plot_receiver()

    #session = ReceiverPlot(1090e6, 20e6)
    #xmt = Transmit(1090e6)
    #xmt.transmit_single_tone()
    #session.plot_receiver()

if __name__ == "__main__":
    main()