'''
Created on Jul 23, 2017

@author: Sam
'''
'''
Created on Jul 22, 2017

@author: Sam

plot during playback of ONLEFT.WAV
'''
import __init__  # @UnusedImport
import windaq as w
import pandas as pd
import numpy as np
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
                        'speaker':     file_contents.data(speakerCH)
                        })

left_fpath  = "on_left.WDH"

currentCH = 1
voltageCH = 2
enableCH  = 3
speakerCH = 4

df  = windaq_to_df(left_fpath)
df['power'] = df['voltage'] * (df['current'] / 1000)

''' min current point '''
min_current = df['current'][np.argmin(df['current'])]
min_time    = df['time'][np.argmin(df['current'])]

''' max current point '''
max_current = df['current'][np.argmax(df['current'])]
max_time    = df['time'][np.argmax(df['current'])]



''' plotting '''
fig, (ax0, ax1, ax2) = plt.subplots(nrows=3)
fig.set_size_inches(16,9, forward=True)
fig.set_dpi(80)
fig.set_facecolor('w')
fig.set_edgecolor('k')

ax0.plot(df['time'], df['voltage'], '-b', label='Battery Voltage')
ax0.plot(df['time'], df['amp enable'], '-c', label='Amp Enable')
ax0.plot(df['time'], df['speaker'], '-y', label='Speaker')
ax0.legend()
ax0.set_ylabel("V")
ax0.get_yaxis().get_major_formatter().set_useOffset(False)
ax0.set_title("Voltage")

ax1.plot(df['time'], df['current'], '-g')
ax1.set_ylabel("mA")
ax1.get_yaxis().get_major_formatter().set_useOffset(False)
ax1.set_title("Current")
ax1.annotate("{:.0f}mA".format(min_current),
    xy=(min_time, min_current), xycoords='data',
    xytext=(5, -25), textcoords='offset points',
    arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
ax1.annotate("{:.0f}mA".format(max_current),
    xy=(max_time, max_current), xycoords='data',
    xytext=(5, 25), textcoords='offset points',
    arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))

ax2.plot(df['time'], df['power'], '-m')
ax2.set_ylabel('W')
ax2.get_yaxis().get_major_formatter().set_useOffset(False)
ax2.set_xlabel('Seconds')
ax2.set_title("Power")

''' remove ticks '''
ax0.xaxis.set_major_locator(ticker.NullLocator())
ax0.xaxis.set_minor_locator(ticker.NullLocator())
ax1.xaxis.set_major_locator(ticker.NullLocator())
ax1.xaxis.set_minor_locator(ticker.NullLocator())

#plt.savefig("idle.png", transparent=True)
plt.show()