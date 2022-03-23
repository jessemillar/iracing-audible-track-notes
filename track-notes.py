#!python3

#pip install pyirsdk
#pip install pyttsx3
#pip install pypiwin32

import irsdk
import time
import pyttsx3
import json
from pathlib import Path
import os
from os.path import exists

# TODO Handle notes at close to 100% more reliably
# TODO Don't read notes in pit lane

# this is our State class, with some helpful variables
class State:
    ir_connected = False
    lastAnnouncedPercent = -1 # Set to something lower than 0 as the "null" value
    laps = 0
    notes = []

# here we check if we are connected to iracing
# so we can retrieve some data
def check_iracing():
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        # don't forget to reset your State variables
        state.lastAnnouncedPercent = -1
        state.laps = 0
        # we are shutting down ir library (clearing all internal variables)
        ir.shutdown()
        print('irsdk disconnected', flush=True)
    elif not state.ir_connected and ir.startup() and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
        print('irsdk connected', flush=True)

# our main loop, where we retrieve data
# and do something useful with it
def loop():
    # on each tick we freeze buffer with live telemetry
    # it is optional, but useful if you use vars like CarIdxXXX
    # this way you will have consistent data from those vars inside one tick
    # because sometimes while you retrieve one CarIdxXXX variable
    # another one in next line of code could change
    # to the next iracing internal tick_count
    # and you will get incosistent data
    ir.freeze_var_buffer_latest()

    try:
        if ir['WeekendInfo']:
            trackName = ir['WeekendInfo']['TrackDisplayName'] + " " + ir['WeekendInfo']['TrackConfigName']
            trackFile = Path('notes/'+trackName+'.json')
            if not exists(trackFile) or os.path.getsize(trackFile) == 0:
                print("File is empty", flush=True)
                f = open(trackFile, 'w') 
                f.write('{\n\t"notes": []\n}')
                f.close()
            f = open(trackFile) 
            jsonFile = json.load(f)
            if jsonFile is not None:
                state.notes = jsonFile
            f.close()
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        print("Check JSON", flush=True)

    if ir['Lap']:
        if ir['Lap'] != state.laps:
            state.laps = ir['Lap'] 
            state.lastAnnouncedPercent = -1
        
    if ir['LapDistPct']:
        percent = int(ir['LapDistPct'] * 100)
        #print(percent, flush=True)

        if percent == 0:
            state.lastAnnouncedPercent = -1

        if state.notes:
            for note in state.notes['notes']:
                if note.get('percent') and note.get('note'):
                    #print(percent, note, flush=True)
                    if state.lastAnnouncedPercent != note['percent'] and state.lastAnnouncedPercent <= note['percent'] and note['percent'] <= percent:
                        state.lastAnnouncedPercent = note['percent']
                        converter.say(note['note'])
                        converter.runAndWait()

        #if state.notes['debug'] == True:
            #if percent % 10 == 0 and percent != state.lastAnnouncedPercent:
                #state.lastAnnouncedPercent = percent
                #converter.say(str(percent) + "percent")
                #converter.runAndWait()

if __name__ == '__main__':
    # initializing ir and state
    ir = irsdk.IRSDK()
    state = State()

    converter = pyttsx3.init()
    voices = converter.getProperty('voices')
    converter.setProperty('voice', voices[1].id)

    try:
        # infinite loop
        while True:
            # check if we are connected to iracing
            check_iracing()
            # if we are, then process data
            if state.ir_connected:
                loop()
            # sleep for 1 second
            # maximum you can use is 1/60
            # cause iracing updates data with 60 fps
            time.sleep(1)
    except KeyboardInterrupt:
        # press ctrl+c to exit
        pass