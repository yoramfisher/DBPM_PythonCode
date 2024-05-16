#!/usr/bin/python

#File: plotDD.py
# 6/15/22
from datetime import datetime
from matplotlib import markers
from pytz import timezone
import matplotlib 
from matplotlib import pyplot as plt
import numpy as np
import os
cwd = os.getcwd()
tz = timezone("EST")
dt = datetime.now(tz)
dtfor = (dt.strftime("%Y_%m_%d_%H-%M-%S"))
def plot_Bscan (dSN):
    dat = np.loadtxt((cwd + r"\bscan.txt"), dtype = float, delimiter = None, comments = '%',skiprows = 5,)

    x = (np.array(dat)[:,0] -20)
    tCounts = (np.array(dat)[:,1])
    y = tCounts/np.max(tCounts) * -1
    figB = plt.figure()
    bPlot = figB.add_subplot(1,1,1)
    bPlot.plot(x, y, color ="blue")
 
# To show the plot
    bPlot.set_title("Device Bias Scan SN " + dSN)
    bPlot.set_xlabel("Bias (V)")
    bPlot.set_ylabel("Current (Normalized)")
#plt.show() 
    BpltName = "#F_BScan_SN" + dSN + ".jpg"
    figB.savefig(str(BpltName))
    plt.close()

