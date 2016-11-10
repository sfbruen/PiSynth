import AudioFrequency
#reload(AudioFrequency) #otherwise pyc file doesn't update

obj = AudioFrequency.AudioFrequency()
#obj.start()
obj.load_440()
obj.frequency_response()