# Wormy-8dir
# by Taraz Lee
# Original wormy code by Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys, os
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from pygame.locals import *
import pygame.midi

# side of screen to start at
LSIDE = 0
BSIDE = 1
RSIDE = 2
TSIDE = 3

# Game parameters
FPSSTART = 40 # Starting framerate
SPEEDSTART = 1
SPEEDINCREMENT = 1
SPEEDEND = 2 # Max speed allowed for a HIT
SPEEDMAX = 4 # total maximum speed
CORRECT = 1
INCORRECT = 0

# SCREEN PARAMETERS
WINDOWWIDTH = 1000
WINDOWHEIGHT = 1000
CELLSIZE = 2
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

# SIZES
MAXAPPLESIZE = 160
MINAPPLESIZE = 5
STARTAPPLESIZE = 100
APPLEINCREMENT = 10
APPLEDECREMENT = 5
BARWIDTH = 40
BAR_HEIGHT_ADJ = 4 # multiplier to make height of prediction bar correct
CENTERAPPLELOC = [{'x': CELLWIDTH /8, 'y': CELLHEIGHT /2}]
BARLOC = [{'x': CELLWIDTH /2, 'y': 9*CELLHEIGHT /10}]#[{'x': (WINDOWWIDTH)/2, 'y': WINDOWHEIGHT/2}]

# TIMING
SPEEDINCREMENT = 1
TIMEINCREMENT = 200
TIMEDECREMENT = 100
WAITTIME = 1000
READYTIME = 500
REWARDFONTSIZE = 200
TEXTSIZE = 75
MAXTRIALTIME = 3000 # In milliseconds
MINTIME = 2000
TIMEADJUSTMENT = 35

# FEEDBACK and DISPLAY
READYMESSAGE = "+"
INSTRUMENTS = [55, 26]

# trialtypes
GAIN_TRIAL = 999
LOSS_TRIAL = -999
EASY_TRIAL = 0
HARD_TRIAL = 1
MEDIUM_TRIAL = 2
PRACTICE_TRIAL = 0
FIRST_COLOR_HARD = 0
FIRST_COLOR_EASY = 1
SECOND_COLOR_HARD = 2
SECOND_COLOR_EASY = 3

# stim files
REWARDFILE = 'm_seq_rewX5.npy' # name/location of reward sequence numpy file
JITTERFILE = 'jitters.npy' # name/location of jitter sequence numpy file
READYFILE = 'readytimes.npy' #name/location of ready time sequence numpyfile

INIT_EARNINGS = 5
JITTERVALUES = [2000, 4000, 6000]
REWARDVALUES = [99, 5, 20]
READYVALUES = [1000, 1000, 1000]
GAINLOSSVALUES = ["5-H","5-E","20-H", "20-E"]
SIDES = [BSIDE, LSIDE,RSIDE] # To randomly choose a starting side

# trial outcomes
TOOSLOW = 0 
TOOFAST = 1
OOB = 2
HIT = 3

# COLORS
#             R    G    B
WHITE     = [255, 255, 255]
BLACK     = [  0,   0,   0]
RED       = [255,   0,   0]
GREEN     = [  0, 255,   0]
DARKGREEN = [  0, 155,   0]
DARKGRAY  = [ 40,  40,  40]
GRAY      = [ 80,  80,  80]
LIGHTGRAY = [100, 100, 100]
GOLD      = [255, 215,   0]
BGCOLOR = BLACK
EASY_COLOR = DARKGREEN
HARD_COLOR = RED
CORRECT_COLOR_FEEDBACK = GOLD
INCORRECT_COLOR_FEEDBACK = WHITE
BARCOLOR = WHITE

# DISTANCES (between apple and worm)
CLOSE = 3
MEDIUM = 2
FAR = 1

# DIRECTIONS
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
UPRIGHT = 'upright'
UPLEFT = 'upleft'
DOWNRIGHT = 'downright'
DOWNLEFT = 'downleft'

NORMAL_TRIAL = 0
HEAD = 0 # syntactic sugar: index of the worm's head
ITERATIONS = 30 # number of total trials (Training + Staircase) -- NOT USED CURRENTLY
TRAINING = 300 # how many training trials to do
NUMSTAIR = 300 # how many staircase trials to do 
NUMREWARD = 420 # how many reward trials to do (243 if m-sequence for 3 reward values)
BLOCKLENGTH = 10 # number of practice trials per block
ACTUALBLOCKLENGTH = BLOCKLENGTH + 2 #practice trials plus gain/loss trials
MSEQ = 'no' # Set to 'no' if you want to randomize order

