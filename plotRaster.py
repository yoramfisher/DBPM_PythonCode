from datetime import datetime
from pytz import timezone
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import os
import sys


#
#  GLOBALS
#

MAX_CLIP_VAL = 1.0


tz = timezone("EST")
dt = datetime.now(tz)
dtfor = (dt.strftime("%Y_%m_%d_%H-%M-%S"))

cwd = os.getcwd()
def plot_Raster(dSN,volts, tMax=None):
	f = np.loadtxt(cwd + "/raster"+ str(volts) +".txt", dtype = float,comments="%", delimiter=None, skiprows = 5)
       
	Ztot =  np.abs((np.array(f[:,2]) + np.array(f[:,3]) + np.array(f[:,4]) + np.array(f[:,5])))
	Zmax = (np.array(f[:,2]) + np.array(f[:,3]) + np.array(f[:,4]) + np.array(f[:,5])) # np.max(Ztot)

# Load data from CSV
#dat = np.genfromtxt(r"raster.txt", dtype = float,comments="%", delimiter=None)
	fMax = np.max(np.abs(f[:,2:5]))
	if tMax != None:
		fMax = tMax


	X_dat = f[:,0]-np.min(f[:,0])
	Y_dat = f[:,1]-np.min(f[:,1])
	Z_dat = Ztot/fMax

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


# try to clip zi
	zic = np.clip(zi, a_min = 0, a_max = MAX_CLIP_VAL)

# I control the range of my colorbar by removing data 
# outside of my range of interest
	# zmin = 0
	# zmax = 1
	# zi[(zi<zmin) | (zi>zmax)] = None
	# #figR = plt.figure()
	# #rPlot = figR.add_subplot(1,1,1)
	
#plt.zlabel("Intensity (Normalized)")
#plt.show() 
#
#
#
#
# Create the contour plot
	# The 40 volt supply is negative. Settingit to 0, result in +20v across the sensor
	# Setting it to "40", results in -20V across the sensor. 
	actVolts = (float(volts) - 20) * (-1) 
	##plt.contourf(xi, yi, zi, 15, cmap=plt.cm.viridis, robust = True)
	#plt.contourf(xi, yi, zi, 15, cmap=plt.cm.viridis, vmin=0, vmax=MAX_CLIP_VAL, extend='neither')
	plt.contourf(xi, yi, zic, 15, cmap=plt.cm.viridis )
	cbar = plt.colorbar()
	cbar.set_label('Intensity (Normalized)', rotation=90) 
	plt.title ("Device SN" + dSN + " " + str(actVolts) +" 2D scan")
	plt.xlabel ("Position (mm)")
	plt.ylabel ("Position (mm)")

	rpltName = "#RasterScan_SN" + dSN +"_" + str(actVolts) + ".jpg"
	plt.savefig(str(rpltName))

	plt.show()
	plt.close()
	return fMax



if __name__ == "__main__":
	if len( sys.argv) >= 2:
		snum = sys.argv[1]
		fmax = plot_Raster(snum,0.0) # "Positive" Bias
		plot_Raster(snum,40.0, fmax)# "Negative" Bias
	else:
		print("Usage: plotRaster.py <sernum>")


