from pyArduControl import Encoder, ArduControl
from pyCrossfire import FieldAnalyzer
from multiprocessing import Process
import time
import re

def gotoPercent(control, motorA=None, motorB=None):  #, motorB):
    

    #if left0 < left50:
    #    limitA = #currentLeft - currentRight - minDistance

    curL = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[0])
    curR = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[1])
    tickA = percentToTicksCalcA(motorA)
    limitL = leftLimitingPos + (curR - rightLimitingPos) - pad
    limitR = rightLimitingPos + (curL - leftLimitingPos) + pad
#    print "limitL: " + str(limitL) + "   GOTOL: " + str(tickA) + " curL: " + str(curL)
    warning = False

    if tickA > limitL:
#        print "LIMIT WARNING!!!"
        warning = True
        #if left0 < left50:
        #    tickA = limitL
        #    if tickA < left0:
        #        tickA = left0
        #else:
        #    tickA = limitL
        #    if tickA > left0:
        #        tickA = left0
        #print "GOTONEW: " + str(tickA)

    
    tickB = percentToTicksCalcB(motorB)
#    print "limitR: " + str(limitR) + "   GOTOR: " + str(tickB) + " curR: " + str(curR)
    
    if warning:
        tickB += abs(curL - limitL)
        if tickB > right100:
#            print "RIGHT HITTING WALL, CHANGING LEFT"
            tickA = limitL 
            tickB = right100
    
    #if tickB < limitR:
    #    tickB = limitR
        
    stdA = control.encoder.convertPositionTicksToStd(int(tickA))
#    print "gotoA: " + str(stdA)
#    print "actualA: " + str(control.encoder.getPositions()[0])
    stdB = control.encoder.convertPositionTicksToStd(int(tickB))
#    print "gotoB: " + str(stdB)
#    print "actualB: " + str(control.encoder.getPositions()[1])
    control.gotoPosition(stdA, stdB)

def track():
    tracking = Process(target=trackPuck, args=(control, field))
    tracking.start()

def percentToTicksCalcA(motor):
    # conditionals are a safety check depending on which way the encoder is reading...
    if left0 < left50:
        positionTicks = left0 + (lengthLeft * motor)
    else:
        positionTicks = left0 - (lengthLeft * motor)
    return positionTicks

def percentToTicksCalcB(motor):
    if right50 < right100:
        positionTicks = (right100 - lengthRight) + (lengthRight * motor)
    else:
        positionTicks = (right100 - lengthRight) - (lengthRight * motor)
    return positionTicks

def percentToStdCalcA(motor):
    # conditionals are a safety check depending on which way the encoder is reading...
    if left0 < left50:
        positionTicks = left0 + (lengthLeft * motor)
    else:
        positionTicks = left0 - (lengthLeft * motor)
    position = control.encoder.convertPositionTicksToStd(positionTicks)
    return position

def percentToStdCalcB(motor):
    if right50 < right100:
        positionsTicks = right50 + (lengthRight * motor)
    else:
        positionTicks = right50 - (lengthRight * motor)
    position = control.encoder.convertPositionTicksToStd(positionTicks)
    return position    

def trackPuck(control, field):
    percent = field.puckLocationsPercent()
    percent = list(percent)
    percent.sort()
    oldpercent = (not percent[0], not percent[1])
    while True:
        gotoPercent(control, percent[0], percent[1])
        percent = field.puckLocationsPercent()
        percent = list(percent)
        percent.sort()
#        print percent
        time.sleep(.5)

def firing(control, field): 
    print "I sort of work"
    while True:
        puckA = field.puckLocationsPercent()[0]
        puckA = percentToTicksCalcA(puckA)
        puckB = field.puckLocationsPercent()[1]
        puckB = percentToTicksCalcA(puckB)

        carriageA = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[0])
        carriageB = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[1])

        carriageAVel = control.encoder.getVelocities()[0]
        carriageBVel = control.encoder.getVelocities()[1]
        print "I work!" 
        if abs(puckA - carriageA) < puckRadius / 3 or abs(puckB - carriageA) < puckRadius / 3:
            control.triggerAOpen()
            print "UNLOAD A"
        elif abs(puckA - carriageA) < puckRadius or abs(puckB - carriageA) < puckRadius:
            print "FIRE A"
            control.fire(triggerA=1)
        else:
            control.triggerAClose()

        if abs(puckA - carriageB) < puckRadius / 3 or abs(puckB - carriageB) < puckRadius / 3:
            control.triggerBOpen()
            print "UNLOAD B"
        elif abs(puckA - carriageB) < puckRadius or abs(puckB - carriageB) < puckRadius:
            control.fire(triggerB=1)
            print "FIRE A"
        else:
            control.triggerBClose()



pad = 100

controller = raw_input("Enter Controller extension: ")
encoder = raw_input("Enter Encoder extension: ")

control = ArduControl(controller, encoder_board = Encoder(encoder, 464))

while not re.match(r"[yY]", raw_input("Press enter to chck encoder. Y,y to exit")):
    print control.encoder.getPositions()

field = FieldAnalyzer(1)
raw_input("Put left carriage at 0%, then press enter")

left0 = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[0])
print left0
raw_input("Put left carriage at 50% limit then press enter")


left50 = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[0])
print left50
raw_input("Put left carriage close to right carriage")

leftLimitingPos = (control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[0]))
rightLimitingPos = (control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[1]))

raw_input("Put right carriage at 100%, then press enter")

right100 = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[1])
print right100
raw_input("Put right carriage at 50%, then press enter")

right50 = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[1])
print right50
lengthLeft = abs(left0 - left50) * 2

lengthRight = abs(right100 - right50) * 2


field.calibrate()
field.start()

#fire = Process(target=firing, args=(control, field, percentToTicksCalcA, percentToTicksCalcB))
#fire.start()

track()

puckRadius = 85

while True:
    puckA = field.puckLocationsPercent()[0]
    puckAforA = percentToTicksCalcA(puckA)
    puckAforB = percentToTicksCalcB(puckA)
    puckB = field.puckLocationsPercent()[1]
    puckBforA = percentToTicksCalcA(puckB)
    puckBforB = percentToTicksCalcB(puckB)

    carriageA = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[0])
    carriageB = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[1])

    carriageAVel = control.encoder.getVelocities()[0]
    carriageBVel = control.encoder.getVelocities()[1]
    if abs(puckAforA - carriageA) < puckRadius / 3 or abs(puckBforA - carriageA) < puckRadius / 3:
        control.triggerAOpen()
    elif abs(puckAforA - carriageA) < puckRadius or abs(puckBforA - carriageA) < puckRadius:
        control.fire(triggerA=1)
    else:
        print "CLOSE A"
        control.triggerAClose()

    if abs(puckAforB - carriageB) < puckRadius / 3 or abs(puckBforB - carriageB) < puckRadius / 3:
        control.triggerBOpen()
    elif abs(puckAforB - carriageB) < puckRadius or abs(puckBforB - carriageB) < puckRadius:
        control.fire(triggerB=1)
    else:
        print "CLOSE B"
        control.triggerBClose()