# make sure there are enough trials that each reward value can be sampled equally
#assert NUMREWARD % len(REWARDVALUES) == 0, "Number of reward trials must be divisible by the number of different reward values"
assert (TRAINING + NUMSTAIR) % len(SIDES) ==0, "Number of training and staircase trials must be divisible by the number of starting sides"
assert NUMREWARD % len(GAINLOSSVALUES) == 0
assert NUMREWARD % len(SIDES) == 0

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, FPS, SPEED, PORT
    
    #initialize output data structures
    outcomes = []
    trial_times = []
    worm_locX = []
    worm_locY = []
    applesX = []
    applesY = []
    apple_sizes = []
    accuracy = []
    startPos = []
    rewards = []
    speedPresses = []
    steerPresses = []
    subjectNums = []
    blockStarts = []
    blockNums = []
    trialDifficulties = []
    types = []
    confidences =[]
    trajectories = []
    deadlines = []
    perceived= []
    endX = []
    endY = []
    total_reward = INIT_EARNINGS
    
    
    maxTime = MAXTRIALTIME +READYTIME
    #get input from user
    subject_number = raw_input("Please enter your subject number:")
    trial_order_file = '%s_mseq_trial_order.csv' % subject_number
    TRIAL_FRAME = pd.read_table(trial_order_file)
    doStaircase = 'no'
    if doStaircase == 'no': 
        threshold = int(raw_input("Enter apple size:"))
        maxTime = int(raw_input("Enter maximum time:"))
        #difficultTime = maxTime - 50
        #easyTime = maxTime + 100
        
    
    if MSEQ == 'yes':
        rewardSchedule = np.load(REWARDFILE) 
        jitterSchedule = np.load(JITTERFILE)
        readySchedule = np.load(READYFILE)
    else:
        rewardSchedule = TRIAL_FRAME.rewardSchedule
        ColorSchedule = TRIAL_FRAME.colorSchedule
        DifficultySchedule = TRIAL_FRAME.difficultySchedule
        trialTypes = TRIAL_FRAME.gainLossSchedule
        timeSchedule = TRIAL_FRAME.timeSchedule
        distanceSchedule = TRIAL_FRAME.distanceSchedule
        perceivedDiff = TRIAL_FRAME.perceivedDiff
        wormXstarts = []
        wormYstarts = []
        appleXstarts = []
        appleYstarts = []
    
    numTrials = len(TRIAL_FRAME)
    sidesSchedule = makeSideOrder(SIDES, numTrials)
    #FPS = FPStime
    pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
    pygame.init()
    
    
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')
    SPEED = SPEEDSTART
    size = int(threshold)
    #CENTERAPPLELOC[0]['x'] = CENTERAPPLELOC[0]['x'] - (size /2 )
        
    
    #expStart = waitForTTL(1)
    
    # Play the game for the number of trials in numTrials
    for i in range(numTrials):
        
        
        if i > TRAINING and doStaircase == 'yes': maxTime = np.mean(reversalTimes)
        if maxTime ==0: maxTime = MAXTRIALTIME
        if doStaircase == 'no': reward = float(rewardSchedule[i])
        else: reward = 0
        
        # set difficulties
        if DifficultySchedule[i] == EASY_TRIAL:
            trial_difficulty = 'EASY'
        elif DifficultySchedule[i] == HARD_TRIAL:
            trial_difficulty = 'HARD'
        elif DifficultySchedule[i] == MEDIUM_TRIAL:
            trial_difficulty = 'MEDIUM'
        apple_color = ColorSchedule[i]
        trial_max_time = maxTime + timeSchedule[i]
        # fix apple color to be integers
        apple_color = apple_color[1:-1].split(',')
        apple_color = map(int, apple_color)
        
        if trialTypes[i] == LOSS_TRIAL: # make loss trials negative
                reward = reward*-1       
        #for gain and loss trials
        if i % ACTUALBLOCKLENGTH == BLOCKLENGTH:
            confidence = prepareGainTrial(size, apple_color, reward)
        elif trialTypes[i] == LOSS_TRIAL:
            # set loss trial confidence to be the same as previous gain trial
            confidence = confidences[-1] 
            
            drawMessage('LOSE:', TEXTSIZE)
            drawMessage('$%0.2f' % reward, REWARDFONTSIZE, TEXTSIZE + 5)
            pygame.display.update()
            pygame.time.wait(1000)
        else:
            confidence = float('NaN')
            
        # ---------------------------------------        
        # END gain/loss section
        if (i % (ACTUALBLOCKLENGTH *10) ==0):
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawMessage('TOTAL EARNED: $ %s' % total_reward, TEXTSIZE)
            drawTrialNumber(i)
            pygame.display.update()
            pygame.time.wait(1500)
            waitForTTL(i/ACTUALBLOCKLENGTH+1)
        if (i % ACTUALBLOCKLENGTH == 0):
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawMessage("EXPOSURE", TEXTSIZE)
			#drawMessage("TRIALS", TEXTSIZE)
            pygame.display.update()
            pygame.time.wait(1500)
            
            # play loss trial

        #play a trial
        trial_outcome, start_locX, start_locY, apple_loc, startSide, \
            trial_time, speedPress, steerPress, trajectory, end_locX, end_locY \
            = runGame(distanceSchedule[i],size,i, str(reward),sidesSchedule,trial_max_time, trialTypes[i],apple_color) 
                # fill in output data
        outcomes.append(trial_outcome)
        worm_locX.append(start_locX)
        worm_locY.append(start_locY)
        applesX.append(apple_loc[0]['x'])
        applesY.append(apple_loc[0]['y'])
        trial_times.append(trial_time)
        apple_sizes.append(size)
        startPos.append(startSide)
        rewards.append(reward)
        speedPresses.append(speedPress)
        steerPresses.append(steerPress)
        subjectNums.append(subject_number)
        blockNums.append(i/ACTUALBLOCKLENGTH+1)
        types.append(trialTypes[i])
        confidences.append(confidence)
        trajectories.append(trajectory)
        deadlines.append(trial_max_time)
        perceived.append(perceivedDiff[i])
        endX.append(end_locX)
        endY.append(end_locY)
        
        # Accuracy
        if trial_outcome == HIT: 
            accuracy.append(CORRECT)
        else: 
            accuracy.append(INCORRECT)
            
        # make output panda structure
        data = {'startX': worm_locX, 'starty': worm_locY, 'appleX': applesX, 
                'appleY': applesY, 'outcome': outcomes, 'times': trial_times, 
                'apple_size': apple_sizes, 'accuracy': accuracy, 'starting_side': startPos, 
                'reward': rewards, 'throttle': speedPresses, 
                'steering': steerPresses, 'subject': subjectNums, 
                'runNum': blockNums, 'trial_type': types, 'perf_prediction': confidences,
                'deadlines': deadlines, 'perceived_difficulty': perceived, \
                'endX': endX, 'endY': endY
                }
        frame = DataFrame(data)
        # write temporary output in case something crashes . . .
        frame.to_csv('%s_temp_shiva_output.csv' % subject_number, sep= '\t')
        np.save(subject_number + "_temp_reward_trajectories.npy", trajectories)
        if trialTypes[i] == GAIN_TRIAL and trial_outcome == HIT:
            total_reward += reward
        elif trialTypes[i] == LOSS_TRIAL and trial_outcome != HIT:
            total_reward += reward # reward is negative in this case
        if total_reward < 0: total_reward = 0
        
    # save output panda as CSV and give feedback to user
    if doStaircase == 'yes':
        frame.to_csv('%s_training.csv' % subject_number, sep= '\t') #write output
        print 'staircased apple size is %s' % str(np.mean(reversalSizes))
        print 'last speed deadline was %s' % str(maxTime)
        print 'staircased speed deadline is %s' % str(np.mean(reversalTimes))
    else:
        frame.to_csv('%s__shiva_reward.csv' % subject_number, sep= '\t') #write output
        print 'total accuracy: %03f' % np.mean(accuracy)
        print 'total money earned: $ %i' % total_reward
        #~ randtrial = 1 + random.randint(0, len(trial_times))
        #~ print 'trial number %i was chosen at random' % randtrial
        #~ print 'reward value was $%i' % rewards[randtrial]
        #~ if accuracy[randtrial]==1:
            #~ print 'You succeeded on this trial.  Congratulations!'
        #~ else:
            #~ print 'Unfortunately you were not successful on this trial.'
    pygame.midi.quit()
    np.save(subject_number + "_reward_trajectories.npy", trajectories)
    terminate()

