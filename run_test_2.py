#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 17:44:30 2016

@author: thomasbruen
"""

import AudioFrequency
import matplotlib.pyplot as pp

pp.ion()
obj = AudioFrequency.AudioFrequency()


obj.start_stream()
obj.setup_plot()
#obj.connect()
#obj.animation()

for i in range(20):
    ld = obj.update(1)
    
obj.stream.close()