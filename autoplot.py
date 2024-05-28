#
#
#created 21MAY2024
#File: autoplot.py - monitor a file for changes (hscan.txt, vscan.txt, raster.txt, zscan.txt, ...)
# and plot the results in real time - while the other process is generating the file.

# Version 1.0 YF 5/21/2024

import time
import pandas as pd
import matplotlib.pyplot as plt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import matplotlib.animation as animation
import numpy as np
from scipy.interpolate import griddata

# Requires: pip install watchdog matplotlib

# Path to the text file
file_path = r"txts\hscan.txt"

#global
handler = None


class FileUpdateHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.data = None
        self.scanType = ""
        self.filename = ""
        
    def on_modified(self, event):
        print(f"File modified event detected. {event}")
        self.scanType = ""
        self.filename = event.src_path
        
        if "hscan.txt" in event.src_path:
            self.scanType = "hscan"
        elif "vscan.txt" in event.src_path:    
            self.scanType = "vscan"
        elif "bscan.txt" in event.src_path:    
            self.scanType = "bscan"
        elif "zscan.txt" in event.src_path:    
            self.scanType = "zscan"
        elif "raster" in event.src_path:    
            self.scanType = "raster"
        else:
            return    
    

        try:
            # Read the file, skipping the first 5 rows (header lines with '%')
            self.data = pd.read_csv(event.src_path, skiprows=5, header=None, delimiter=' ')


        except Exception as e:
            print(f"Error plotting data: {e}")


def update_plot(frame):
    global handler
    skipThePlot = False
    if handler.data is not None:
        plt.clf() # Clear the previous plot
        
        data = handler.data
        title = handler.filename
        xlabel = ""
        ylabel = ""
        
        if handler.scanType in ["hscan","vscan", "raster"]:  
            A = data.iloc[:,2]
            B = data.iloc[:,3]
            C = data.iloc[:,4]
            D = data.iloc[:,5]
        
        # plot based on scanType
        if handler.scanType == "hscan":  
            x = data.iloc[:,0]
           
            tCounts = A + B + C + D 
            y = ((A+D) - (B+C)) / tCounts # As per DataSheet formula! for 'x'
            xlabel = 'X mm'
            ylabel = "Normalized Signal"
            
        if handler.scanType == "vscan":  
            x = data.iloc[:,1]
            
            tCounts = A + B + C + D 
    
            y = ((A+B) - (C+D)) / tCounts # As per DataSheet formula! for 'y'

            xlabel = 'Y (mm)'
            ylabel = "Normalized Signal"
        
        if handler.scanType == "bscan":
            A = data.iloc[:,1]
            B = data.iloc[:,2]
            C = data.iloc[:,3]
            D = data.iloc[:,4]
           
            x = data.iloc[:,0] - 20
            y = A + B + C + D   # note that plotRaster.py only looked at Quad#1
            xlabel = 'V (volts)'
            ylabel = "Abs Signal"
        
        if handler.scanType == "raster":
            Ztot =  A + B + C + D
            fMax = np.max(np.abs( Ztot ))

            x = data.iloc[:,0]
            y = data.iloc[:,1]
            Z_dat = Ztot/fMax

            # Convert from pandas dataframes to numpy arrays
            X, Y, Z, = np.array([]), np.array([]), np.array([])
            for i in range(len(x)):
                X = np.append(X, x[i])
                Y = np.append(Y, y[i])
                Z = np.append(Z, Z_dat[i])

            # create x-y points to be used in heatmap
            xi = np.linspace(X.min(), X.max(), 1000)
            yi = np.linspace(Y.min(), Y.max(), 1000)

            # Interpolate for plotting
            zi = griddata((X, Y), Z, (xi[None,:], yi[:,None]), method='cubic')

	
    
            #
            #
            # Create the contour plot
            # The 40 volt supply is negative. Settingit to 0, result in +20v across the sensor
            # Setting it to "40", results in -20V across the sensor. 
            plt.contourf(xi, yi, zi, 15, cmap=plt.cm.viridis, extend='both' )
            cbar = plt.colorbar()
            cbar.set_label('Intensity (Normalized)', rotation=90) 
            
            xlabel = "X (mm)"
            ylabel = "Y (mm)"
            skipThePlot=True
                
        if skipThePlot:
            pass
        else:
            plt.plot(x, y)
            
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        
        
        
        
#
#  MAIN
#        
if __name__ == "__main__":
    
    # Create an observer
    observer = Observer()

    # Create a file event handler
    handler = FileUpdateHandler()    
    

    # Schedule the observer to watch the directory containing the file
    observer.schedule(handler, path='txts', recursive=False)

    # Start the observer
    observer.start()
    
    # Set up animation
    ani = animation.FuncAnimation(plt.gcf(), update_plot, interval=1000)

    # Show the plot
    plt.show()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