# Run one trial
# returns trial outcome, worm location, apple location, and length of trial in ms
def runGame(distance, targetSize, trialNum, rewardVal,startingSides, maxTime, trial_type, appleColor = RED, test = NORMAL_TRIAL):
    # Set a random start point.
    if trialNum == GAIN_TRIAL or trialNum == LOSS_TRIAL:
        side = random.randint(0,2)
    else:
        side = startingSides[trialNum]# choose a random edge of the screen
    readyDuration = READYTIME
    maxTime = maxTime + readyDuration # adjust time limit for trial
    speedPress = 0
    steerPress = 0
    startx, starty = getRandomWormLoc(side)
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    
    # Set initial movement direction
    if side == LSIDE: 
        direction = RIGHT
    elif side == BSIDE: 
        direction = UP
    elif side == RSIDE: 
        direction = LEFT
    elif side == TSIDE: 
        direction = DOWN
    FPS = FPSSTART
    #SPEED = random.randint(1,SPEEDMAX) # make starting speed 1, 2, or 3
    SPEED = 1
    # get a random apple location
    appleCoords = makeSpacedApple(targetSize, side, wormCoords[HEAD], distance)
    startTime = pygame.time.get_ticks()    
    rewardOnset = startTime
    trajectories = []
    
    # initialize sounds
    errorSound = pygame.mixer.Sound(os.path.join('sounds', 'fail.wav'))  #load sound
    correctSound = pygame.mixer.Sound(os.path.join('sounds', 'champ.wav'))  #load sound
    
    while True: # main game loop
        curr_time = pygame.time.get_ticks() - startTime
        # pause at the beginning of each trial and
        # display reward value for WAITIME milliseconds
        if curr_time < WAITTIME: 
            
            # draw displays
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            #drawWorm(wormCoords)
            #drawApple(appleCoords, targetSize, appleColor)
            #drawTrialNumber(trialNum+1)
            
            drawMessage(READYMESSAGE, REWARDFONTSIZE/2)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
            
        # pause between reward presentation and
        # display READYMESSAGE for READYTIME milliseconds
        elif curr_time < WAITTIME + readyDuration:
            readyOnset = rewardOnset + WAITTIME
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawWorm(wormCoords)
            drawApple(appleCoords, targetSize, appleColor)
            #drawMessage(READYMESSAGE, REWARDFONTSIZE/2)
            #drawTrialNumber(trialNum+1)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
            if checkForKeyPress(): # clear event queue
                pygame.event.get()
        # play the game    
        elif curr_time > WAITTIME + readyDuration:
            moveOnset = rewardOnset + WAITTIME + readyDuration
            # check if maximum time has elapsed
            if curr_time > maxTime:
                moveOffset = pygame.time.get_ticks()
                
                errorSound.play()
                flashFeedback(INCORRECT)
                endTime = curr_time
                
                while True: # Make sure trial takes MAXTRIALTIME seconds total
                    curr_time = pygame.time.get_ticks() - startTime
                    if curr_time > MAXTRIALTIME + readyDuration+ WAITTIME: break
                return TOOSLOW, startx, starty, appleCoords, side, moveOffset-moveOnset, \
                    speedPress, steerPress, trajectories, wormCoords[HEAD]['x'], wormCoords[HEAD]['y']
                
            #check for keypress    
            for event in pygame.event.get(): # event handling loop
                if event.type == QUIT:
                    terminate()
                elif event.type == KEYDOWN:
                    keytype, direction, SPEED = checkKeyPress(event.key, direction, SPEED)
                    if keytype == 'throttle': speedPress += 1
                    elif keytype == 'steer': steerPress += 1

            # check if the worm has hit itself or the edge
            if wormCoords[HEAD]['x'] <= -1 or wormCoords[HEAD]['x'] >= CELLWIDTH or wormCoords[HEAD]['y'] <= -1 or wormCoords[HEAD]['y'] >= CELLHEIGHT:
                errorSound.play()
                flashFeedback(INCORRECT)
                moveOffset = pygame.time.get_ticks()
                
                while True: # Make sure trial takes MAXTRIALTIME seconds total
                    curr_time = pygame.time.get_ticks() - startTime
                    if curr_time > MAXTRIALTIME + readyDuration+ WAITTIME: break
                        
                return OOB, startx, starty, appleCoords, side, moveOffset-moveOnset, \
                    speedPress, steerPress, trajectories, wormCoords[HEAD]['x'], \
                    wormCoords[HEAD]['y'] # game over
            
            # check if worm has eaten an apple
            for coord in appleCoords:
                if wormCoords[HEAD]['x'] == coord['x'] and wormCoords[HEAD]['y'] == coord['y']:
                    if SPEED > SPEEDEND:
                            #showGameOverScreen('TOO FAST')
                        errorSound.play()
                        flashFeedback(INCORRECT)
                        moveOffset = pygame.time.get_ticks()
                        while True: # Make sure trial takes MAXTRIALTIME seconds total
                            curr_time = pygame.time.get_ticks() - startTime
                            if curr_time > MAXTRIALTIME + readyDuration + WAITTIME: break
                        return TOOFAST, startx, starty, appleCoords, side, \
                            moveOffset-moveOnset, speedPress, steerPress, trajectories, \
                            wormCoords[HEAD]['x'], wormCoords[HEAD]['y']
                            
                    # CORRECT TRIAL
                    correctSound.play()
                    flashFeedback(INCORRECT)
                    moveOffset = pygame.time.get_ticks()  
                    while True: # Make sure trial takes MAXTRIALTIME seconds total
                            curr_time = pygame.time.get_ticks() - startTime
                            if curr_time > MAXTRIALTIME +  readyDuration + WAITTIME: break
                    return HIT, startx, starty, appleCoords, side, moveOffset-moveOnset, \
                        speedPress, steerPress, trajectories, wormCoords[HEAD]['x'], \
                        wormCoords[HEAD]['y']
             
            del wormCoords[-1] # remove worm's tail segment

            # move the worm by adding a segment in the direction it is moving
            if direction == UP:
                newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - SPEED*3}
            elif direction == DOWN:
                newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + SPEED*3}
            elif direction == LEFT:
                newHead = {'x': wormCoords[HEAD]['x'] - SPEED*3, 'y': wormCoords[HEAD]['y']}
            elif direction == RIGHT:
                newHead = {'x': wormCoords[HEAD]['x'] + SPEED*3, 'y': wormCoords[HEAD]['y']}
            elif direction == UPRIGHT:
                newHead = {'x': wormCoords[HEAD]['x'] + SPEED*2, 'y': wormCoords[HEAD]['y'] - SPEED*2}
            elif direction == UPLEFT:
                newHead = {'x': wormCoords[HEAD]['x'] - SPEED*2, 'y': wormCoords[HEAD]['y'] - SPEED*2}
            elif direction == DOWNRIGHT:
                newHead = {'x': wormCoords[HEAD]['x'] + SPEED*2, 'y': wormCoords[HEAD]['y'] + SPEED*2}
            elif direction == DOWNLEFT:
                newHead = {'x': wormCoords[HEAD]['x'] - SPEED*2, 'y': wormCoords[HEAD]['y'] + SPEED*2}
                    
            wormCoords.insert(0, newHead)
            trajectories.append([wormCoords[HEAD], curr_time-moveOnset])
            # draw displays
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawWorm(wormCoords)
            drawApple(appleCoords, targetSize, appleColor)
            #if rewardVal == '0':
                #drawSpeed(SPEED)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
		
