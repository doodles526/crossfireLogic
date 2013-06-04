from pyArduControl import Encoder, ArduControl
from pyCrossfire import FieldAnalyzer
from multiprocessing import Process
import time

def gotoPercent(control, motorA, limitA):  #, motorB):
    if abs(motorA - limitA) < 100:
        if left0 < left50:
            motorA -= abs(motorA - limitA)
        else:
            motorA += abs(motorA - limitA)
    percentA = percentCalcA(motorA)
    #percentB = percentCalc(motorB)
    control.gotoPosition(percentA)  #, percentB)

def percentCalcA(motor):
    # conditionals are a safety check depending on which way the encoder is reading...
    if left0 < left50:
        positionTicks = left0 + (lengthLeft * motor)
    else:
        positionTicks = left0 - (lengthLeft * motor)
    print positionTicks
    position = control.encoder.convertPositionTicksToStd(positionTicks)
    return position

def percentCalcB(motor):
    pass

def trackPuck(control, field):
    while True:
        percents = field.puckLocationsPercent()
        percents = list(percents).sort()
        gotoPercent(control, percents[0])   #, percents[1])

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

touchLimit = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[0])

#leftToRight = control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[0]) \
#            - control.encoder.convertPositionStdToTicks(control.encoder.getPositions()[1])

#raw_input("Put right carriage at 100%, then press enter")

#right100 = control.encoder.convertPositionsStdToTicks(control.encoder.getPositions()[1])

#raw_input("Put right carriage at 50%, then press enter")

#right50 = control.encoder.convertPositionsStdToTicks(control.encoder.getPositions()[1])

lengthLeft = abs(left0 - left50) * 2

#lengthRight = abs(right100 - right50) * 2

field.start()

gotoPercent(control, .5, touchLimit)

control.triggerAWorker(.15)
#while True:
#    percent = field.puckLocationsPercent()[0]
#    gotoPercent(control, percent)
#    control.fire(1)
#    time.sleep(.1)
