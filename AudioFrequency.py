from matplotlib.animation import FuncAnimation
import pyaudio
import matplotlib.pyplot as pp
import seaborn as sb #just importing this formats the plots
import numpy as np
from math import ceil
from datetime import datetime
from matplotlib.dates import DateFormatter

# http://onlinetonegenerator.com/
# audio read based on https://gist.github.com/mabdrabo/8678538

class AudioFrequency():
    RATE = 44100
    FORMAT = pyaudio.paFloat32
    CHUNK = 1024 * 2
    RECORD_SECONDS = 0.2
    CHANNELS = 1
    PLOT_SECONDS = 5
    pausing = False
    
    def __init__(self):
        self.peak_data =  [] #peak frequency timeseries
        self.time_data = []
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
    
    @property
    def num_chunks(self):
        return ceil(self.RATE / self.CHUNK * self.RECORD_SECONDS)
        
    @property
    def num_peaks_time(self):
        return ceil(self.PLOT_SECONDS / self.RECORD_SECONDS)


    def start_stream(self):
        audio = pyaudio.PyAudio()
        #start audio stream
        self.stream = audio.open(format=self.FORMAT,
                                 channels=self.CHANNELS,
                                 rate=self.RATE,
                                 input=True,
                                 frames_per_buffer=self.CHUNK)
        
    def setup_plot(self):
        #setup the plot that will display FFT and peak frequency timeseries
        self.fig, (self.ax1, self.ax2) = pp.subplots(2,1)

        self.line, = self.ax1.plot([],[])
        self.line2, = self.ax1.plot([],[], 'o')
        self.line3, = self.ax2.plot(datetime.now(), 0,'o-')
        self.textObj = self.ax1.text(1,0.002," ",
                                  horizontalalignment='left',
                                  verticalalignment='center')
        
        self.ax1.set_xlim(10,10000)
        self.ax1.set_xscale("log", nonposx='clip')
        self.ax2.set_ylim(10,10000)
#        self.ax2.set_yscale("log", nonposy='clip')

        #Remove microseconds from x axis labels
        self.ax2.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        #Display microseconds for cursor position
        self.ax2.fmt_xdata = DateFormatter('%H:%M:%S.%f')
        
        self.ax1.set_ylabel("Amplitude", fontsize=12, fontweight='bold')
        self.ax1.set_xlabel("Frequency", fontsize=12, fontweight='bold')
        self.ax2.set_ylabel("Max Frequency", fontsize=12, fontweight='bold')
        self.ax2.set_xlabel("Time", fontsize=12, fontweight='bold')
        
        pp.setp(self.ax2.xaxis.get_majorticklabels(), rotation=30)
#        pp.tight_layout()

    def pause_plot(self):
        #pause animation
        print("Pausing plot...")
        self.animate.event_source.stop()
        self.plot_paused = True
        
    def start_plot(self):
        #restart animation
        print("Starting plot...")
        self.animate.event_source.start()
        self.plot_paused = False

    def frequency_response(self, data):
        
        L = 2**int(np.ceil(np.log2(len(data)))) #pad to next power of 2 for efficiency
        Y = np.fft.rfft(data,L)
        F = np.fft.rfftfreq(L,1/self.RATE)
        P1 = 2*np.abs(Y/L)
        ind = np.argmax(P1)
        
        data_xy = [F, P1, ind]
        return data_xy
    
    def update(self, frame_number):
        line_data = []
        frames = []

        #When plot is paused, new data = previous data
        if self.pausing == True:
            line_data.append(self.line)
            line_data.append(self.line2)
            line_data.append(self.line3)
    
        else:
            #take multiple blocks of data from stream
            for i in range(0, self.num_chunks):
                incoming = self.stream.read(self.CHUNK,exception_on_overflow=False)
                frames.append(incoming)
    
            self.time_data.append(datetime.now())
    
            #merge blocks of data into single float vector    
            audio_data = np.empty(1)
            for i in range(0,len(frames)):
                decoded = np.fromstring(frames[i], 'Float32');
                audio_data = np.concatenate((audio_data,decoded))
    
            #get frequency response
            FreqResponse = self.frequency_response(audio_data[1:-1])
            AmpPeak = FreqResponse[1][FreqResponse[2]]
            FreqPeak = FreqResponse[0][FreqResponse[2]]
            
            # add new timeseries peak data, and remove old data if necessary
            self.peak_data.append(float(FreqPeak))
            if len(self.peak_data) == self.num_peaks_time:
                del self.peak_data[0]
                del self.time_data[0]
                
            #update line data for plotting
            self.line.set_data(FreqResponse[0], FreqResponse[1])
            self.line2.set_data(FreqPeak, AmpPeak)        
            self.line3.set_data(self.time_data, self.peak_data)
            self.textObj.set_text("{:.2f}Hz".format(FreqPeak))
            self.textObj.set_x(FreqPeak)
            self.textObj.set_y(AmpPeak)
    
            #update axes limits
    #        PeakLog = float(np.log10(FreqPeak))
    #        self.ax1.set_xlim(10**(PeakLog-1), 10**(PeakLog+1))
            self.ax1.set_xlim(0.2*FreqPeak , 5*FreqPeak)
            self.ax1.set_ylim(0, max(FreqResponse[1])*1.1)
        
            if len(self.peak_data) > 1:
#                update time axes once more than one reading is available
                self.ax2.set_xlim(self.time_data[0], self.time_data[-1])

            if len(set(self.peak_data)) > 1:
#                rescale based on min and max freq
                self.ax2.set_ylim(min(self.peak_data)*0.9, max(self.peak_data)*1.1)
            else:
                #only one frequency value in vector (or the first sample):
                self.ax2.set_ylim(0.9*self.peak_data[0] , 1.1*self.peak_data[0])
        
            line_data.append(self.line)
            line_data.append(self.line2)
            line_data.append(self.line3)        
            # does textobj need to be added too?

        return line_data
    
    def animation(self): 
        self.animate = FuncAnimation(self.fig, self.update, interval=50, blit=False)
        pp.show()


                
        