def getRandomWormLoc(side):
    if side == LSIDE:
        startx = 5 #random.randint(5, CELLWIDTH - 6)
        starty = random.randint(MAXAPPLESIZE, CELLHEIGHT - MAXAPPLESIZE)
    elif side == BSIDE:
        startx = random.randint(MAXAPPLESIZE, CELLWIDTH - MAXAPPLESIZE)
        starty = CELLHEIGHT - 5
    elif side == RSIDE:
        startx = CELLWIDTH - 5
        starty = random.randint(MAXAPPLESIZE, CELLHEIGHT - MAXAPPLESIZE)
    elif side == TSIDE:
        startx = random.randint(MAXAPPLESIZE, CELLWIDTH - MAXAPPLESIZE)
        starty = 5
    return startx, starty
    
def checkKeyPress(key, direction, SPEED):
    #keytype = 'error'
    if (key == K_LEFT or key == K_y) and direction == UP: 
        direction = UPLEFT
        keytype = 'steer'
    elif (key == K_LEFT or key == K_y) and direction == DOWN: 
        direction = DOWNRIGHT
        keytype = 'steer'
    elif (key == K_LEFT or key == K_y) and direction == RIGHT: 
        direction = UPRIGHT
        keytype = 'steer'
    elif (key == K_LEFT or key == K_y) and direction == LEFT: 
        direction = DOWNLEFT
        keytype = 'steer'
    elif (key == K_LEFT or key == K_y) and direction == UPLEFT: 
        direction = LEFT
        keytype = 'steer'
    elif (key == K_LEFT or key == K_y) and direction == DOWNLEFT: 
        direction = DOWN
        keytype = 'steer'
    elif (key == K_LEFT or key == K_y) and direction == UPRIGHT: 
        direction = UP
        keytype = 'steer'
    elif (key == K_LEFT or key == K_y) and direction == DOWNRIGHT: 
        direction = RIGHT
        keytype = 'steer'
    elif (key == K_RIGHT or key == K_n) and direction == UP: 
        direction = UPRIGHT
        keytype = 'steer'
    elif (key == K_RIGHT or key == K_n) and direction == DOWN: 
        direction = DOWNLEFT
        keytype = 'steer'
    elif (key == K_RIGHT or key == K_n) and direction == RIGHT: 
        direction = DOWNRIGHT
        keytype = 'steer'
    elif (key == K_RIGHT or key == K_n) and direction == LEFT: 
        direction = UPLEFT
        keytype = 'steer'
    elif (key == K_RIGHT or key == K_n) and direction == UPLEFT: 
        direction = UP
        keytype = 'steer'
    elif (key == K_RIGHT or key == K_n) and direction == DOWNLEFT: 
        direction = LEFT
        keytype = 'steer'
    elif (key == K_RIGHT or key == K_n) and direction == UPRIGHT: 
        direction = RIGHT
        keytype = 'steer'
    elif (key == K_RIGHT or key == K_n) and direction == DOWNRIGHT: 
        direction = DOWN
        keytype = 'steer'
    elif (key == K_t or key == K_x):
        SPEED = SPEED + SPEEDINCREMENT        
        keytype = 'throttle'
        if SPEED > SPEEDMAX:
            SPEED = SPEEDMAX
    elif (key == K_b or key == K_z):
        SPEED = SPEED - SPEEDINCREMENT
        keytype = 'throttle'
        if SPEED < 1:
            SPEED = 1
    elif key == K_ESCAPE:
        terminate()
    else:
        keytype = 'error'
  
        
    return keytype, direction, SPEED
    
