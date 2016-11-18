import AudioFrequency
import threading

obj = AudioFrequency.AudioFrequency()


threading1 = threading.Thread(target=obj.check_input)
threading1.daemon = True
threading1.start()
obj.start_stream()
obj.setup_plot()
obj.connect()
obj.animation()


