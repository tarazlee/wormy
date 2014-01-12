# create csv file that contains the trial types
# output is tab-delimited panda Dataframe


import random, pygame, sys
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from pygame.locals import *
from copy import copy, deepcopy

NUM_PRAC_TRIALS = 500
BLOCKLENGTH = 10
NUM_BLOCKS = NUM_PRAC_TRIALS / BLOCKLENGTH
NUM_GAINLOSS_TRIALS = NUM_BLOCKS * 2
TOTAL_TRIALS = NUM_PRAC_TRIALS + NUM_GAINLOSS_TRIALS

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
GOLD      = (255, 215,   0)


COLOR_ONE= GREEN
COLOR_TWO = RED
GAIN_TRIAL = 999
LOSS_TRIAL = -999
EASY_TRIAL = 0
HARD_TRIAL = 1
MEDIUM_TRIAL = 2

# side of screen to start at
LSIDE = 0
BSIDE = 1
RSIDE = 2
TSIDE = 3

# DISTANCES (between apple and worm)
CLOSE = 3
MEDIUM = 2
FAR = 1

# BLOCK TYPES
FIRST_COLOR_HARD = 0
FIRST_COLOR_EASY = 1
SECOND_COLOR_HARD = 2
SECOND_COLOR_EASY = 3
PRACTICETRIAL = 0
HARD_TRIAL_HIGH = 0
HARD_TRIAL_LOW = 1
EASY_TRIAL_HIGH = 2
EASY_TRIAL_LOW = 3

HIGH_REW = 2
LOW_REW = 0.25
TIME_RANGE = [100, 200, 300, 400] # in milliseconds to shift easy and hard trials

FIRST_BLOCK_TYPES = [FIRST_COLOR_HARD, FIRST_COLOR_EASY, SECOND_COLOR_HARD, SECOND_COLOR_EASY]
TEST_TYPES = [HARD_TRIAL_HIGH, EASY_TRIAL_HIGH, HARD_TRIAL_LOW, EASY_TRIAL_LOW]
MSEQ = np.load('m_seq_5^3_x6.npy')

def main():
    difficultySchedule = []
    colorSchedule = []
    gainLossSchedule = []
    combined_types = []
    blockOrder = []
    timeSchedule = []
    distanceSchedule = []
    subject_number = raw_input("Please enter subject number:")
    # fill in trial type (practice or gain/loss)
    for block in range(NUM_BLOCKS):
        for i in range(BLOCKLENGTH):
            gainLossSchedule.append(PRACTICETRIAL)
        gainLossSchedule.append(GAIN_TRIAL)
        gainLossSchedule.append(LOSS_TRIAL)
    
    # make array of all block-types
    # each block is of the form [first_block_type, test_type]
    for btind, block_type in enumerate(FIRST_BLOCK_TYPES):
        for ting, test in enumerate(TEST_TYPES):
            blockOrder.append([block_type, test])
    random.shuffle(blockOrder)
    blockSchedule = blockOrder * (NUM_BLOCKS / (len(FIRST_BLOCK_TYPES)*len(TEST_TYPES))) # make entire block schedule by repeating blocks
    #random.shuffle(blockSchedule) # randomize block order completely
    colorSchedule, difficultySchedule = setColorDiffSchedule(blockSchedule)
    rewardSchedule = setRewardSchedule(blockSchedule)
    distanceSchedule = setDistanceSchedule(blockSchedule)
    actDiffSchedule = deepcopy(difficultySchedule)
    
    # make medium difficulty trials
    for dind, difficulty in enumerate(difficultySchedule):
        # make third trial of each mini-block and gain/loss trials of medium difficulty
        if dind % (BLOCKLENGTH + 2) == 2 or dind % (BLOCKLENGTH +2) == 7 or \
            dind % (BLOCKLENGTH +2) == 10 or dind %(BLOCKLENGTH +2) == 11: 
            difficultySchedule[dind] =MEDIUM_TRIAL
    timeSchedule = setTimeSchedule(difficultySchedule)
    data = {'gainLossSchedule':gainLossSchedule, 'difficultySchedule': difficultySchedule, \
            'colorSchedule': colorSchedule, 'rewardSchedule': rewardSchedule, 'timeSchedule': timeSchedule, \
            'distanceSchedule': distanceSchedule, 'perceivedDiff': actDiffSchedule
            }
    frame = DataFrame(data)
    frame.to_csv('%s_wormy_shiva_trial_order.csv' % subject_number, sep= '\t')
    
def setTimeSchedule(difficultySchedule):
    timeSchedule = []
    hardTimes = []
    easyTimes = []
    for dind, difficulty in enumerate(difficultySchedule):
        if hardTimes ==[]: 
            hardTimes = [t*-1 for t in TIME_RANGE]
            random.shuffle(hardTimes)
        if easyTimes ==[]: 
            easyTimes = [x for x in TIME_RANGE]
            random.shuffle(easyTimes)
        if difficulty == MEDIUM_TRIAL:
            timeSchedule.append(0) # no adjustment for medium trials
        elif difficulty == EASY_TRIAL:
            timeSchedule.append(easyTimes.pop()) # add easy time adjustment by popping value off easyTimes
        elif difficulty == HARD_TRIAL:
            timeSchedule.append(hardTimes.pop()) # add hard time adjustment by popping value off easyTimes
    return timeSchedule
    
