# Wormy-8dir
# by Taraz Lee
# Original wormy code by Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from pygame.locals import *

# side of screen to start at
LSIDE = 0
BSIDE = 1
RSIDE = 2
TSIDE = 3


FPSSTART = 40 # Starting framerate
SPEEDSTART = 1
SPEEDINCREMENT = 1
SPEEDEND = 2 # Max speed allowed for a HIT
SPEEDMAX = 4 # total maximum speed
CORRECT = 1
INCORRECT = 0

WINDOWWIDTH = 1000
WINDOWHEIGHT = 1000
CELLSIZE = 2
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)
MAXAPPLESIZE = 160
MINAPPLESIZE = 5
STARTAPPLESIZE = 100
APPLEINCREMENT = 10
APPLEDECREMENT = 5
SPEEDINCREMENT = 1
TIMEINCREMENT = 200
TIMEDECREMENT = 100
WAITTIME = 1000
READYTIME = 4000
READYMESSAGE = "+"
REWARDFONTSIZE = 300
TEXTSIZE = 75
MAXTRIALTIME = 3000 # In milliseconds
MINTIME = 2000
REWARDFILE = 'm_seq_rew_5_10_40.npy' # name/location of reward sequence numpy file
JITTERFILE = 'jitters.npy' # name/location of jitter sequence numpy file
READYFILE = 'readytimes.npy' #name/location of ready time sequence numpyfile

JITTERVALUES = [2000, 4000, 6000]
REWARDVALUES = [99, 5, 20]
READYVALUES = [1000, 2000, 3000]
SIDES = [LSIDE,RSIDE] # To randomly choose a starting side

# trial outcomes
TOOSLOW = 0 
TOOFAST = 1
OOB = 2
HIT = 3

fname = 'wormy_wheel_output.txt'

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
UPRIGHT = 'upright'
UPLEFT = 'upleft'
DOWNRIGHT = 'downright'
DOWNLEFT = 'downleft'


HEAD = 0 # syntactic sugar: index of the worm's head
ITERATIONS = 30 # number of total trials (Training + Staircase) -- NOT USED CURRENTLY
TRAINING = 300 # how many training trials to do
NUMSTAIR = 300 # how many staircase trials to do 
NUMREWARD = 243 # how many reward trials to do (243 if m-sequence for 3 reward values)
BLOCKLENGTH = 27
MSEQ = 'yes' # Set to 'no' if you want to randomize order

