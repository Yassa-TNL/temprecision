from __future__ import division
import os,random,time, sys, numpy, math
from psychopy import visual, core, event, sound, gui

#The directory to search through for images.
directoryStim = '/Users/Yassalab/Desktop/TemporalPrecision/Stim/'

TrialDuration=9

#Create the window object.  Set it to full screen mode.
window = visual.Window(fullscr = True, units='pix', color='Black',allowGUI=True) 
## display instructions
message = ("In this part of the experiment, you will see still frames from the "
            "videos you just watched, one at a time. For each image, you'll need "
            "to place it on a timeline to indicate when you saw it during the videos. "
            "You will see a timeline on the screen that ranges from 0 to 28:18. "
            "That is the length of all 3 videos added together. When you see each "
            "image, think about when it occurred in the videos, and move the cursor "
            "to where you want it on the timeline. You can move the cursor using "
            "the scroll wheel. If you scroll quickly, the cursor will move more "
            "quickly. You'll get a chance to practice using the scroll wheel in a "
            "moment. Make your response as quickly as possible. You only have 9 "
            "seconds to respond to each image before it will move on to the next "
            "trial."

            "Sometimes, two gray circles will appear on the screen. Scroll up if the "
            "right circle is darker, and down if the left circle is darker. Keep "
            "making responses until the circles are gone from the screen."

            "Now, we're going to do some practice trials to show you what the task "
            "will be like. These images will be unrelated to the experiment and is "
            "just for you to practice using the scroll wheel. This practice will "
            "use the same timing as you'll have during the experiment, so you can "
            "get used to only having 9 seconds to respond. ")
Instruc1 = visual.TextStim(window, message, color ='White', wrapWidth=780, font='Verdana', pos = [0,0], height=20)

Instruc1.draw(window)
window.flip()
event.waitKeys(keyList=['space','escape'])

# the prevPos variable determines where the cursor is on the timeline. the value of
# prevPos is based on the movement of the participant's scroll wheel, which in our
# case emits a "t" for a scroll up or a "b" for a scroll down    
prevPos = 0
b_list=[]
t_list=[]
catPictures = []

# gather practice pictures
for files in os.listdir('.'):
    if files.lower().find(".jpg")!= -1:
        catPictures.append(files)

print(catPictures)

# Stimuli
Image2 = visual.ImageStim(window)
cursorImage = visual.ImageStim(window)
# minimum timeline value
min = visual.TextStim(window, '0:00', color='White', pos=[-500, 200])
# maximum timeline value
max = visual.TextStim(window, '28:18', color='White', pos=[500, 200])
timeText = visual.TextStim(window,color='White',wrapWidth=1080,font='Verdana', 
                           pos=[0,252], height=50)
ITI = visual.TextStim(window, '+', pos=[0,0], height=50, color='White')

# loop through pictures
trialNum=0
for eachPic in catPictures:
    #prevPos = 0
    key=[]
    #b_list=[]
    #t_list=[]
    timer = core.CountdownTimer(TrialDuration)
    event.clearEvents() # get rid of other, unprocessed events
    # while time isn't up on the countdown timer...
    while timer.getTime() > 0:
        for key in event.getKeys():
            if key in ['escape']:
                core.quit() # quit if they press escape
            if key in ['b']:
                # add keypress to list for each keypress. then move cursor 
                # proportionally to length of this list
                b_list.append(key)
                prevPos+=len(b_list)
            if key in ['t']:
                t_list.append(key)
                prevPos-=len(t_list)
    
        # set upper and lower limits to where cursor can go (which will later be 
        # halved to restrict range of cursor on the screen)
        if prevPos <= -849:
            prevPos = -849
        elif prevPos >=849:
            prevPos = 849

        # make absolute position so pos_absolute becomes a range from 0 to 300 
        # (based on 28:18 min video)
        pos_absolute = prevPos + 849
        # need to have range of 1698 (# of seconds in 28:18)
        # current range is 0 to 849 (which is 50% of 1698)
        seconds =  pos_absolute
    
        # make image a little higher than the absolute middle
        Image2.setPos([0,70])
        # use each image 
        Image2.setImage(catPictures[trialNum])
        imageWidth= window.size[1]/3.9
        if Image2.size[0]> Image2.size[1]:
            sizeFactor=imageWidth/Image2.size[0]
        else:
            sizeFactor = imageWidth/Image2.size[1]
        Image2.setSize((sizeFactor*Image2.size[0],sizeFactor*Image2.size[1]))
    
        # define cursor that moves along timeline
        cursorImage.setImage(directoryStim+'cursor.png')
        # make cursor move by however big prevPos is
        cursorImage.setPos([int(prevPos)*.5,int(200)])
        # make the line
        timeline = visual.SimpleImageStim(win=window, image=directoryStim+'line.png', 
                                          units='pix', pos=[0, 200])
    
        # shows where the cursor is on the timeline, in minutes and seconds
        timeText.text = '%d:%02d' % (seconds/60, seconds % 60)
    
        ## now put everything on the screen
        Image2.draw(window)
        min.draw(window)
        max.draw(window)
        timeText.draw(window)
        timeline.draw(window)
        cursorImage.draw(window)
        ## flip so it actually appears
        window.flip()
    
    ITI.draw(window)
    window.flip()
    core.wait(.5,.5)
    trialNum+=1