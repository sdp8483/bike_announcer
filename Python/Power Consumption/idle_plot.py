'''
Created on Jul 22, 2017

@author: Sam

plot of the idle current, voltage, power
'''
import __init__  # @UnusedImport
import windaq as w
import pandas as pd
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

idle_fpath  = "idle.WDH"

currentCH = 1
voltageCH = 2
enableCH  = 3
speakerCH = 4

df  = windaq_to_df(idle_fpath)
print "{:.2f}mA Average Current".format(df['current'].mean())
print "{:.2f}mA Max Current".format(df['current'].max())
print "{:.2f}mA Min Current".format(df['current'].min())

''' plotting '''
fig, host = plt.subplots()
fig.set_size_inches(16,9, forward=True)
fig.set_dpi(80)
fig.set_facecolor('w')
fig.set_edgecolor('k')

par1 = host.twinx()

p1, = host.plot(df['time'], df['voltage'], "b-", label="Voltage")
p2, = par1.plot(df['time'], df['current'], "g-", label="Current")

host.set_xlim(0, 10)
host.set_ylim(0, 5)
par1.set_ylim(0, 500)

host.set_title("Idle Current Consumption", fontsize='xx-large')
host.set_xlabel("Time [seconds]", fontsize='x-large')
host.set_ylabel("Battery Voltage [V]", fontsize='x-large')
par1.set_ylabel("Battery Current [mA]", fontsize='x-large')

host.yaxis.label.set_color(p1.get_color())
par1.yaxis.label.set_color(p2.get_color())

tkw = dict(size=4, width=1.5)
host.tick_params(axis='y', colors=p1.get_color(), **tkw)
par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
host.tick_params(axis='x', **tkw)

lines = [p1, p2]

host.legend(lines, [l.get_label() for l in lines], loc='upper right', fontsize='x-large')
plt.savefig("idle.png", transparent=True)