# make sure there are enough trials that each reward value can be sampled equally
#assert NUMREWARD % len(REWARDVALUES) == 0, "Number of reward trials must be divisible by the number of different reward values"
assert (TRAINING + NUMSTAIR) % len(SIDES) ==0, "Number of training and staircase trials must be divisible by the number of starting sides"

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, FPS, SPEED
    
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
    training = []
    rewards = []
    speedPresses = []
    steerPresses = []
    subjectNums = []
    reversals = []
    reversalSizes = []
    speedReversals = []
    reversalTimes = []
    rewardOnsets = []
    readyOnsets = []
    moveOnsets = []
    moveOffsets = []
    blockStarts = []
    blockNums = []
    trajectories = []
    
    lastStep = lastSpeedStep = 0
    maxTime = MAXTRIALTIME +READYTIME
    #get input from user
    subject_number = raw_input("Please enter your subject number:")
    doStaircase = 'no'
    if doStaircase == 'no': 
        threshold = raw_input("Enter apple size:")
        maxTime = int(raw_input("Enter maximum time:"))
    
    if MSEQ == 'yes':
        rewardSchedule = np.load(REWARDFILE) 
        jitterSchedule = np.load(JITTERFILE)
        readySchedule = np.load(READYFILE)
    else:
        rewardSchedule = makeRandomRewardSchedule(REWARDVALUES)
        jitterSchedule = makeRandomRewardSchedule(JITTERVALUES)
        readySchedule = makeRandomRewardSchedule(READYVALUES)
    
    numTrials = NUMREWARD
    sidesSchedule = makeSideOrder(SIDES, numTrials)
    #FPS = FPStime
    pygame.init()
    
    
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')
    SPEED = SPEEDSTART
    if doStaircase =='yes': size = STARTAPPLESIZE
    else: size = int(threshold)
    
    expStart = waitForTTL(1)
    blockstart = expStart
    
    # Play the game for the number of trials in numTrials
    for i in range(numTrials):
        if i > TRAINING and doStaircase == 'yes': maxTime = np.mean(reversalTimes)
        if maxTime ==0: maxTime = MAXTRIALTIME
        if doStaircase == 'no': reward = rewardSchedule[i] 
        else: reward = 0
        
        if i > 1 and i % BLOCKLENGTH == 0:
            waitForEnter()
            blockstart = waitForTTL(i/BLOCKLENGTH +1)
        
        # inter-trial interval
        waitForITI(jitterSchedule[i])
        
        #play a trial
        trial_outcome, start_locX, start_locY, apple_loc, startSide, \
            trial_time, speedPress, steerPress, rewardOnset, \
            readyOnset, moveOnset, moveOffset, trajectory \
            = runGame(size,i, str(reward),sidesSchedule,maxTime, readySchedule) 
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
        rewardOnsets.append(rewardOnset-blockstart)
        readyOnsets.append(readyOnset-blockstart)
        moveOnsets.append(moveOnset-blockstart)
        moveOffsets.append(moveOffset-blockstart)
        blockStarts.append(blockstart)
        blockNums.append(i/BLOCKLENGTH+1)
        trajectories.append(trajectory)
        
        training.append('no')
        
        # Accuracy
        if trial_outcome == 3: 
            accuracy.append(CORRECT)
            reversals.append(0)
        else: 
            accuracy.append(INCORRECT)
            reversals.append(0)
            
        # make output panda structure
        data = {'startX': worm_locX, 'starty': worm_locY, 'appleX': applesX, 
                'appleY': applesY, 'outcome': outcomes, 'times': trial_times, 
                'apple_size': apple_sizes, 'accuracy': accuracy, 'starting_side': startPos, 
                'training': training, 'reward': rewards, 'throttle': speedPresses, 
                'steering': steerPresses, 'subject': subjectNums, 'reversals': reversals,
                'rewardOnsets': rewardOnsets, 'readyOnsets': readyOnsets, 
                'moveOnsets': moveOnsets, 'moveOffsets': moveOffsets, 'blockStarts': blockStarts,
                'runNum': blockNums
                }
        frame = DataFrame(data)
        # write temporary output in case something crashes . . .
        frame.to_csv('%s_temp_reward_output.csv' % subject_number, sep= '\t')  
        np.save(subject_number + "_temp_reward_trajectories.npy", trajectories)
    # save output panda as CSV and give feedback to user
    if doStaircase == 'yes':
        frame.to_csv('%s_training.csv' % subject_number, sep= '\t') #write output
        print 'staircased apple size is %s' % str(np.mean(reversalSizes))
        print 'last speed deadline was %s' % str(maxTime)
        print 'staircased speed deadline is %s' % str(np.mean(reversalTimes))
    else:
        frame.to_csv('%s_reward.csv' % subject_number, sep= '\t') #write output
        print 'total accuracy: %03f' % np.mean(accuracy)
        #tempFive = frame[frame.reward==40]
        print 'total money earned: $ %i' % frame[frame['accuracy']==1]['reward'].sum()
        randtrial = 1 + random.randint(0, len(trial_times))
        print 'trial number %i was chosen at random' % randtrial
        print 'reward value was $10' #hack so we never pay $40
        #print 'reward value was $%i' % rewards[randtrial]
        if accuracy[randtrial]==1:
            print 'You succeeded on this trial.  Congratulations!'
        else:
            print 'Unfortunately you were not successful on this trial.'
    np.save(subject_number + "_reward_trajectories.npy", trajectories)    
    terminate()

