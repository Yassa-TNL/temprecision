from __future__ import division
import os,random,time,sys, locale, numpy, math, pygame,serial
from psychopy import core, event, sound, gui

# make GUI that allows the experimenter to input the subject #
correctSubj = False
while not correctSubj:
    dialog = gui.Dlg(title="Temporal Precision")
    dialog.addField("Participant Number:")
    dialog.addField("Scanner", False)
    dialog.show()
    if gui.OK:
        if dialog.data[0].isdigit():
            subject = int(dialog.data[0])
            scanner = int(dialog.data[1])
            print(scanner)
            correctSubj = True

# have to import visual after subj # dialog box is made
from psychopy import visual
  
## set up scanner stuff
if scanner == 1:
    sPort = serial.Serial('/dev/tty.KeySerial1',timeout=1)

# set up important variables
TrialDuration = 9
#Create the window object.  Set it to full screen mode.
window = visual.Window(fullscr=True, units='pix', color='Black',allowGUI=True)
#Create a clock object.
clock = core.Clock()
# create mouse object
myMouse = event.Mouse() 
#The directory to search through for images.
directoryStim = '/Users/Yassalab/Desktop/TemporalPrecision/Stim/'

## define function that you'll use later to convert imageName to seconds
## remove ".png" from image name and convert from min.sec format to seconds
def removeJPG(imageName):
    ''' Remove the file extension from the image name so that error can be recorded 
        in seconds and converted to a float to do math on.
    '''
    imageName = imageName.replace(".png", "")
    response = float(imageName)
    # split into integer(i) and decimal(d) parts
    i, d = divmod(response,1)
    # round in case the decimal is repeating
    roundedFloat = ('%.0f' % d)
    return imageName

