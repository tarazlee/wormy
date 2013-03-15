import random, pygame, sys
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from pygame.locals import *

# file to parse
filename = "taraz_scanner_training.csv"
stimFileStem = "training_stimTimes_run_"
training = True 
BLOCKLENGTH = 5
RUNLENGTH = 60
SUB = raw_input("Please enter subject number:")
NUMRUNS = int(raw_input("Please enter number of runs:"))
TOTALTRIALS = NUMRUNS * RUNLENGTH
BLOCKS_PER_RUN = RUNLENGTH/BLOCKLENGTH
blockstarts = []
blockOffsets = []
allRunTimes = []
beh_path = "/home/taraz/wormy/" + SUB + "/behavior/"
server = raw_input("running on server?  enter y or n:")
if server == "n":
    data = pd.read_csv(filename, sep = "\t")
elif server == "y":
    data = pd.read_csv(beh_path+filename, sep = "\t")

def main():
    if training:
        for trial in range(0,TOTALTRIALS):
            if trial % 5 == 0:
                blockstarts.append(data.readyOnsets[trial])
            if trial % 5 == 4:
                blockOffsets.append(data.moveOffets[trial]) # check to see if it's moveOffsets or moveOff"E"ts 
        
        for runNum in range(0, NUMRUNS):
            print runNum
            runTimes = []
            for block in range(BLOCKS_PER_RUN):
                start = blockstarts[block+runNum]
                end = blockOffsets[block+runNum]
                duration = (end - start)/1000
                runTimes.append(str(start/1000)+':'+str(duration))
            allRunTimes.append(runTimes)
    makeStimFiles('taraz', allRunTimes)
    
    
    
    
def makeStimFiles(subjectNum, times):
    for i in range(0,len(times)):
        f = open(str(subjectNum) + '_' +stimFileStem + str(i+1) + '.txt', 'w')
        for j in range(0,len(times)):
            if i != j: 
                f.write('*\n')
            else:
                for time in times[j]:
                    f.write(time+' ')
                f.write('\n')
        f.close()
        
    #1/0
        
if __name__ == '__main__':
    main()