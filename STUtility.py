#
#
#
#File: STUtility
# Provides some base classes for other classes
# V 1.0 YF 6/12/2024

import matplotlib.pyplot as plt


class IRunnable:
    def __init__(self) -> None:
        super().__init__()  # Ensure any further base classes are initialized
        self.interrupted = False
        print("Initializing IRunnable")


class IPlottable:
    def __init__(self) -> None:
        super().__init__()  # Ensure any further base classes are initialized
        self.xtrace = []
        self.ytrace = []
        self.zlist = []
        print("Initializing IPlottable")
        self.fig, self.ax = plt.subplots()
        ##self.line, = self.ax.plot([], [])  # Initialize an empty line
        
         
    def ticklePlot(self):
        plt.draw()
        plt.pause(0.001)  # Small pause to allow the plot to update    
              
    def updateLivePlot(self, arr, filename = "", reset = 0 ):
        #print("updateLivePlot:", arr)
            
        A = arr[2]
        B = arr[3]
        C = arr[4]
        D = arr[5]
        title = filename
        xlabel = ""
        ylabel = ""
        handleZSpecial = 0


        ## plt.clf() # try
        self.ax.clear()
            
        # plot based on scanType
        if self.cmd == "-hscan":  
            x = arr[0]
            tCounts = A + B + C + D 
            if tCounts:
                y = ((A+D) - (B+C)) / tCounts # As per DataSheet formula! for 'x'
            xlabel = 'X mm'
            ylabel = "Normalized Signal"

        elif self.cmd == "-vscan":  
            x = arr[1]
            tCounts = A + B + C + D 
            if tCounts:
                y = ((A+B) - (C+D)) / tCounts # As per DataSheet formula! for 'y'
            xlabel = 'Y (mm)'
            ylabel = "Normalized Signal"

        elif self.cmd == "-zscan":  
            x = arr[0]
            z = arr[1]
            if not self.zlist:
                self.zlist.append(z)
            elif self.zlist[-1]  != z:
                self.zlist.append(z)   
                
            tCounts = A + B + C + D 
            if tCounts:
                y = ((A+D) - (B+C)) / tCounts # As per DataSheet formula! for 'x'            xlabel = 'X (mm)'
            ylabel = "(Z-scan) Normalized Signal"
            handleZSpecial = True
            
          

        if reset:
            self.xtrace = []
            self.ytrace = []
            self.zlist = []
            self.ax.clear()  # Clear the previous plot
            return

        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.set_title(title)     
        
        
        self.xtrace.append(x)
        self.ytrace.append(y)    
        
        if handleZSpecial:
            prevX = -9999
            previ = 0
            zi = 0
         
            
             # a dumb brute force way to do it...    
            for i in range(len(self.xtrace)):
                x = self.xtrace[i]
                if x < prevX:
                    
                    self.ax.plot( self.xtrace[previ:i],self.ytrace[previ:i], label = str( self.zlist[zi] ) )
                    
                    previ = i
                    zi += 1
                    
                
                prevX = x
                
                    
        else:  
            self.ax.plot(self.xtrace, self.ytrace)
            ##self.line.set_data(self.xtrace, self.ytrace)
        
        # Adjust the axis limits dynamically
        self.ax.relim()
        self.ax.autoscale_view()
     
        if handleZSpecial:
            plt.legend(loc="upper left")
            
        plt.draw()
        plt.pause(0.001)  # Small pause to allow the plot to update   
        
        # Redraw the canvas
        self.fig.canvas.flush_events() 
        