def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

def waitForEnter():
    DISPLAYSURF.fill(BGCOLOR)
    drawGrid()
    drawMessage('Press 9 to continue', TEXTSIZE/2)
    pygame.display.update()
    while True:
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_9:
                    return
                elif event.key == K_ESCAPE:
                    terminate()
                    

def waitForTTL(blockNum):
    DISPLAYSURF.fill(BGCOLOR)
    drawGrid()
    drawMessage('Block # %i' % (blockNum), TEXTSIZE)
    pygame.display.update()
    while True:
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_5 or event.key == K_y:
                    return pygame.time.get_ticks()
                elif event.key == K_SPACE:
                    return pygame.time.get_ticks()
                elif event.key == K_ESCAPE:
                    terminate()
                
        #if checkForKeyPress() == K_5:
        #    pygame.event.get() # clear event queue
         #   return pygame.time.get_ticks()

def getUserConfidence(size, apple_color):
    confidenceOne = 0
    confidenceTwo = 50
    clearScreen()
    drawMessage('Test Apple is: ', 2*TEXTSIZE/3, x = WINDOWWIDTH/5, y =CELLHEIGHT *3/4)
    pygame.display.update()
    if apple_color == RED:
        color_txt = 'RED'
    elif apple_color == DARKGREEN or apple_color == GREEN:
        color_txt = 'GREEN'
    else:
        color_txt = "UNKOWN"
    #disp_apple_loc = CENTERAPPLELOC
    #drawApple(disp_apple_loc, size, apple_color)
    drawMessage(color_txt, TEXTSIZE, x = WINDOWWIDTH/5, y = CELLHEIGHT*7/8, fontColor = apple_color)
    pygame.display.update()
    if confidenceOne > 0:
        drawBar(abs(confidenceOne), yOffset = -confidenceOne)
    else:
        drawBar(abs(confidenceOne))
        drawMessage('Relative Difficulty?', TEXTSIZE, TEXTSIZE, WINDOWWIDTH/2, 0)
        drawMessage('Test Apple is: ', 2*TEXTSIZE/3, 0, WINDOWWIDTH/5, CELLHEIGHT*3/4 )
        drawMessage(color_txt, TEXTSIZE, x = WINDOWWIDTH/5, y = CELLHEIGHT*7/8, fontColor = apple_color)

        pygame.display.update()
    #pygame.time.wait(200)
    checkForKeyPress()
    # get first confidence
    Loop = True
    loopStart = pygame.time.get_ticks()
    while Loop:
        currentTime = pygame.time.get_ticks() - loopStart
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_b:
                    if currentTime > 200:
                        return confidenceOne
                    else:
                        confidenceOne = 0
                elif event.key == K_y:
                    confidenceOne += 20
                elif event.key == K_n:
                    confidenceOne -= 20
                elif event.key == K_ESCAPE:
                    terminate()
            if confidenceOne < -40: confidenceOne = -40
            elif confidenceOne > 40: confidenceOne = 40
        clearScreen()
        drawBar(80, GRAY, yOffset = -40) # for total scale
        drawTicks()
        if confidenceOne > 0:
            drawBar(abs(confidenceOne), yOffset = -confidenceOne)
        else:
            drawBar(abs(confidenceOne))
        drawMessage('Relative Difficulty?', TEXTSIZE, TEXTSIZE, WINDOWWIDTH/2, 0)
        drawMessage('Test Apple is: ', 2*TEXTSIZE/3, 0, WINDOWWIDTH/5, CELLHEIGHT*3/4 )
        drawMessage(color_txt, TEXTSIZE, x = WINDOWWIDTH/5, y = CELLHEIGHT*7/8, fontColor = apple_color)

        pygame.display.update()
    

