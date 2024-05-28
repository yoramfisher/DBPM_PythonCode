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
cwd = os.getcwd() + "txts" + "\\"
tz = timezone("EST")
dt = datetime.now(tz)
dtfor = (dt.strftime("%Y_%m_%d_%H-%M-%S"))
def plot_HV(dSN):
    # HSCAN *****************************
    dat = np.loadtxt((cwd + r"\hscan.txt"), dtype = float, delimiter = None, comments = '%',skiprows = 5, )
    A = np.array(dat)[:,2]
    B = np.array(dat)[:,3]
    C = np.array(dat)[:,4]
    D = np.array(dat)[:,5]

    tCounts = np.abs(A + B + C + D )
    CD = (np.abs(C + D)) / tCounts
    AB = (np.abs(A + B)) / tCounts


    x = (np.array(dat)[:,0] - np.min(np.array(dat)[:,0]))
    #y = (np.array(dat)[:,1])
    y = CD-AB
    figH = plt.figure()
    hPlot = figH.add_subplot(1,1,1)
    hPlot.plot(x, y, color ="blue")
 
# To show the plot
    hPlot.set_title("Device Horizontal Scan SN"+ dSN)
    hPlot.set_xlabel("position (mm)")
    hPlot.set_ylabel("Current (Normalized)")
#plt.show() 
    pltNameH = "#HScan_SN" + dSN + ".jpg"
    figH.savefig(pltNameH)
    plt.close()


    # VSCAN *****************************

    datV = np.loadtxt((cwd +r"\vscan.txt"), dtype = float, delimiter = None, comments = '%',skiprows = 5,)
    A = np.array(datV)[:,2]
    B = np.array(datV)[:,3]
    C = np.array(datV)[:,4]
    D = np.array(datV)[:,5]

    tCountsV = np.abs(A + B + C + D)
    AD = (np.abs(A + D)) / tCountsV
    BC = (np.abs(B + C)) / tCountsV
    x1 = np.array(datV)[:,1] - np.min(np.array(datV)[:,1])
    #y = (np.array(dat)[:,1])
    y1 = AD-BC

    figV = plt.figure()
    vPlot = figV.add_subplot(1,1,1)
    vPlot.plot(x1, y1, color ="green")
 
# To show the plot
    vPlot.set_title("Device Vertical Scan SN" + dSN)
    vPlot.set_xlabel("position (mm)")
    vPlot.set_ylabel("Current (Normalized)")
#plt.show() 
    pltNameV = "#VScan_SN" + dSN + ".jpg"
    figV.savefig(pltNameV)
    plt.close()




if __name__ == "__main__":
    plot_HV("000")    