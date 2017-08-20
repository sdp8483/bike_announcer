'''
Created on Jul 15, 2017

@author: Sam

Plot windaq data collection for power consumption
'''
import __init__  # @UnusedImport
import windaq as w
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def windaq_to_df(fpath):
    file_contents = w.windaq(fpath)
    
    currentCH = 1
    voltageCH = 2
    enableCH  = 3
    speakerCH = 4
    
    return pd.DataFrame({'time':       file_contents.time(),
                        'current':     file_contents.data(currentCH),
                        'voltage':     file_contents.data(voltageCH),
                        'amp enable':  file_contents.data(enableCH),
                        'speaker':     file_contents.data(speakerCH),
                        'power':       [V*(I/1000) for V, I in zip(file_contents.data(voltageCH), file_contents.data(currentCH))]})

left_fpath  = "on_left.WDH"
right_fpath = "on_right.WDH"
tone_fpath  = "tone.WDH"
idle_fpath  = "idle.WDH"

currentCH = 1
voltageCH = 2
enableCH  = 3
speakerCH = 4

left_df  = windaq_to_df(left_fpath)
right_df = windaq_to_df(right_fpath)
tone_df  = windaq_to_df(tone_fpath)

''' find amp enable for left file '''


''' plotting '''
fig, (ax0, ax1, ax2, ax3) = plt.subplots(nrows=4)
fig.set_size_inches(16,9, forward=True)
fig.set_dpi(80)
fig.set_facecolor('w')
fig.set_edgecolor('k')

ax0.plot(left_df['time'], left_df['speaker'])
ax0.plot(left_df['time'], left_df['amp enable'])
ax0.set_title('Speaker Output')

ax1.plot(left_df['time'], left_df['voltage'])
ax1.set_title("Battery Voltage")

ax2.plot(left_df['time'], left_df['current'])
ax2.set_title("Current Draw")

ax3.plot(left_df['time'], left_df['power'])
ax3.set_title("Power")

''' remove ticks '''
ax0.xaxis.set_major_locator(ticker.NullLocator())
ax0.xaxis.set_minor_locator(ticker.NullLocator())
ax1.xaxis.set_major_locator(ticker.NullLocator())
ax1.xaxis.set_minor_locator(ticker.NullLocator())
ax2.xaxis.set_major_locator(ticker.NullLocator())
ax2.xaxis.set_minor_locator(ticker.NullLocator())

plt.show()