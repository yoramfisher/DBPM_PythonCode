from datetime import datetime
from pytz import timezone
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import os
tz = timezone("EST")
dt = datetime.now(tz)
dtfor = (dt.strftime("%Y_%m_%d_%H-%M-%S"))

cwd = os.getcwd()
plot_series = 3; # 2 for on, 3 for off
theVoltage = 50.0

def plot_Raster(dSN):
        global plot_series
        f = np.loadtxt(cwd + "/TXCraster" +".txt", dtype = float,comments="%", delimiter=None, skiprows = 5)

        Ztot =  np.abs((np.array(f[:,plot_series])))
        Zmax = np.max(Ztot)

# Load data from CSV
#dat = np.genfromtxt(r"raster.txt", dtype = float,comments="%", delimiter=None)
        fMax = np.max(f[:,plot_series])


        X_dat = f[:,0]-np.min(f[:,0])
        Y_dat = f[:,1]-np.min(f[:,1])
        Z_dat = Ztot/Zmax

# Convert from pandas dataframes to numpy arrays
        X, Y, Z, = np.array([]), np.array([]), np.array([])
        for i in range(len(X_dat)):
                X = np.append(X, X_dat[i])
                Y = np.append(Y, Y_dat[i])
                Z = np.append(Z, Z_dat[i])

# create x-y points to be used in heatmap
        xi = np.linspace(X.min(), X.max(), 1000)
        yi = np.linspace(Y.min(), Y.max(), 1000)

# Interpolate for plotting
        zi = griddata((X, Y), Z, (xi[None,:], yi[:,None]), method='cubic')

# I control the range of my colorbar by removing data 
# outside of my range of interest
        zmin = 0
        zmax = 1
        zi[(zi<zmin) | (zi>zmax)] = None
        #figR = plt.figure()
        #rPlot = figR.add_subplot(1,1,1)
        
#plt.zlabel("Intensity (Normalized)")
#plt.show() 
#
#
#
#
# Create the contour plot

        plt.contourf(xi, yi, zi, 15, cmap=plt.cm.viridis, vmax=zmax, vmin=zmin,)
        cbar = plt.colorbar()
        cbar.set_label('Intensity (Normalized)', rotation=90) 
        plt.title ("Diamond Plate " + dSN + " "  +" 2D scan")
        plt.xlabel ("Position (mm)")
        plt.ylabel ("Position (mm)")
#plt.show()
        rpltName = "#RasterScan_DP_" + dSN +  ".jpg"
        plt.savefig(str(rpltName))
        plt.close()

plot_Raster(' 132 -20 V')