def RunPerceptualBaselineSelfPaced(duration):
    '''Present two circles of a certain color (specified in leftRect and rightRect).
        One of them is slightly darker than the other. The participant needs to press
        1 or 2 to indicate which is darker. Once a key is pressed, the shade of
        each circle changes based on whether the response was correct or incorrect.
        If the key press is correct, the difference between the two circles becomes
        smaller. If the key press is incorrect, the difference becomes bigger.

        This function uses its own clock, scanClock, to set how long the function
        will run.
        '''
    # set up variables the function needs
    #window = visual.Window(fullscr=True,units='pix',color='White')
    squareSize =  window.size[1]/3
    LeftRect = visual.GratingStim(window,tex=None,mask='gauss',size=squareSize,
                pos= (0 - squareSize,0),color="White")
    RightRect = visual.GratingStim(window,tex =None,mask='gauss',size=squareSize,
                pos= (squareSize,0),color="White")
    # indicate start of PB & indicate time since psychopy.core was loaded
    difference = .3
    trialStart = core.Clock()
    trialStart.reset()
    trial =0
    scanClock = core.Clock()
    logfile.write("PB,%s\n" % clock.getTime())
    while scanClock.getTime() < duration:
        startpoint = float(random.randint(1,10))/10
        havePoints = False
        if random.randint(0,1) == 0 or  startpoint + difference > 1.0:
            if startpoint - difference > 0.1:
                darker = startpoint
                lighter = startpoint - difference
                havePoints = True
        if not havePoints:
            darker= startpoint + difference
            lighter = startpoint
        if random.randint(0,1) == 0:
            LeftRect.setOpacity(darker)
            LeftRect.draw(window)
            RightRect.setOpacity(lighter)
            RightRect.draw(window)
            left = True
        else:
            LeftRect.setOpacity(lighter)
            LeftRect.draw(window)
            RightRect.setOpacity(darker)
            RightRect.draw(window)
            left = False
        window.flip()
        event.clearEvents()
        wait = duration - scanClock.getTime()
        keys = event.waitKeys(wait,timeStamped=True)
        if keys == [] or keys == None:
            keys=[['q',0]]
        if keys[0][0] == 'escape':
            break
        if keys[0][0] == 'f5':
            sys.exit()
        if (keys[0][0] == 'b' and left) or (keys[0][0] ==  't' and not left):
            if difference > .06:
                difference -= .05
            if left:
                print "%d: Left and correct. Difference: %.2f\n" %(trial,difference)
                logfile.write("PB,%d,Left,correct,%.2f,%s\n" %(trial,difference,keys))
            else:
                print "%d: Right and correct. Difference: %.2f\n" %(trial,difference)
                logfile.write("PB,%d,Right,correct,%.2f,%s\n" %(trial,difference,keys))
        else:
            if difference < .5:
                difference += .05
            if left:
                print "%d: Left and fail. Difference: %.2f" %(trial,difference)
                logfile.write("PB,%d,Left,fail,%.2f,%s\n" %(trial,difference, keys)
            else:
                print "%d: Right and fail. Difference: %.2f" %(trial,difference, keys)
                # PB, trial #, left or right, fail or correct, difference, RT
                logfile.write("PB,%d,Right,fail,%.2f,%s\n" %(trial,difference, keys))
        window.flip()
        trial += 1
    wait = duration - scanClock.getTime()
    if wait < .5:
        core.wait(wait)
        print('wait time <.5: %s' % wait)
    else:
        core.wait(.5)
        print('wait time: %s' % wait)
    instruxText = visual.TextStim(window,'+',color='Black',wrapWidth=1080,
                font='Verdana', height=50)
    instruxText.draw(window)
    window.flip()
    core.wait(.5,.5)

def WaitSyncPulse():
    #Wait for sync pulse from the scanner before proceeding
    haveTrigger = False
    event.clearEvents()
    sPort.flushInput()
    while not haveTrigger:
        sread = sPort.read(1)
        if sread != '' and sread != None:
            print "received trigger"
            print sread
            haveTrigger = True
        keys = event.getKeys()
        if 'spacebar' in keys:
            haveTrigger = True

# set up the logfile. make it rename the old logfile if a duplicate name is made
if os.path.isfile("./logs/%d_log.txt" %(subject)):
    os.rename("./logs/%d_log.txt" %(subject),"./logs/%d_log_old%d.txt" 
              %(subject,time.time()))
logfile = open("./logs/%d_log.txt" %(subject),'w')

# doing this makes it so that the randomization that happens throughout the script
# will be the same every time the script is run with the same subject #
random.seed(subject)

# find images to be displayed and put into a list (curbImages)
curbImages = []
for files in os.listdir('.'):
    if files.lower().find(".png")!= -1:
        curbImages.append(files)
print('len CurbImages: %s' % len(curbImages))

logfile.write("""OnsetTime,Participant,TrialNumber,BlockNumber,ImageName,EndTime,
            EndTimeInSeconds,CorrectTimeinSeconds,ErrorSec,AbsError,OffsetTime,
            LastTrialTime  \n""")

# set cursor position to middle (between -849 and 849)
prevPos = 0

## present initial instructions
while True:
    instruc_text = ("In this part of the experiment, you will see still frames from "
                    "the videos you just watched, one at a time. For each image, "
                    "you'll need to place it on a timeline to indicate when you saw "
                    "it during the videos. When you see each image, think about when "
                    "it occurred in the videos, and move the cursor to where you "
                    "want it on the timeline. You can move the cursor using the "
                    "scroll wheel. If you scroll quickly, the cursor will move "
                    "more quickly. "

                    "Sometimes, two gray circles will appear on the screen. Scroll "
                    "up if the right circle is darker, and down if the left circle "
                    "is darker.")
    Instruc1 = visual.TextStim(window, instruc_text, color ='White', wrapWidth=600, 
                                        font='Verdana', pos = [0,100], height=20)

    Instruc1.draw(window)
    window.flip()
    # break out of the loop (go on to the experiment) when a key is pressed
    if event.getKeys():
        break

'''We want 18 perceptual baseline trials throughout the experiment. So we're making
two lists of 36 random #s from 1-4. We'll go through that list, and whenever  the # 
we are on is 1 (which should happen 9 times per run), we'll run the Perceptual 
Baseline function instead of presenting a trial'''
randomNum1 = range(1,5)*int((len(curbImages)/8))
randomNum2 = range(1,5)*int((len(curbImages)/8))
# now randomly shuffle the lists
random.shuffle(randomNum1)
random.shuffle(randomNum2)
# now merge the lists
randomNum = randomNum1 + randomNum2

trialNumber = 0 # keep track of what trial we're on
blockNum = 0 # keep track of what block we're on

random.shuffle(curbImages)
responses=[]

# Put stimuli on the screen
curbImage2 = visual.ImageStim(window)
cursorImage = visual.ImageStim(window)
min = visual.TextStim(window, '0:00', color='White', pos=[-500, 200])
max = visual.TextStim(window, '28:18', color='White', pos=[500, 200])
timeText = visual.TextStim(window,color='White',wrapWidth=1080,font='Verdana', 
                            pos=[0,265], height=50)
ITI = visual.TextStim(window, '+', pos=[0,0], height=50, color='White')

# reset clock before trials start to get accurate onsets
clock.reset()

# the next line makes sure the experiment doesn't keep going once the first block
# is done when in scanner mode
spaceText = visual.TextStim(window,'+',color='White',wrapWidth=1080,font='Verdana')

# start the test
for i in curbImages:
    # display this text before the first trial and the middle trial
    if trialNumber == 0 or trialNumber == (len(curbImages)/2):
        spaceText.draw(window)
        window.flip()
        event.waitKeys(keyList=['space','escape'])
        instruxText = visual.TextStim(window,'Ready to start block %d.' % 
                      (blockNum+1),color='White',wrapWidth=1080,font='Verdana')
        instruxText.draw(window)
        window.flip()

        # tell the experiment what input to wait for before moving on, based on
        # whether it's in scanner mode or not
        if scanner == 1:
            WaitSyncPulse()
        elif scanner == 0:
            event.waitKeys(keyList = ['space', 'escape'])
        blockNum+=1
        clock.reset()

    # run the perceptual baseline function 18 times
    if randomNum[trialNumber] == 1 :
        RunPerceptualBaselineSelfPaced(TrialDuration)
    timer = core.CountdownTimer(TrialDuration)
    t_list =[]
    b_list=[]
    OnsetList=[]
    OnsetG=[] 

    # this line relates to code below to only print the first getTime call 
    # (onset time) in the while loop
    first = True
    # flush events
    event.clearEvents() # get rid of other, unprocessed events
    lastTime = 0 # setting up to get RT at last key press
    while timer.getTime() >0: # while time isn't up (turns negative when time's up)
        for key in event.getKeys():
            if key in ['escape']:
                core.quit() # quit if they press escape
            if key in ['b']:
                # add keypress to list for each keypress. then move cursor 
                # proportionally to length of this list
                b_list.append(key)
                prevPos+=len(b_list)
                lastTime = clock.getTime()
            if key in ['t']:
                t_list.append(key)
                prevPos-=len(t_list)
                lastTime = clock.getTime()
        lastTrialTime = lastTime

        # set upper and lower limits to where cursor can go (which will later be 
        # halved to restrict range of cursor on the screen)
        if prevPos <= -849:
            prevPos = -849
        elif prevPos >=849:
            prevPos = 849

        # make absolute position so pos_absolute becomes a range from 0 to 300 
        # (based on 28:18 min movie)
        pos_absolute = prevPos + 849
        # need to have range of 1698 (# of seconds in 28:18)
        # current range is 0 to 849 (which is 50% of 1698)
        seconds =  pos_absolute

        # define still frame images
        # make a little higher than the absolute middle
        curbImage2.setPos([0,40])
        # use each image (i in curbImages)
        curbImage2.setImage(i)
        ## preserve the aspect ratio of the images 
        imageWidth= window.size[1]/2.2
        if curbImage2.size[0]> curbImage2.size[1]:
            sizeFactor=imageWidth/curbImage2.size[0]
        else:
            sizeFactor = imageWidth/curbImage2.size[1]
        curbImage2.setSize((sizeFactor*curbImage2.size[0],
                            sizeFactor*curbImage2.size[1]))

        # define cursor that moves along timeline
        cursorImage.setImage(directoryStim+'cursor.png')

        '''Info about cursorImage and how the timeline works:
        @prevPos is change in scroll wheel. Negative numbers (scroll down) moves 
        it to the left. Pos numbers (scroll up) moves it to the right. The x value 
        moves it from left to right. We multiply by .5 to make it take up less of the 
        screen (e.g. only goes to 849*.5 on either side) The second value 
        (after comma) is y value (from top to bottom). 
         '''
        cursorImage.setPos([int(prevPos)*.5,int(200)])
        # make the line
        timeline = visual.SimpleImageStim(win=window, image=directoryStim+'line.png', units='pix', pos=[0, 200])

        # print constantly updating time value
        timeText = visual.TextStim(window,'%d:%02d' % (seconds/60, seconds % 60),
                color='White',wrapWidth=1080,font='Verdana', pos=[0,252], height=50)
        
        ## now put everything on the window
        curbImage2.draw(window)
        min.draw(window)
        max.draw(window)
        timeText.draw(window)
        timeline.draw(window)
        cursorImage.draw(window)
        ## flip so it actually appears
        window.flip()

        # only print the Onset time if it's the result of the first clock.getTime()
        # call. after that, stop writing to log file
        OnsetTime = clock.getTime()
        if first:
            logfile.write('%s,' % OnsetTime)
            first = False

    # ITI
    ITI = visual.TextStim(window, '+', pos=[0,0], height=50, color='White')
    ITI.draw(window)
    window.flip()
    core.wait(.5,.5)
    # add 1 to @trialNumber on every trial
    trialNumber += 1
    # display thank you text after the last trial
    if trialNumber == len(curbImages):
        thanksText = visual.TextStim(window,'This part of the experiment is over.', 
                    color='White', wrapWidth=1080,font='Verdana')
        thanksText.draw(window)
        window.flip()
        event.waitKeys(keyList=['space', 'escape'])

    # this var isn't really necessary but makes things a little easier
    minutes = seconds / 60

    # make error variable, which is the image name var without the file extension
    ErrorSec = (seconds - int(removeJPG(i)))
    if not OnsetG:
        OnsetG='NA'

    # write important variables to the log file (see logfile header for more info)
    logfile.write('%s,%d,%d,%s,%d:%02d,%d,%s,%d,%d,%f,%s\n' % (subject,trialNumber,
        blockNum,i,minutes,seconds % 60, seconds, removeJPG(i), ErrorSec, 
        abs(ErrorSec),OnsetTime,lastTrialTime))
    # reset cursor position after each response
    prevPos = 0