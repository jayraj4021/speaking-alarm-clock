import RPi.GPIO as GPIO
import time
from datetime import datetime
import schedule
import os
import thread

GPIO.setmode(GPIO.BCM)

#minute bits
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#hour bits
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO for setting alarm time and stopping alarm
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO for snoooooooooooz and reset
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#function to be called as thread to play alarm tone
def alarm_tone():
    while alarm_set == 1 and snooz == 0:
        cmd = "aplay /home/pi/music/Calm.wav 2>\dev\\null"
        os.system(cmd)

#function to check if it is time for alarm
def check_time():
    global hours
    global minutes
    global alarm_set
    global snooz
    curr_time = datetime.time(datetime.now())
    #print curr_time.hour
    #print curr_time.minute
    #print "alarm_time="+str(hours)+" " +str(minutes)
    if alarm_set == 1:
        if (hours-curr_time.hour)==0 and (minutes-curr_time.minute)==0:
            snooz = 0
            thread.start_new_thread(alarm_tone,())
            while True:
                #if stop button is pressed (stop and alarm set button are same)
                if GPIO.input(19)==0:
                    alarm_set = 0
                    run_IDs = os.popen('ps aux | grep \'aplay /home/pi/music/Calm.wav\' | awk \'{print $2}\'').read()
                    IDs = run_IDs.split('\n')
                    IDs.pop()
                    for ID in IDs:
                        cmd = 'kill -9 '+ ID + ' 2>\dev\\null'
                        os.system(cmd)
                    break
                #if snooz button is pressed (snooz and alarm reset button are same)
                if GPIO.input(26)==0:
                    snooz = 1
                    minutes = minutes + 5
                    if minutes == 60:
                        minutes = 0
                        hours = hours + 1
                        if hours==24:
                            hours = 0
                    alarm_set = 1
                    run_IDs = os.popen('ps aux | grep \'aplay /home/pi/music/Calm.wav\' | awk \'{print $2}\'').read()
                    IDs = run_IDs.split('\n')
                    IDs.pop()
                    for ID in IDs:
                        cmd = 'kill -9 '+ ID + ' 2>\dev\\null'
                        os.system(cmd)
                    cmd = "espeak -ven+f5 \"Will ring again after 5 minutes\" 2>\dev\\null"
                    os.system(cmd)
                    break

minutes = 0
hours = 0
snooz = 0
alarm_set = 0
while True:
    while GPIO.input(19)==0: 
        bit_0 = GPIO.input(4)
        bit_1 = GPIO.input(17)
        bit_2 = GPIO.input(27)
        bit_3 = GPIO.input(22)
         
        bit_4 = GPIO.input(21)
        bit_5 = GPIO.input(20)
        bit_6 = GPIO.input(16)
        bit_7 = GPIO.input(12)
        bit_8 = GPIO.input(7)

        #print "Minute bits value="+ str(bit_3) + str(bit_2) + str(bit_1)+ str(bit_0)
        #print "Hour bits value="+ str(bit_8) + str(bit_7) + str(bit_6) + str(bit_5)+ str(bit_4)
        
        #reading minute value
        minutes = 5 * (bit_3*8 + bit_2*4 + bit_1*2 + bit_0*1)
        to_speak_minutes = ""
        if minutes > 55:
            to_speak_minutes = "We have only 60 minutes"
        else:
            to_speak_minutes = str(minutes) + " minutes"

        #reading hour value
        hours = (bit_8*16) + (bit_7*8) + (bit_6*4) + (bit_5*2) + (bit_4*1)
        to_speak_hours = ""
        if hours > 24:
            to_speak_hours = "We have only 24 hrs"
        else:
            to_speak_hours = str(hours) + " hour"

        to_speak = "Alarm set to " + to_speak_hours + to_speak_minutes
        cmd = "espeak -ven+f5 \"" + to_speak + "\" 2>\dev\\null" 
        os.system(cmd)
        alarm_set = 1

    if alarm_set==1:
        #print "alarm set"
        schedule.every().minute.do(check_time)
        while True:
            schedule.run_pending()
            #user wants to reset alarm timing
            if GPIO.input(26)==0 and snooz==0:
                #print "alarm reset"
                cmd = "espeak -ven+f5 \"Alarm Reset\" 2>\dev\\null"
                os.system(cmd)
                alarm_set = 0
                schedule.clear()
                break
            
