from matplotlib.animation import FuncAnimation
import pyaudio
import matplotlib.pyplot as pp
import seaborn as sb
import numpy as np

# http://onlinetonegenerator.com/
# audio read based on https://gist.github.com/mabdrabo/8678538

class AudioFrequency():
    RATE = 44100
    FORMAT = pyaudio.paFloat32
    CHUNK = 1024
    RECORD_SECONDS = 0.1
    CHANNELS = 1
    WAVE_OUTPUT_FILENAME = "file.wav"
    SAVE_FILE = False
    pausing = False
    
    def __init__(self):
        print("init test")
        print("Type 'pause' to pause the plot and 'continue' to continue plotting, or click on the axes")
    
    def check_input(self):
        while True:
            command = input().lower()
            #Check if something has been typed
            if command != "":
                #Pause plot if 'pause' is typed, restart if 'continue' is typed 
                if command == "pause":
                    self.pausing = True
                elif command == "continue":
                    self.pausing = False
                #If one on the two above commands isn't typed, remind user
                else:
                    print("Command not recognised, please enter either 'pause' or 'continue'")
                            
    def connect(self):
        #Setup for detecting mouse button pressed on plot
        self.cidpress = self.fig.canvas.mpl_connect("button_press_event", self.onclick)
            
    def onclick(self, event):
        #Change value of 'pausing' when plot area is clicked on
        if event.inaxes:
            self.pausing ^= True
            
                          
    def start_stream(self):
        audio = pyaudio.PyAudio()
        #start audio stream
        self.stream = audio.open(format=self.FORMAT,
                                 channels=self.CHANNELS,
                                 rate=self.RATE,
                                 input=True,
                                 frames_per_buffer=self.CHUNK)
        
    def setup_plot(self):
        #setup the plot that will display FFT
        self.fig = pp.figure()
        ax = self.fig.add_subplot(111)
        ax.set_xlim(0, 5000)
        ax.set_ylim(0, 0.1)
        self.line, = ax.plot([],[])
        self.line2, = ax.plot([],[], 'o') 
        
    def frequency_response(self, data):
        
        L = 2**int(np.ceil(np.log2(len(data)))) #pad to next power of 2 for efficiency
        Y = np.fft.fft(data,L)
        P2 = np.abs(Y/L)
        P1 = 2*P2[0:L/2+1];
        F = self.RATE/2 * np.linspace(0,1,L/2+1)
        #F = np.fft.fftfreq(L,d=1/float(RATE))  
        ind = P1.argmax()
        
        data_xy = [F, P1, ind]
        return data_xy
    
    def update(self, frame_number):
        line_data = []
        frames = []
        #When plot is paused, new data = previous data
        if self.pausing == True:
            line_data.append(self.line)
            line_data.append(self.line2)
        
        else:
            #take multiple blocks of data from stream
            for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                incoming = self.stream.read(self.CHUNK)
                frames.append(incoming)
    
            #merge blocks of data into single float vector    
            self.data = np.empty(1)
            for i in range(0,len(frames)):
                decoded = np.fromstring(frames[i], 'Float32');
                self.data = np.concatenate((self.data,decoded))
                
            #get frequencyresponse
            FreqResponse = self.frequency_response(self.data)
            
            self.line.set_data(FreqResponse[0], FreqResponse[1])
            self.line2.set_data(FreqResponse[0][FreqResponse[2]], FreqResponse[1][FreqResponse[2]]) #max frequency
            
            line_data.append(self.line)
            line_data.append(self.line2)
            
        return line_data
    
    def animation(self): 
        self.animate = FuncAnimation(self.fig, self.update, interval=50, blit=True)
        pp.show()


                
        