def setColorDiffSchedule(blockSchedule):
    colorSchedule = []
    difficultySchedule =[]
    for bind,bt in enumerate(blockSchedule):
        # fill in trial colors
        if bt[0] == FIRST_COLOR_HARD:
            colorSchedule.extend([COLOR_ONE]*(BLOCKLENGTH/2))
            colorSchedule.extend([COLOR_TWO]*(BLOCKLENGTH/2))
            difficultySchedule.extend([HARD_TRIAL]*(BLOCKLENGTH/2))
            difficultySchedule.extend([EASY_TRIAL]*(BLOCKLENGTH/2))
            if bt[1] == HARD_TRIAL_HIGH or bt[1] == HARD_TRIAL_LOW:
                colorSchedule.extend([COLOR_ONE]*2) # for gain and loss trials
                difficultySchedule.extend([HARD_TRIAL]*2)
            else: 
                colorSchedule.extend([COLOR_TWO]*2)
                difficultySchedule.extend([EASY_TRIAL]*2)
        elif bt[0] == FIRST_COLOR_EASY:
            colorSchedule.extend([COLOR_ONE]*(BLOCKLENGTH/2))
            colorSchedule.extend([COLOR_TWO]*(BLOCKLENGTH/2))
            difficultySchedule.extend([EASY_TRIAL]*(BLOCKLENGTH/2))
            difficultySchedule.extend([HARD_TRIAL]*(BLOCKLENGTH/2))
            if bt[1] == HARD_TRIAL_HIGH or bt[1] == HARD_TRIAL_LOW:
                colorSchedule.extend([COLOR_TWO]*2) # for gain and loss trials
                difficultySchedule.extend([HARD_TRIAL]*2)
            else: 
                colorSchedule.extend([COLOR_ONE]*2)
                difficultySchedule.extend([EASY_TRIAL]*2)
        elif bt[0] == SECOND_COLOR_HARD:
            colorSchedule.extend([COLOR_TWO]*(BLOCKLENGTH/2))
            colorSchedule.extend([COLOR_ONE]*(BLOCKLENGTH/2))
            difficultySchedule.extend([HARD_TRIAL]*(BLOCKLENGTH/2))
            difficultySchedule.extend([EASY_TRIAL]*(BLOCKLENGTH/2))
            if bt[1] == HARD_TRIAL_HIGH or bt[1] == HARD_TRIAL_LOW:
                colorSchedule.extend([COLOR_TWO]*2) # for gain and loss trials
                difficultySchedule.extend([HARD_TRIAL]*2)
            else: 
                colorSchedule.extend([COLOR_ONE]*2)
                difficultySchedule.extend([EASY_TRIAL]*2)
        elif bt[0] == SECOND_COLOR_EASY:
            colorSchedule.extend([COLOR_TWO]*(BLOCKLENGTH/2))
            colorSchedule.extend([COLOR_ONE]*(BLOCKLENGTH/2))
            difficultySchedule.extend([EASY_TRIAL]*(BLOCKLENGTH/2))
            difficultySchedule.extend([HARD_TRIAL]*(BLOCKLENGTH/2))
            if bt[1] == HARD_TRIAL_HIGH or bt[1] == HARD_TRIAL_LOW:
                colorSchedule.extend([COLOR_ONE]*2) # for gain and loss trials
                difficultySchedule.extend([HARD_TRIAL]*2)
            else: 
                colorSchedule.extend([COLOR_TWO]*2)
                difficultySchedule.extend([EASY_TRIAL]*2)
               
    return colorSchedule, difficultySchedule
   
def setDistanceSchedule(blockSchedule):
    distanceSchedule = []
    for bind,bt in enumerate(blockSchedule):
        
        for i in range(BLOCKLENGTH):
            dist = random.choice([CLOSE, MEDIUM, FAR])
            distanceSchedule.append(dist)
        # for gain and loss trials
        distanceSchedule.extend([MEDIUM]*2)
        
    return distanceSchedule
def setRewardSchedule(blockSchedule):
    rewardSchedule = []
    for bind,bt in enumerate(blockSchedule):
        rewardSchedule.extend([0]*BLOCKLENGTH)
        if bt[1] == HARD_TRIAL_HIGH or bt[1] == EASY_TRIAL_HIGH:
            rewardSchedule.extend([HIGH_REW]*2)
        elif bt[1] == HARD_TRIAL_LOW or bt[1] == EASY_TRIAL_LOW:
            rewardSchedule.extend([LOW_REW]*2)
    return rewardSchedule
            
# sets colors specifically to be in the following order: odd blocks = color 1-color2, even blocks = color2-color1
def setColors(first_color, second_color, numTrials):
    colorSchedule = []
    for i in range(numTrials):
        if (i % (BLOCKLENGTH*2)) < BLOCKLENGTH:
            if (i % BLOCKLENGTH) < (BLOCKLENGTH /2):
                colorSchedule.append(first_color)
            else:
                colorSchedule.append(second_color)
        else:
            if (i % BLOCKLENGTH) < (BLOCKLENGTH /2):
                colorSchedule.append(second_color)
            else:
                colorSchedule.append(first_color)
    return colorSchedule
    
# make schedule so that half of each block is of the chosen type
def makeBlockedSchedule(valuesArr, numTrials):
    schedule = []
    chosenVal = np.zeros(len(valuesArr))
    maxTrials = NUMREWARD / len(valuesArr)
    
    for i in range(numTrials):
        randVal = random.randint(0, len(valuesArr)-1)
def makeRandomSchedule(valuesArr, numTrials):
    schedule = []
    chosenVal = np.zeros(len(valuesArr))
    maxTrials = NUMREWARD / len(valuesArr)
    
    for i in range(numTrials):
        randVal = random.randint(0, len(valuesArr)-1)
        while chosenVal[randVal] == maxTrials:
            randVal = random.randint(0, len(valuesArr)-1)
            #1/0
        schedule.append(valuesArr[randVal])
        chosenVal[randVal] = chosenVal[randVal] +1
    return schedule
    
    
    
if __name__ == '__main__':
    main()