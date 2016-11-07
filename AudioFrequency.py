import pyaudio
import wave
import matplotlib.pyplot as pp
import seaborn as sb
import numpy as np

# http://onlinetonegenerator.com/
# audio read based on https://gist.github.com/mabdrabo/8678538

class AudioFrequency:
    RATE = 44100
    FORMAT = pyaudio.paFloat32
    CHUNK = 1024
    RECORD_SECONDS = 2
    CHANNELS = 1
    WAVE_OUTPUT_FILENAME = "file.wav"
    SAVE_FILE = False
    
    audio = pyaudio.PyAudio()
    
    def __init__(self):
        print("init test")
        
    def start(self):
        # start Recording
        stream = self.audio.open(format=self.FORMAT,channels=self.CHANNELS,rate=self.RATE,input=True,frames_per_buffer=self.CHUNK)
        
        frames = []
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            block = stream.read(self.CHUNK)
            frames.append(block)
            
        # stop Recording
        stream.stop_stream()
        stream.close()
        #self.audio.terminate()
        print("recording stopped")
        
        if self.SAVE_FILE:
            waveFile = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
            waveFile.setnchannels(self.CHANNELS)
            waveFile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            waveFile.setframerate(self.RATE)
            waveFile.writeframes(b''.join(frames))
            waveFile.close()
        
        #merge blocks of data into single float vector
        self.data = np.empty(1)
        for i in range(0,len(frames)):
            decoded = np.fromstring(frames[i], 'Float32');
            self.data = np.concatenate((self.data,decoded))
            
        
    def frequency_response(self):
        L = 2**int(np.ceil(np.log2(len(self.data)))) #pad to next power of 2 for efficiency
        Y = np.fft.fft(self.data,L)
        P2 = np.abs(Y/L)
        P1 = 2*P2[0:L/2+1];
        F = self.RATE/2 * np.linspace(0,1,L/2+1)
        #F = np.fft.fftfreq(L,d=1/float(RATE))
        
        ind = P1.argmax()
        
        sb.set_style("darkgrid")
        pp.plot(F,P1)
        pp.plot(F[ind],P1[ind],'o')
        pp.ylabel('Power')
        pp.xlabel('Frequency [Hz]')
        pp.show()