def terminate():
    pygame.quit()
    sys.exit()

def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}

def showGameOverScreen(message):
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render(message, True, WHITE)  
    gameRect = gameSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, WINDOWHEIGHT / 4)

    DISPLAYSURF.blit(gameSurf, gameRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(1000)
    if checkForKeyPress(): # clear out any key presses in the event queue
        pygame.event.get()
    
    #~ while True:
        #~ if checkForKeyPress():
            #~ pygame.event.get() # clear event queue
            #~ return

def drawMessage(value, fontSize, offset = 0, x = WINDOWWIDTH/2, y = WINDOWHEIGHT / 3, fontColor = WHITE):
    rewardFont = pygame.font.Font('freesansbold.ttf', fontSize)
    rewardSurf = rewardFont.render(value, True, fontColor)
    rewardRect = rewardSurf.get_rect()
    rewardRect.midtop = (x, y + offset)
    
    DISPLAYSURF.blit(rewardSurf, rewardRect)

def drawSideMessage(value, fontSize, offset = 0, x = WINDOWWIDTH/2, y = WINDOWHEIGHT / 3, fontColor = WHITE):
    rewardFont = pygame.font.Font('freesansbold.ttf', fontSize)
    rewardSurf = rewardFont.render(value, True, fontColor)
    rewardRect = rewardSurf.get_rect()
    rewardRect.topleft = (x, y + offset)
    
    DISPLAYSURF.blit(rewardSurf, rewardRect)
        
def drawSpeed(score):
    scoreSurf = BASICFONT.render('Speed: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def drawTrialNumber(trialNum):
    trialSurf = BASICFONT.render('Trial # %s' % (trialNum), True, WHITE)
    trialRect = trialSurf.get_rect()
    trialRect.topleft = (20, 10)
    DISPLAYSURF.blit(trialSurf, trialRect)

def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, GOLD, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GOLD, wormInnerSegmentRect)


def drawApple(appleCoords, targetSize, color = RED):
    x = appleCoords[0]['x'] * CELLSIZE
    y = appleCoords[0]['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE*targetSize, CELLSIZE*targetSize)
    pygame.draw.rect(DISPLAYSURF, color, appleRect)

def drawBar(height, color = BARCOLOR, xOffset = 0, yOffset=0, width = 1):
    x = xOffset + BARLOC[0]['x']*CELLSIZE
    y = (BARLOC[0]['y']*CELLSIZE)- (50-yOffset)*CELLSIZE*BAR_HEIGHT_ADJ
    barRect = pygame.Rect(x, y, CELLSIZE*BARWIDTH*width, CELLSIZE*height*BAR_HEIGHT_ADJ)
    totalBarRect = pygame.Rect(x, y, CELLSIZE*BARWIDTH, CELLSIZE*80*BAR_HEIGHT_ADJ)
    pygame.draw.rect(DISPLAYSURF, color, barRect)

def drawTicks():
    drawSideMessage('No Difference', REWARDFONTSIZE/10, 0, (BARLOC[0]['x']*CELLSIZE+\
        (CELLSIZE*BARWIDTH)+BARWIDTH+5), (BARLOC[0]['y']+15*CELLSIZE))
    drawSideMessage('Slightly Harder', REWARDFONTSIZE/10, 0, (BARLOC[0]['x']*CELLSIZE+\
        (CELLSIZE*BARWIDTH)+BARWIDTH+5), (BARLOC[0]['y'])-15*CELLSIZE*BAR_HEIGHT_ADJ)
    drawSideMessage('Much Harder', REWARDFONTSIZE/10, 0, (BARLOC[0]['x']*CELLSIZE+\
        (CELLSIZE*BARWIDTH)+BARWIDTH+5), (BARLOC[0]['y'])-CELLSIZE*35*BAR_HEIGHT_ADJ)
    drawSideMessage('Slightly Easier', REWARDFONTSIZE/10, 0, (BARLOC[0]['x']*CELLSIZE+\
        (CELLSIZE*BARWIDTH)+BARWIDTH+5), (BARLOC[0]['y'])+25*CELLSIZE*BAR_HEIGHT_ADJ)
    drawSideMessage('Much Easier', REWARDFONTSIZE/10, 0, (BARLOC[0]['x']*CELLSIZE+\
        (CELLSIZE*BARWIDTH)+BARWIDTH+5), (BARLOC[0]['y'])+CELLSIZE*45*BAR_HEIGHT_ADJ)
    drawBar(0, LIGHTGRAY, xOffset = -BARWIDTH, yOffset = -20, width = 2)
    drawBar(0, LIGHTGRAY, xOffset = -BARWIDTH, yOffset = 20, width =2)
    drawBar(0, LIGHTGRAY, xOffset = -BARWIDTH, yOffset = 0, width = 2)
    drawBar(0, LIGHTGRAY, xOffset = -BARWIDTH, yOffset = -40, width =2)
    drawBar(0, LIGHTGRAY, xOffset = -BARWIDTH, yOffset = 40, width =2)





def getRandomAppleLocation(side, size):
    if side == LSIDE:
        return {'x': CELLWIDTH - MAXAPPLESIZE, 'y': random.randint(0, CELLHEIGHT - MAXAPPLESIZE)}
    elif side == BSIDE:
        return {'x': random.randint(0, CELLWIDTH - MAXAPPLESIZE), 'y': MAXAPPLESIZE-size}
    elif side == RSIDE:
        return {'x': MAXAPPLESIZE-size, 'y': random.randint(0, CELLHEIGHT - MAXAPPLESIZE)}
    elif side == TSIDE:
        return {'x': random.randint(0, CELLWIDTH - MAXAPPLESIZE), 'y': CELLHEIGHT - MAXAPPLESIZE}
    
    
# make an apple that is distance away from the worm.  Distance can be close, medium, or far
# the turn direction is chosen randomly and switched if there isn't enough distance
def makeSpacedApple(targetSize, side, wormLoc, distance):
    appleLoc = {'x':0, 'y':0}
    turnDir = random.choice([RIGHT,LEFT])
    cellDistance = CELLWIDTH/(2+distance) # make actual coordinate distance
    if side == LSIDE:
        appleLoc['x'] = CELLWIDTH - MAXAPPLESIZE
        if turnDir == RIGHT:
            appleLoc['y'] = wormLoc['y'] + cellDistance
            if appleLoc['y'] + targetSize> CELLWIDTH:
                appleLoc['y'] = wormLoc['y'] - targetSize - cellDistance
        else:
            appleLoc['y'] = wormLoc['y'] - targetSize - cellDistance
            if appleLoc['y'] < 0:
                appleLoc['y'] = wormLoc['y'] + cellDistance
                
    elif side == RSIDE:
        appleLoc['x'] = MAXAPPLESIZE-targetSize
        if turnDir == LEFT:
            appleLoc['y'] = wormLoc['y'] + cellDistance
            if appleLoc['y'] +targetSize> CELLWIDTH:
                appleLoc['y'] = wormLoc['y'] - targetSize - cellDistance
        else:
            appleLoc['y'] = wormLoc['y'] - targetSize - cellDistance
            if appleLoc['y'] < 0:
                appleLoc['y'] = wormLoc['y'] + cellDistance
                
    elif side == BSIDE:
        appleLoc['y'] = MAXAPPLESIZE-targetSize
        if turnDir == RIGHT:
            appleLoc['x'] = wormLoc['x'] + cellDistance
            if appleLoc['x'] + targetSize> CELLWIDTH:
                appleLoc['x'] = wormLoc['x'] - targetSize - cellDistance
        else:
            appleLoc['x'] = wormLoc['x'] - targetSize - cellDistance
            if appleLoc['x'] < 0:
                appleLoc['x'] = wormLoc['x'] + cellDistance
    
    appleCoords = []
    for i in range(targetSize):
        for j in range(targetSize):
            applePixel = {'x': appleLoc['x'] + i, 'y': appleLoc['y'] + j}
            appleCoords.append(applePixel)
    return appleCoords
    
    
def makeApple(targetSize, side, wormLoc = [{0,0}]):
    apple = getRandomAppleLocation(side, targetSize) #getRandomLocation()
    #check to make sure the worm and the apple aren't straight across from each other
    applecheck = True
    while applecheck:
        if side == LSIDE or side == RSIDE:
            if 0 < (apple['y'] - wormLoc['y'] + targetSize) < targetSize: 
                apple =getRandomAppleLocation(side,targetSize)
            else: applecheck = False
        elif side == TSIDE or side == BSIDE:
            if (wormLoc['x'] - apple['x']) <= targetSize:
                apple = getRandomAppleLocation(side, targetSize)
            else: applecheck = False
    
    appleCoords = []
    for i in range(targetSize):
        for j in range(targetSize):
            applePixel = {'x': apple['x'] + i, 'y': apple['y'] + j}
            appleCoords.append(applePixel)
    return appleCoords


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))
        