# Run one trial
# returns trial outcome, worm location, apple location, and length of trial in ms
def runGame(targetSize, trialNum, rewardVal,startingSides, maxTime, readySchedule):
    # Set a random start point.
    side = startingSides[trialNum]# choose a random edge of the screen
    readyDuration = readySchedule[trialNum]
    maxTime = maxTime + readyDuration # adjust time limit for trial
    speedPress = 0
    steerPress = 0
    SPEED = 1
    startx, starty = getRandomWormLoc(side)
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    trajectories = []
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
    SPEED = SPEEDSTART
    
    # Start the apple in a random place.
    appleCoords = makeApple(targetSize, side, wormCoords[HEAD])    
    startTime = pygame.time.get_ticks()    
    rewardOnset = startTime
    while True: # main game loop
        curr_time = pygame.time.get_ticks() - startTime
        # pause at the beginning of each trial and
        # display reward value for WAITIME milliseconds
        if curr_time < WAITTIME: 
            
            # draw displays
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawWorm(wormCoords)
            drawApple(appleCoords, targetSize)
            if rewardVal == '99': 
                drawMessage('$ ?', REWARDFONTSIZE)
            drawTrialNumber(trialNum+1)
            if rewardVal != '99': 
                drawMessage('$' + rewardVal, REWARDFONTSIZE)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
            
        # pause between reward presentation and
        # display READYMESSAGE for READYTIME milliseconds
        elif curr_time < WAITTIME + readyDuration:
            readyOnset = rewardOnset + WAITTIME
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawWorm(wormCoords)
            drawApple(appleCoords, targetSize)
            drawMessage(READYMESSAGE, REWARDFONTSIZE)
            drawTrialNumber(trialNum+1)
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
                showGameOverScreen('TOO SLOW!')
                endTime = curr_time
                
                while True: # Make sure trial takes MAXTRIALTIME seconds total
                    curr_time = pygame.time.get_ticks() - startTime
                    if curr_time > MAXTRIALTIME + readyDuration+ WAITTIME: break
                return TOOSLOW, startx, starty, appleCoords, side, moveOffset-moveOnset, \
                    speedPress, steerPress, rewardOnset, readyOnset, \
                    moveOnset, moveOffset, trajectories
                
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
                
                moveOffset = pygame.time.get_ticks()
                showGameOverScreen('OUT OF BOUNDS')
                
                while True: # Make sure trial takes MAXTRIALTIME seconds total
                    curr_time = pygame.time.get_ticks() - startTime
                    if curr_time > MAXTRIALTIME + readyDuration+ WAITTIME: break
                        
                return OOB, startx, starty, appleCoords, side, moveOffset-moveOnset, \
                    speedPress, steerPress, rewardOnset, readyOnset, moveOnset, \
                    moveOffset, trajectories# game over
            
            # check if worm has eaten an apple
            for coord in appleCoords:
                if wormCoords[HEAD]['x'] == coord['x'] and wormCoords[HEAD]['y'] == coord['y']:
                    if SPEED > SPEEDEND:
                        moveOffset = pygame.time.get_ticks()
                        showGameOverScreen('TOO FAST')
                        while True: # Make sure trial takes MAXTRIALTIME seconds total
                            curr_time = pygame.time.get_ticks() - startTime
                            if curr_time > MAXTRIALTIME + readyDuration + WAITTIME: break
                        return TOOFAST, startx, starty, appleCoords, side, \
                            moveOffset-moveOnset, speedPress, steerPress, rewardOnset, \
                            readyOnset, moveOnset, moveOffset, trajectories
                    
                    # send worm back to start
                    moveOffset = pygame.time.get_ticks() 
                    showGameOverScreen('GOOD!!!')                    
                    while True: # Make sure trial takes MAXTRIALTIME seconds total
                            curr_time = pygame.time.get_ticks() - startTime
                            if curr_time > MAXTRIALTIME +  readyDuration + WAITTIME: break
                    return HIT, startx, starty, appleCoords, side, moveOffset-moveOnset, \
                        speedPress, steerPress, rewardOnset, readyOnset, \
                        moveOnset, moveOffset, trajectories
             
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
            trajectories.append(wormCoords[HEAD])
            # draw displays
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawWorm(wormCoords)
            drawApple(appleCoords, targetSize)
            if rewardVal == '0':
                drawSpeed(SPEED)
            drawTrialNumber(trialNum+1)
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
    
