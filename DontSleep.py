#Test program to keep computer from going to sleep 

import sys 
import time
import os

cwd = os.getcwd()


def main(argv):
    val = 0
    while val < 1 :
        with open(cwd +"/spongebob.txt", "r", encoding="utf-8") as file:
            for line in file:
                print(line.strip())
        time.sleep(5)
        with open(cwd +"/finger.txt", "r", encoding="utf-8") as file:
            for line in file:
                print(line.strip())
        time.sleep(.75)
        with open(cwd +"/unic.txt", "r", encoding="utf-8") as file:
            for line in file:
                print(line.strip())
        time.sleep(5)
     
      
  
      
#
#
#
if __name__ == "__main__":

  
    argv = sys.argv

#    #
#    #
#    #  #debug
#    ## argv = ['this', 'read', '-loop']
#    #
#    #
#    #
    main(argv[1:])