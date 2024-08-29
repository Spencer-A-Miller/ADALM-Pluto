import time
import adi
from typing import Optional
import numpy as np
from scipy.signal import chirp


from Transmit.driver_config import UsbDriver # type: ignore

class Transmit:
    def __init__(self, sdr: adi.Pluto=None, sample_rate: int=10e6) -> None:
        if sdr is None:
            session = UsbDriver()
            self.sdr = session.establish_AD9364_usb_connection()
        else:
            self.sdr = sdr
 
        self.sample_rate = sample_rate
    
    def power_sweep_single_tone(self, freq: int, start_power: int=-50, stop_power: int=10, step_power:int=10, step_duration: int=5) -> None:
        '''
        Generate transmit power sweep from -80 to 0 dB
        '''
        # Configure the transmitter parameters for power sweep
        self.sdr.tx_lo = int(freq)
        self.sdr.tx_cyclic_buffer = False
        self.sdr.tx_rf_bandwidth = int(10e6)  # Set the transmit bandwidth to 20 MHz
        self.sdr.tx_sample_rate = int(self.sample_rate)

        # Generate the tone
        num_samples = int(self.sample_rate * 1)  # Generate 1 second worth of samples
        t = np.arange(num_samples) / self.sample_rate
        tone = np.exp(2j * np.pi * freq * t)
        #print(f"Transmitting a {freq/1e6} MHz tone indefinitely")

        while True:
            for tx_gain in range(start_power, stop_power, step_power):
                #print(f"tx_gain = {tx_gain}")
                self.sdr.tx_hardwaregain_chan0 = tx_gain # Increase to increase tx power, valid range is -80 to 0 dB
                self.sdr.tx(tone)
                print(f"TX Gain: {tx_gain} dB for {step_duration} seconds")
                time.sleep(step_duration)

    def freq_sweep_constant_gain(self, gain: int, start_freq: int=1050e6, stop_freq: int=1650e6, step_freq:int=50e6, step_duration: int=5) -> None:
        """
        TX sweeping frequency at single power level using ADALM-Pluto.
        """

        # Configure the transmitter parameters
        self.sdr.tx_cyclic_buffer = True
        self.sdr.tx_rf_bandwidth = int(20e6)  # Set the transmit bandwidth to 20 MHz
        self.sdr.tx_sample_rate = int(self.sample_rate)
        self.sdr.tx_hardwaregain_chan0 = gain # Increase to increase tx power, valid range is -90 to 0 dB

        num_samples = int(self.sample_rate * 1)  # Generate 1 second worth of samples
        t = np.arange(num_samples) / self.sample_rate

        for tx_freq in range(int(start_freq), int(stop_freq), int(step_freq)):
            # Generate the tone from the frequency
            tone = np.exp(2j * np.pi * int(tx_freq) * t)
    
            # Transmit the tone for the specified duration
            print(f"Transmitting a {tx_freq/1e6} MHz tone for {step_duration} seconds")
            self.sdr.tx_lo = int(tx_freq)
            self.sdr.tx_destroy_buffer()
            #time.sleep(1)
            self.sdr.tx(tone)
            time.sleep(step_duration)

    def jam_spectrum(self, bandwidth: int=20e6, center_freq: int=1325e6, gain: int=-10) -> None:
        '''
        WORK IN PROGRESS
        Supposed to transmit at high power over a wide spectrum from the center frequency. The power spectrum is not
        as wide as expected. TO-DO: Convolve mutliple frequencies
        '''
        # Configure the transmitter parameters
        self.sdr.tx_lo = int(center_freq)
        self.sdr.tx_cyclic_buffer = True
        self.sdr.tx_rf_bandwidth = int(bandwidth)  # Set the transmit bandwidth to 20 MHz
        self.sdr.tx_sample_rate = int(self.sample_rate)
        self.sdr.tx_hardwaregain_chan0 = gain # Increase to increase tx power, valid range is -90 to 0 dB

        num_samples = int(self.sample_rate * 1)  # Generate 1 second worth of samples
        t = np.arange(num_samples) / self.sample_rate

        # Generate the tone from the frequency
        tone = np.exp(2j * np.pi * int(center_freq) * t) * np.exp(2j * np.pi * int(1600e6) * t)
    
        # Transmit the tone for the specified duration
        print(f"Transmitting a {center_freq/1e6} MHz tone over {bandwidth/1e6} bandwidth")
        time.sleep(2)
        self.sdr.tx(tone)

    def transmit_single_tone(self, freq: int, duration: int=None) -> None:
        """
        Transmit a single tone at a specific frequency using ADALM-Pluto.

        Parameters:
        freq (int): Frequency of the tone in Hz.
        duration (int): Duration of the transmission in seconds.
        sample_rate (int): Sample rate in samples per second (default is 1 MHz).
        """

        # Configure the transmitter parameters
        self.sdr.tx_lo = int(freq)
        self.sdr.tx_cyclic_buffer = True
        self.sdr.tx_rf_bandwidth = int(20e6)  # Set the transmit bandwidth to 20 MHz
        self.sdr.tx_sample_rate = int(self.sample_rate)
        self.sdr.tx_hardwaregain_chan0 = -10 # Increase to increase tx power, valid range is -90 to 0 dB

        # Generate the tone        
        num_samples = int(self.sample_rate * 1)  # Generate 1 second worth of samples
        t = np.arange(num_samples) / self.sample_rate
        tone = np.exp(2j * np.pi * freq * t)

        # Transmit the tone indefinitely if duration is None
        if duration is None:
            print(f"Transmitting a {freq/1e6} MHz tone indefinitely")
            #while True:
            self.sdr.tx(tone)
        else:
            # Transmit the tone for the specified duration
            print(f"Transmitting a {freq/1e6} MHz tone for {duration} seconds")
            self.sdr.tx(tone)
            time.sleep(duration)

    def transmit_sinc_tone(self, carrier_freq: int, duration=None) -> None:
        tx_lo = carrier_freq
        self.sdr.tx_rf_bandwidth = int(self.sample_rate)
        self.sdr.tx_lo = int(tx_lo)
        self.sdr.tx_cyclic_buffer = True
        self.sdr.tx_hardwaregain_chan0 = int(-10)
        self.sdr.tx_buffer_size = int(2**18)

        def sinc(carrier_freq):
            N = 2**16
            f0 = carrier_freq
            fs = self.sample_rate
            w0 = 2*np.pi*f0/fs
            ts = 1 / float(fs)
            t = np.arange(1, N * ts, ts)

            #(0.5 * np.pi * t * carrier_freq)

            c1 = np.cos(2 * np.pi * t ) * 2**14
            s1 = 1j * np.sin(2 * np.pi * t * carrier_freq) * 2**14

            c2 = np.cos(2 * np.pi * t * carrier_freq) * 2**14
            s2 = 1j * np.sin(-2 * np.pi * t * carrier_freq) * 2**14

            #return ((1 / (2j * (2 * np.pi * t * carrier_freq))) * ((c1 + s1) - (c2 - s2)))
            return (((1 / (2j * (2 * np.pi * t * carrier_freq))) * 2**14) * ((c1 + s1) - (c2 - s2)))
            #(2 * np.pi * t * carrier_freq)
        self.sdr.tx(sinc(carrier_freq))
        

        

        '''
        def sinc(x):
            return np.sinc(x / np.pi)
        
        
        x = np.linspace(-1e-9, 1e-9, 400)  # Duration of 2 nanoseconds
        y = sinc(x)
        pulse_duration = 2e-9

        self.sdr.tx_cyclic_buffer = True
        self.sdr.tx_hardwaregain_chan0 = -10
        bandwidth = int(200e3)
        self.sdr.tx_rf_bandwidth = bandwidth  # Set the transmit bandwidth to 200k Hz
        y_modulated = y * np.exp(2j * np.pi * carrier_freq * x) * 2**14
        self.sdr.tx(y_modulated)
        '''

        #num_samps = int(pulse_time * self.sample_rate)
        #pulse = np.ones(num_samps, dtype=np.complex64)
        #self.sdr.tx(pulse)
        
        #self.sdr.tx_lo = int(center_freq)
        #num_samps = int(10000)
        #t = np.arange(num_samps)/self.sample_rate
        #print(f"t = {t}")
        #sinc_tone = np.sinc(t)
        #sinc_tone *= 2**14
        #sinc_tone = sinc_tone / np.max(np.abs(sinc_tone))
        #print(f"sinc_tone = {sinc_tone}")
        #sinc_tone = sinc_tone * 1j #* np.zeros_like(sinc_tone)
        #self.sdr.tx(sinc_tone)

        # Create Transmit waveform
       # time_axis = np.linspace(0, pulse_duration, 1000)
       # np.sinc(time_axis)
       # print(f"time_axis = {time_axis}")
       # f0 = - int(bandwidth / 2)
       # alpha = bandwidth / pulse_duration
       # 
       # self.sdr.sample_rate = self.sample_rate
       # self.sdr.tx_lo = int(1350e6)
       # self.sdr.gain_control_mode_chan0 = "manual"
       # self.sdr.tx_hardwaregain_chan0 = -10 # Increase to increase tx power, valid range is -90 to 0 dB
       # self.sdr.tx_cyclic_buffer = True

        #trans_chirp = 2*14 # The PlutoSDR expects samples to be between -2^14 and +2^14, not -1 and +1 like some SDRs
        #print(f"The chirp is {len(trans_chirp)} long")
        #self.sdr.tx(trans_chirp)

        #self.sdr.tx_sample_rate = int(self.sample_rate)
        #self.sdr.tx_hardwaregain_chan0 = -10 # Increase to increase tx power, valid range is -90 to 0 dB

        # Generate the sinc tone        
        #num_samples = int(self.sample_rate * 1)  # Generate 1 second worth of samples

        # Generation of transmitted signal
        #t = np.arange(num_samples) / self.sample_rate
        #tone = np.sinc(t*freq / np.pi)
        #tone = np.exp(2j * np.pi * freq * t)

        # Transmit the tone indefinitely if duration is None
       # if duration is None:
       #     print(f"Transmitting sinc indefinitely")
       #     #while True:
       #     self.sdr.tx(chirp_tone)
       # else:
       #     # Transmit the tone for the specified duration
       #     print(f"Transmitting sinc for {duration} seconds")
       #     self.sdr.tx(chirp_tone)
       #     time.sleep(duration)

    def chirp_test(self):

        # Define waveform properties
        sample_rate = 60000000
        pulse_duration = 140e-6 # sec
        num_samps = int(sample_rate * pulse_duration)
        if(~(num_samps%1024)):
            num_samps = 1024*(num_samps//1024)
        if(num_samps == 0):
            num_samps = 1024
        print(num_samps)
        bandwidth = 20000000 #20e6

        # Create transmit waveform
        # Create axis for transmitted chirp
        time_axis = np.linspace(0, pulse_duration, num_samps)
        f0 = - bandwidth / 2
        f1 = + bandwidth / 2
        c = 3e8 # Speed of light
        alpha = bandwidth / pulse_duration

        # Configure properties
        self.sdr.sample_rate = 60000000 #60e6
        self.sdr.tx_rf_bandwidth = 20000000 #20e6
        self.sdr.tx_lo = 2400000000
        self.sdr.gain_control_mode_chan0 = "manual"
        self.sdr.tx_hardwaregain_chan0 = -20

        #Configure rx properties
        self.sdr.gain_control_mode_chan0 = 'manual'
        self.sdr.rx_hardwaregain_chan0 = 70.0 # dB
        self.sdr.rx_lo = 2400000000
        self.sdr.sample_rate = 60000000
        self.sdr.rx_rf_bandwidth = 20000000 # filter width, just set it to the same as sample rate for now
        self.sdr.rx_buffer_size = num_samps
        self.sdr._rxadc.set_kernel_buffers_count(1) # set buffers to 1 (instead of the default 4) to avoid stale data on Pluto

        # Configuration data channels
        self.sdr.tx_enabled_channels = [0]
        self.sdr.rx_enabled_channels = [0]

        # Generation of transmitted signal
        trans_chirp = np.exp(1j * 2 * np.pi * (f0 * time_axis + (alpha * time_axis ** 2) / 2))

        trans_chirp = 2*14 # The PlutoSDR expects samples to be between -2^14 and +2^14, not -1 and +1 like some SDRs
        #print("The length of transmitted chirp.",len(trans_chirp))

        self.sdr.tx_cyclic_buffer = True # Enable cyclic buffers
        self.sdr.tx(trans_chirp)

    #def test_sinc(self):
    #    sample_rate = 10e6  # 1 MSPS
    #    carrier_freq = 1300e6  # 1300 MHz

    #    self.sdr.tx_rf_bandwidth = int(sample_rate)
    #    self.sdr.tx_lo = int(1500e6)
    #    self.sdr.tx_cyclic_buffer = True
    #    self.sdr.tx_hardwaregain_chan0 = int(-10)
    #    self.sdr.tx_buffer_size = int(2**18)

    #    # Generate a simple tone
    #    N = 2**16
    #    fs = 1e9
    #    ts = 1 / float(fs)
    #    #t = np.arange(1, N * ts, ts)
    #    #signal = np.cos(2 * np.pi * t * carrier_freq) * 2**14
    #    #c1 = np.cos(2 * np.pi * t * carrier_freq) * 2**14
    #    #s1 = 1j * np.sin(2 * np.pi * t * carrier_freq) * 2**14

    #    #c2 = np.cos(2 * np.pi * t * carrier_freq) * 2**14
    #    #s2 = 1j * np.sin(-2 * np.pi * t * carrier_freq) * 2**14

    #    #signal = ((np.sin(2 * np.pi * t * carrier_freq))/(2 * np.pi * t * carrier_freq)) * 2**14
    #    #signal = ((1 / (2j * (2 * np.pi * t * carrier_freq))) * ((c1 + s1) - (c2 - s2)))
    #    
    #    t = np.arange(-N//2, N//2) * ts  # Center the time array around zero

    #    bandwidth = 56e6  # 600 MHz
    #    sinc_width = bandwidth / (2 * np.pi)

    #    # Use np.sinc to avoid division by zero and modulate by the carrier frequency
    #    sinc_signal = np.sinc(t * sinc_width)
    #    modulated_signal = sinc_signal * np.cos(2 * np.pi * t * carrier_freq) * 2**14

    #    self.sdr.tx(modulated_signal)

    #def test_chirp(self):
    #    sample_rate = 10e6
    #    freq_center =  1300e6 # 2.5e9 
    #    duration = 1 
    #    bandwidth = 2e6 

    #    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    #    chirp_signal = np.exp(1j * 2 * np.pi * (freq_center * t + 0.5 * bandwidth * t**2 / duration))
    #    self.sdr.tx_enabled_channels = [0]
    #    self.sdr.tx_rf_bandwidth = int(bandwidth) 
    #    self.sdr.tx_lo = int(freq_center)
    #    self.sdr.tx_cyclic_buffer = True 
    #    self.sdr.tx_hardwaregain = -10 
    #    self.sdr.sample_rate = int(sample_rate) 

    #    self.sdr.tx(chirp_signal)

    #    try:
    #        while True:
    #            time.sleep(1)
    #    except KeyboardInterrupt:
    #        print("killed by user")

    #    self.sdr.tx_destroy_buffer()

    def chirp_linear_sweep_constant_gain(self, gain: int, start_freq: int=1e6, stop_freq: int=1255e6, step_freq:int=0, step_duration: int=0) -> None:
        """
        TX sweeping frequency at single power level using ADALM-Pluto.
        """

        # Configure the transmitter parameters
        self.sdr.tx_cyclic_buffer = False
        self.sdr.tx_rf_bandwidth = int(20e6)  # Set the transmit bandwidth to 20 MHz
        self.sdr.tx_sample_rate = int(20e6)
        self.sdr.tx_hardwaregain_chan0 = gain # Increase to increase tx power, valid range is -90 to 0 dB

        num_samples = int(self.sample_rate * 1)  # Generate 1 second worth of samples
        t = np.arange(num_samples) / self.sample_rate
        self.sdr.tx_lo = int(1227e6)
        print(f"Transmitting a chirp tone")

        Instantaneous_freq = start_freq
        chirp = np.exp((2j * np.pi * t) / (self.sample_rate / Instantaneous_freq))
        while True:
            chirp = 0
            Instantaneous_freq = start_freq
            chirp = np.exp((2j * np.pi * t) / (self.sample_rate / Instantaneous_freq))
            while Instantaneous_freq < stop_freq:
                Instantaneous_freq = Instantaneous_freq * 10
                waveform_at_NextFrequency = np.exp((2j * np.pi * t) / (self.sample_rate / Instantaneous_freq))
                self.sdr.tx(waveform_at_NextFrequency)

            #for tx_freq in range(int(start_freq), int(stop_freq), int(step_freq)):
                # Generate the tone from the frequency
                #tone = np.exp(2j * np.pi * int(tx_freq) * t)
        
                # Transmit the tone for the specified duration
                
                #self.sdr.tx_destroy_buffer()
                #time.sleep(1)
                #self.sdr.tx(tone)
                #time.sleep(step_duration)
            