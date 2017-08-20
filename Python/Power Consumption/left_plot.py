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
                        }).iloc[::230]

left_fpath  = "on_left.WDH"

currentCH = 1
voltageCH = 2
enableCH  = 3
speakerCH = 4

df  = windaq_to_df(left_fpath)

amp_on = np.argwhere(df['amp enable']>3)

print "{:.2f}mA Average Current".format(df['current'].iloc[amp_on[0][0]:amp_on[-1][0]].mean())
print "{:.2f}mA Max Current".format(df['current'].iloc[amp_on[0][0]:amp_on[-1][0]].max())
print "{:.2f}mA Min Current".format(df['current'].iloc[amp_on[0][0]:amp_on[-1][0]].min())
print
print "Playing Time: {:.4f} seconds".format(df['time'].iloc[amp_on[-1][0]] - df['time'].iloc[amp_on[0][0]])

''' plotting '''
fig, host = plt.subplots()
fig.set_size_inches(16,9, forward=True)
fig.set_dpi(80)
fig.set_facecolor('w')
fig.set_edgecolor('k')

par1 = host.twinx()

p11, = host.plot(df['time'], df['voltage'], "b-", label="Battery Voltage")
p12, = host.plot(df['time'], df['amp enable'], "c-", label="Amplifier Enable")
p13, = host.plot(df['time'], df['speaker'], "m-", label="Speaker Voltage")
p2, = par1.plot(df['time'], df['current'], "g-", label="Battery Current")

host.set_xlim(0, 3)
host.set_ylim(-8, 8)
par1.set_ylim(0, 2000)

host.set_title("Playing ONLEFT.WAV", fontsize='xx-large')
host.set_xlabel("Time [seconds]", fontsize='x-large')
host.set_ylabel("Battery Voltage [V]", fontsize='x-large')
par1.set_ylabel("Battery Current [mA]", fontsize='x-large')

host.yaxis.label.set_color(p11.get_color())
par1.yaxis.label.set_color(p2.get_color())

tkw = dict(size=4, width=1.5)
host.tick_params(axis='y', colors=p11.get_color(), **tkw)
par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
host.tick_params(axis='x', **tkw)

lines = [p11, p12, p13, p2]

host.legend(lines, [l.get_label() for l in lines], loc='upper right', fontsize='x-large')
plt.savefig("left.png", transparent=True)
#plt.show()