from pyArduControl import Encoder, ArduControl
from pyCrossfire import FieldAnalyzer
from multiprocessing import Process
import time

def gotoPercent(control, motorA=None, motorB=None):  #, motorB):
    

    #if left0 < left50:
    #    limitA = #currentLeft - currentRight - minDistance
    warning = False

    tickA = percentToTicksCalcA(motorA)
    tickB = percentToTicksCalcB(motorB)
    limitL = leftLimitingPos + (curR - rightLimitingPos) - pad
    limitR = rightLimitingPos + (curL - leftLimitingPos) + pad
    print "limitL: " + str(limitL) + "   GOTOL: " + str(tickA) + " curL: " + str(curL) + " limitR: " + str(limitR) \
         + " GOTOR: " + str(tickB) + " curR: " + str(curR)



    if tickA > limitL:
        print "LIMIT WARNING!!!"
        warning = True
        offset = tickA - limitL
       #     if tickA < left0:
       #         tickA = left0
       # else:
       #     tickA = limitL
       #     if tickA > left0:
       #         tickA = left0
       # print "GOTONEW: " + str(tickA)



    if tickB < limitR:
        print "RIGHT BREAKING LIMIT"
        tickB = limitR
        if right50 < right100:
            tickB = limitR

    if warning:
        tickA = limitL  # wait until the other is out of the way...
        tickB += offset
        if tickB < right100:
            tickB = right100
    stdA = control.encoder.convertPositionTicksToStd(tickA)
    stdB = control.encoder.convertPositionTicksToStd(tickB)
    control.gotoPosition(stdA, stdB)
            

def percentToTicksCalcA(motor):
    # conditionals are a safety check depending on which way the encoder is reading...
    if left0 < left50:
        positionTicks = left0 + (lengthLeft * motor)
    else:
        positionTicks = left0 - (lengthLeft * motor)
    return positionTicks

def percentToTicksCalcB(motor):
    if right50 < right100:
        positionTicks = right100 - (lengthRight * motor)
    else:
        positionTicks = right100 + (lengthRight * motor)
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
    while True:
        percents = field.puckLocationsPercent()
        percents = list(percents).sort()
        gotoPercent(control, percents[0])   #, percents[1])

pad = 300

controller = raw_input("Enter Controller extension: ")
encoder = raw_input("Enter Encoder extension: ")

control = ArduControl(controller, encoder_board = Encoder(encoder, 464))

field = FieldAnalyzer(1)
field.calibrate()
raw_input("Put left carriage at 0%, then press enter")

left0 = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[0])
raw_input("Put left carriage at 50% limit then press enter")

left50 = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[0])

raw_input("Put left carriage close to right carriage")

leftLimitingPos = (control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[0]))
rightLimitingPos = (control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[1]))

raw_input("Put right carriage at 100%, then press enter")

right100 = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[1])

raw_input("Put right carriage at 50%, then press enter")

right50 = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[1])

lengthLeft = abs(left0 - left50) * 2

lengthRight = abs(right100 - right50) * 2

field.start()

#gotoPercent(control, .5, touchLimit)

#control.triggerAWorker(.15)
while True:
    curL = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[0])
    curR = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[1])
    percent = field.puckLocationsPercent()
    percent = list(percent)
    percent.sort()
    print percent 
    gotoPercent(control, percent[0], percent[1])
    control.fire(1)
    time.sleep(.1)
