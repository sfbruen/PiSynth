from matplotlib.animation import FuncAnimation
import pyaudio
import matplotlib.pyplot as pp
import seaborn as sb
import numpy as np

# http://onlinetonegenerator.com/
# audio read based on https://gist.github.com/mabdrabo/8678538

class AudioFrequency:
    RATE = 44100
    FORMAT = pyaudio.paFloat32
    CHUNK = 1024*4
    RECORD_SECONDS = 0.2
    CHANNELS = 1
    
    def __init__(self):
        print("init test")
        self.peak_data = np.zeros(1)
    
    def connect(self):
        #setup for detecting mouse button pressed on plot
        self.cidpress = self.fig.canvas.mpl_connect("button_press_event", self.onclick)
        self.plot_paused = False
            
    def onclick(self, event):
        if event.inaxes:
            if self.plot_paused == False:
                self.pause_plot()
            else:
                self.start_plot()        
    
    @property
    def num_chunks(self):
        return int(self.RATE / self.CHUNK * self.RECORD_SECONDS)
        
    def start_stream(self):
        audio = pyaudio.PyAudio()
        #start audio stream
        self.stream = audio.open(format=self.FORMAT,
                                 channels=self.CHANNELS,
                                 rate=self.RATE,input=True,
                                 frames_per_buffer=self.CHUNK)
        
    def setup_plot(self):
        #setup the plot that will display FFT
#        self.fig = pp.figure()
#        ax = self.fig.add_subplot(111)
        self.fig, (ax1, ax2) = pp.subplots(2,1)

        ax1.set_xlim(0, 5000)
        ax1.set_ylim(0, 0.04)
        ax2.set_xlim(0,100)
        ax2.set_ylim(10, 1000)
        
        self.line, = ax1.plot([],[])
        self.line2, = ax1.plot([],[], 'o')
        self.line3, = ax2.plot([],[])
        self.textObj = ax1.text(1,0.002," ",
                                  horizontalalignment='left',
                                  verticalalignment='center')
    
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
        Y = np.fft.fft(data,L)
        P2 = np.abs(Y/L)
        P1 = 2*P2[0:int(L/2)+1];
        F = self.RATE/2 * np.linspace(0,1,L/2+1)
        ind = P1.argmax()
        
        self.peak_data = np.concatenate((self.peak_data,np.array([F[ind]])))
        data_xy = [F, P1, ind]
        return data_xy
    
    def update(self, frame_number):
        line_data = []
        frames = []
        #take multiple blocks of data from stream
        for i in range(0, self.num_chunks):
            incoming = self.stream.read(self.CHUNK)
            frames.append(incoming)
            
        #merge blocks of data into single float vector    
        self.data = np.empty(1)
        for i in range(0,len(frames)):
            decoded = np.fromstring(frames[i], 'Float32');
            self.data = np.concatenate((self.data,decoded))
        
        #get frequencyresponse
        FreqResponse = self.frequency_response(self.data)
        AmpPeak = FreqResponse[1][FreqResponse[2]]
        FreqPeak = FreqResponse[0][FreqResponse[2]]
        
        #update line data for plotting
        self.line.set_data(FreqResponse[0], FreqResponse[1])
        self.line2.set_data(FreqPeak, AmpPeak)        
        self.line3.set_data(np.arange(np.size(self.peak_data)) , self.peak_data)
        self.textObj.set_text("{:.2f}Hz".format(FreqPeak))
        self.textObj.set_x(FreqPeak)
        self.textObj.set_y(AmpPeak) 
        
        line_data.append(self.line)
        line_data.append(self.line2)
        line_data.append(self.line3)        
        # does textobj need to be added too?
        return line_data
    
    def animation(self): 
        self.animate = FuncAnimation(self.fig, self.update, interval=50,blit=False)
        pp.show()
    
        