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
##################
#Number of scan points
###################
cwd = os.getcwd() + "txts" + "\\"
T4Upars = np.loadtxt(r"T4UPars.ini",dtype = float, delimiter = None, comments = '%')
numPoints = int(T4Upars[3])
numRows = 0   # Set below based on file size

def plot_z(dSN):
    dat = np.loadtxt((cwd + r"\zscan.txt"), dtype = float, delimiter = None, comments = '%',skiprows = 5, )

    numRows = int(dat.shape[0] / numPoints)
    y =[]
    for z in range(numRows):
        zstart = z * numPoints 
        zend = zstart + numPoints
        tCounts = np.abs(np.array(dat)[zstart:zend,2] + np.array(dat)[zstart:zend,3] + np.array(dat)[zstart:zend,4] + np.array(dat)[zstart:zend,5])
        AB = (np.abs(np.array(dat)[zstart:zend,2] + np.array(dat)[zstart:zend,4])) / tCounts
        CD = (np.abs(np.array(dat)[zstart:zend,3] + np.array(dat)[zstart:zend,5])) / tCounts
        x = (np.array(dat)[zstart:zend,0] - np.min(np.array(dat)[zstart:zend,0]))
#y = (np.array(dat)[:,1])
        yarray = [AB-CD]
        y.append(yarray)
    figH = plt.figure()
    for i in range(numRows):
        #print(y[i])
        yr=np.reshape(np.array(y[i]), numPoints)
        # hPlot = figH.add_subplot(11,1,1)
        plt.plot(x, yr, label = str(i) )
        plt.legend(loc="upper left")
 
# To show the plot
    # plt.set_title("Device Horizontal Scan SN"+ dSN)
    # plt.set_xlabel("position (mm)")
    # plt.set_ylabel("Current (Normalized)")
    plt.show() 
#     pltNameH = "#HScan_SN" + dSN + ".jpg"
#     figH.savefig(pltNameH)
#     plt.close()
#     datV = np.loadtxt((cwd +r"\vscan.txt"), dtype = float, delimiter = None, comments = '%',skiprows = 5,)
#     tCountsV = np.abs(np.array(datV)[:,2] + np.array(datV)[:,3] + np.array(datV)[:,4] + np.array(datV)[:,5])
#     AD = (np.abs(np.array(datV)[:,2] + np.array(datV)[:,5])) / tCountsV
#     BC = np.abs(np.array(datV)[:,3] + np.array(datV)[:,4]) / tCountsV
#     x1 = (np.array(datV)[:,1] - np.min(np.array(datV)[:,1]))
# #y = (np.array(dat)[:,1])
#     y1 = AD-BC

#     figV = plt.figure()
#     vPlot = figV.add_subplot(1,1,1)
#     vPlot.plot(x1, y1, color ="green")
 
# # To show the plot
#     vPlot.set_title("Device Vertical Scan SN" + dSN)
#     vPlot.set_xlabel("position (mm)")
#     vPlot.set_ylabel("Current (Normalized)")
# #plt.show() 
#     pltNameV = "#VScan_SN" + dSN + ".jpg"
#     figV.savefig(pltNameV)
    # plt.close()
junk = plot_z("garbage")