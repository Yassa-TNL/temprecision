from psychopy import core, event
import time, os,serial
import os,random,time,sys, locale, numpy, math
from psychopy import gui, core, event, sound

# set how high on the screen you want the stimuli
vertPos = 100

videopath='/Users/Yassalab/Desktop/TemporalPrecision/clips/'
filedir = '/Users/Yassalab/Desktop/TemporalPrecision/logs/'

# Make a GUI where the experimenter can input a subject number and choose whether
# or not to run the scanner version
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

# you need to import visual after setting the GUI up or it will fail
from psychopy import visual
win = visual.Window(fullscr=True,units='pix',color='Black',allowGUI=True, screen=1) 

## set up for the scanner version. 
# first, identify the port.
if scanner == 1:
    sPort = serial.Serial('/dev/tty.KeySerial1',timeout=1)

## this function is run after you draw stimuli on the screen and flip the window
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

clock = core.Clock()

# set up the logfile. if it's a logfile name that already exists, rename the old one
if os.path.isfile(filedir+"%d_movielog.txt" %(subject)):
    os.rename(filedir+"%d_movielog.txt" %(subject),"./logs/%d_movielog_old%d.txt",
    %(subject,time.time()))
logfile = open(filedir+"%d_movielog.txt" %(subject),'w')

# instructions
message = ("You will watch a series of 3 videos, one at a time." 
    "The videos are an episode of a sitcom, and they may be offensive. Please pay " 
    "attention to the videos, since you will be asked questions about them later. " 
    "Please do not press any buttons and just watch the videos.\n\nBefore and after " 
    "each video, we will run a resting state scan. During this time, all you need "
    "to do is look at the crosshairs on the screen and stay very still. We will "
    "check in with you between scans.")
text = visual.TextStim(win, message, pos=(0, vertPos), units = 'pix', wrapWidth = 600, 
    height=30, color='White')
text.draw()
win.flip()
# if the following keys are pressed, the experiment will advance to the "+" screen
event.waitKeys(keyList=['space','escape'])

# pre-task resting state scan
text = visual.TextStim(win, '+', pos=(0, 0), units = 'pix', color='White', height=30)
text.draw()
win.flip()
# if the following keys are pressed, the experiment will advance to the screen that 
# says "Waiting for scanner"
event.waitKeys(keyList=['space','escape'])

vidNum = 1
for eachClip in ['clip1.mpg', 'clip2.mpg', 'clip3.mpg']:
    text = visual.TextStim(win, 'Prepping clip %d.\n\nWaiting for scanner.' 
    % vidNum, pos=(0, 0), units = 'pix', color='White')
    # put the instructions on the window
    text.draw()
    # put everything you've drawn on the screen
    win.flip()

    # tell the experiment what to use to determine whether to advance the 
    # experiment or not. if scanner box is checked, wait for the sync pulse.
    # otherwise, wait for a key press
    if scanner == 1:
        WaitSyncPulse()
    elif scanner == 0:
        event.waitKeys(keyList=['space', 'escape'])
    # reset the clock so you know when the video started    
    clock.reset()

    # Create your movie stim.
    mov = visual.MovieStim2(win, videopath+eachClip,
                           size=640,
                           # pos specifies the /center/ of the movie stim location
                           pos=[0,vertPos],
                           flipVert=False,
                           flipHoriz=False,
                           )
    
    # Start the movie stim by preparing it to play
    shouldflip = mov.play()
    logfile.write("AfterShouldflipLine58,%s, Video %s\n" % (clock.getTime(), vidNum))
    while mov.status != visual.FINISHED:
        # Only flip when a new frame should be displayed. Can significantly reduce
        # CPU usage. This only makes sense if the movie is the only /dynamic/ stim
        # displayed.
        if shouldflip:
            # Movie has already been drawn , so just draw text stim and flip
            win.flip()
        else:
            # Give the OS a break if a flip is not needed
            time.sleep(0.001)
        # Drawn movie stim again. Updating of movie stim frames as necessary
        # is handled internally.
        shouldflip = mov.draw()
    
        # Check for action keys.....
        for key in event.getKeys():
            if key in ['escape', 'q']:
                win.close()
                core.quit()
            elif key in ['p']:
                mov.status = -1
            elif key in ['s',]:
                if mov.status in [visual.PLAYING, visual.PAUSED]:
                    # To stop the movie being played.....
                    mov.stop()
                    # Clear screen of last displayed frame.
                    win.flip()
                    # When movie stops, clear screen of last displayed frame,
                    # and display text stim only....
                    text.draw()
                    win.flip()
                else:
                    # To replay a movie that was stopped.....
                    mov.loadMovie(videopath+eachClip)
                    shouldflip = mov.play()
            # if b is pressed, stop playing current video and skip to text before next video
            #elif key in ['b']:
                #mov.status = -1
            elif key in ['p',]:
                # To pause the movie while it is playing....
                if mov.status == visual.PLAYING:
                    mov.pause()
                elif mov.status == visual.PAUSED:
                    # To /unpause/ the movie if pause has been called....
                    mov.play()
                    text.draw()
                    win.flip()
            elif key == 'period':
                # To skip ahead 1 second in movie.
                ntime = min(mov.getCurrentFrameTime()+1.0, mov.duration)
                mov.seek(ntime)
            elif key == 'comma':
                # To skip back 1 second in movie ....
                ntime = max(mov.getCurrentFrameTime()-1.0,0.0)
                mov.seek(ntime)
            elif key == 'minus':
                # To decrease movie sound a bit ....
                cv = max(mov.getVolume()-5, 0)
                mov.setVolume(cv)
            elif key == 'equal':
                # To increase movie sound a bit ....
                cv = mov.getVolume()
                cv = min(mov.getVolume()+5, 100)
                mov.setVolume(cv)
    win.flip()

    # write information about how long it took to play the video segments to a log
    # file
    logfile.write("AfterIterationTime,%s, Video %s\n" % (clock.getTime(), vidNum))

    # After each segment, display text
    text = visual.TextStim(win, 'Segment %d is finished.' % vidNum, pos=(0, 0), 
           units = 'pix', color='White')
    text.draw()
    win.flip()

    # press the following keys to continue to the next resting state scan
    event.waitKeys(keyList=['space','escape'])
    
    # resting state
    text = visual.TextStim(win, '+', pos=(0, 0), units = 'pix', color='White', 
           height=30)
    text.draw()
    win.flip()
    event.waitKeys(keyList=['space','escape'])
    # add 1 to vidNum for each iteration (aka after each video)
    vidNum +=1