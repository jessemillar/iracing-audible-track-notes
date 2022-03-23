#!python3

#pip install pyirsdk
#pip install pyttsx3
#pip install pypiwin32

import irsdk
import pyttsx3
import json

converter = pyttsx3.init()
voices = converter.getProperty('voices')
converter.setProperty('voice', voices[1].id)

ir = irsdk.IRSDK()
ir.startup()

lastAnnouncedPercent = 200 # Set to something higher than 100 as the "null" value

if ir['WeekendInfo']:
    # TODO Live reload file
    trackName = ir['WeekendInfo']['TrackDisplayName'] + " " + ir['WeekendInfo']['TrackConfigName']
    f = open(trackName+'.json')
    allNotes = json.load(f)
    f.close()

    while True:
        if ir['LapDistPct']:
            percent = int(round(ir['LapDistPct'], 2) * 100)
            #print(percent)

            for note in allNotes['notes']:
                if note['percent'] == percent:
                    converter.say(note['note'])
                    converter.runAndWait()

            if allNotes['debug'] == True:
                if percent % 10 == 0 and percent != lastAnnouncedPercent:
                    lastAnnouncedPercent = percent
                    converter.say(str(percent) + "percent")
                    converter.runAndWait()