def makeApple(targetSize, side, wormLoc):
    apple = getRandomAppleLocation(side, targetSize) #getRandomLocation()
    #check to make sure the worm and the apple aren't straight across from each other
    applecheck = True
    while applecheck:
        if side == LSIDE or side == RSIDE:
            if 0 < (apple['y'] - wormLoc['y'] + targetSize) < targetSize: 
                apple =getRandomAppleLocation(side,targetSize)
            else: applecheck = False
        elif side == TSIDE or side == BSIDE:
            if (abs(wormLoc['x'] - apple['x'])) <= targetSize:
                apple = getRandomAppleLocation(side, targetSize)
            else: applecheck = False
    
    appleCoords = []
    for i in range(targetSize):
        for j in range(targetSize):
            applePixel = {'x': apple['x'] + i, 'y': apple['y'] + j}
            appleCoords.append(applePixel)
    return appleCoords
            
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
                if event.key == K_5:
                    return pygame.time.get_ticks()
                elif event.key == K_ESCAPE:
                    terminate()
                
        #if checkForKeyPress() == K_5:
        #    pygame.event.get() # clear event queue
         #   return pygame.time.get_ticks()

def terminate():
    pygame.quit()
    sys.exit()

def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}

def getRandomAppleLocation(side, size):
    if side == LSIDE:
        return {'x': CELLWIDTH - MAXAPPLESIZE, 'y': random.randint(0, CELLHEIGHT - MAXAPPLESIZE)}
    elif side == BSIDE:
        return {'x': random.randint(0, CELLWIDTH - MAXAPPLESIZE), 'y': MAXAPPLESIZE-size}
    elif side == RSIDE:
        return {'x': MAXAPPLESIZE-size, 'y': random.randint(0, CELLHEIGHT - MAXAPPLESIZE)}
    elif side == TSIDE:
        return {'x': random.randint(0, CELLWIDTH - MAXAPPLESIZE), 'y': CELLHEIGHT - MAXAPPLESIZE}
    
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

def drawMessage(value, fontSize):
    rewardFont = pygame.font.Font('freesansbold.ttf', fontSize)
    rewardSurf = rewardFont.render(value, True, WHITE)
    rewardRect = rewardSurf.get_rect()
    rewardRect.midtop = (WINDOWWIDTH / 2, WINDOWHEIGHT / 3)
    
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
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(appleCoords, targetSize):
    x = appleCoords[0]['x'] * CELLSIZE
    y = appleCoords[0]['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE*targetSize, CELLSIZE*targetSize)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))
        
def makeRandomRewardSchedule(rewardArr):
    schedule = []
    chosenRew = np.zeros(len(rewardArr))
    maxTrials = NUMREWARD / len(rewardArr)
    
    for i in range(NUMREWARD):
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
    maxTrials = float(numTrials) / len(sideArr)
    
    for i in range(numTrials):
        randSide = random.randint(0,len(sideArr)-1)
        while numSides[randSide] >= maxTrials:
            randSide = random.randint(0,len(sideArr)-1)
        order.append(sideArr[randSide])
        numSides[randSide] += 1
    return order
 
def waitForITI(jitter):
    DISPLAYSURF.fill(BGCOLOR)
    drawGrid()
    drawMessage(READYMESSAGE, REWARDFONTSIZE)
    pygame.display.update() 
    pygame.time.wait(int(jitter))

if __name__ == '__main__':
    main()