def makeRandomRewardSchedule(rewardArr, numTrials):
    schedule = []
    chosenRew = np.zeros(len(rewardArr))
    maxTrials = NUMREWARD / len(rewardArr)
    
    for i in range(numTrials):
        randRew = random.randint(0, len(rewardArr)-1)
        while chosenRew[randRew] == maxTrials:
            randRew = random.randint(0, len(rewardArr)-1)
            #1/0
        schedule.append(rewardArr[randRew])
        chosenRew[randRew] = chosenRew[randRew] +1
    return schedule

def makeSideOrder(sideArr, numTrials):
    order = []
    numSides = np.zeros(len(sideArr))
    maxTrials = numTrials / len(sideArr)
    
    for i in range(numTrials):
        randSide = random.randint(0,len(sideArr)-1)
        while numSides[randSide] == maxTrials:
            randSide = random.randint(0,len(sideArr)-1)
        order.append(sideArr[randSide])
        numSides[randSide] += 1
    return order
 
def flashFeedback(outcome):
    if outcome == CORRECT:
        color = CORRECT_COLOR_FEEDBACK
    else:
        color = INCORRECT_COLOR_FEEDBACK
    for i in range(0,2):
        DISPLAYSURF.fill(color)
        drawGrid()
        pygame.display.update()
        pygame.time.wait(5)
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        pygame.display.update()
        pygame.time.wait(5)
    
        
        
def prepareGainTrial(size, apple_color, reward):
    clearScreen()
    drawMessage('PERFORMANCE TRIALS', TEXTSIZE)
    pygame.display.update()
    pygame.time.wait(1500)
    confidence = getUserConfidence(size,apple_color)
    clearScreen()
    drawMessage(READYMESSAGE, REWARDFONTSIZE/2)
    pygame.display.update()
    pygame.time.wait(1500)
    clearScreen()
    drawMessage('WIN:', TEXTSIZE)
    drawMessage('$%0.2f' % reward, REWARDFONTSIZE, TEXTSIZE + 5)
    pygame.display.update()
    pygame.time.wait(1000)
    return confidence

def clearScreen():
    DISPLAYSURF.fill(BGCOLOR)
    drawGrid()
    
    
if __name__ == '__main__':
    main()
