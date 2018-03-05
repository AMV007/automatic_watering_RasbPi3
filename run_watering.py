#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import os
import sys
import argparse
import signal
import sys

import config
import logging

import time as tm
from time import sleep
from datetime import datetime, time as datetime_time, timedelta

from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
from email.mime.text import MIMEText        # Import the email modules we'll need


from check_instance import check_only_one_instance
from logging_my import init_logging_my
from bot import send_water_warning_telegram
from bot import init_bot
from bot import stop_bot


#   GLOBAL
work_dir=os.path.dirname(os.path.abspath(__file__))
os.chdir(work_dir)
watering_info_file=work_dir+"/log/watering.time"
water_low_level=None

#   LOGGING
init_logging_my()

#   CHECK ONLY 1 INSTANCE of APPLICATION RUNNING                    
check_only_one_instance()



#   HANDLE CTRL+C 
def signal_handler(signal, frame):    
    GPIO.output(config.GPIO_RUN_PUMP,GPIO.HIGH) # stop water pump
    logging.error('You pressed Ctrl+C!')
    stop_bot()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

#   SEND WATER WARNING

def send_water_warning_mail():
    msg = MIMEText(config.warning_message,'plain')
    msg['Subject'] = "Water level warning !"
    msg['From'] = config.email_sender
    #msg['To'] = config.email_destination
    conn = SMTP(config.smtp_server)
    conn.set_debuglevel(False)
    conn.login(config.smtp_user, config.smtp_pass)
    try:
        conn.sendmail(config.email_sender, config.email_destination, msg.as_string())
    except:
        logging.error("error send mail !")
    finally:
        conn.quit()
    logging.debug("warning mail out ok")
    return


# FUCTIONS

def get_time(time=None):
    if time is None:
        return datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    else:
        return time.strftime('%d-%m-%Y %H:%M:%S')

class watering_info:
    def read(self):
        try:
            with open(watering_info_file, "r") as text_file:
                str1=text_file.readline().strip('\n')
                str2=text_file.readline().strip('\n')
                self.time=datetime.strptime(str1, '%d-%m-%Y %H:%M:%S')
                self.count=int(str2)
                return
        except (IOError,ValueError) as e:
            print "Error load config, resetting, error="+str(e)
            self.time=datetime.strptime('10-06-1990 12:00:00','%d-%m-%Y %H:%M:%S')
            self.count=0
            return 
    def __init__(self):
        self.read()
        return
    def update(self):
        now=datetime.now()
        # remember time, but change date
        self.time=self.time.replace(year=now.year,month=now.month,day=now.day)
        self.count+=1
        return
    def write(self):
        with open(watering_info_file, "w") as text_file:
            text_file.write(get_time(self.time)+"\n"+str(self.count))
        return

#only possible during watering
def check_water_level(Notify=True):
    global water_low_level
    GPIO.setup(config.GPIO_OUT_LEVEL,GPIO.OUT)
    GPIO.setup(config.GPIO_IN_LEVEL,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    GPIO.output(config.GPIO_OUT_LEVEL,GPIO.HIGH)
    water_low_level=not GPIO.input(config.GPIO_IN_LEVEL)
    if water_low_level and Notify:
        logging.debug("low level of water")
        send_water_warning_mail()
        send_water_warning_telegram()
    GPIO.output(config.GPIO_OUT_LEVEL,GPIO.LOW)
    GPIO.setup(config.GPIO_OUT_LEVEL,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    return not water_low_level

def do_watering(watering_seconds=config.DEF_TIME_WATER_S):
#    print "watering start " + get_time()
    global time_wait
    global last_updated
    
    GPIO.output(config.GPIO_RUN_PUMP,GPIO.LOW)
    time_wait=config.DEF_TIME_WAIT_DAYS
    for i in range (0,watering_seconds):
        sleep(1)
        if i>3 and not check_water_level(False):
            sleep(1)
            if not check_water_level():
                time_wait=1
                break

    GPIO.output(config.GPIO_RUN_PUMP,GPIO.HIGH)
    logging.debug("watering done at: " + get_time())   
    last_updated.update()
    last_updated.write()
    return time_wait

#   INIT

#GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(config.GPIO_RUN_PUMP,GPIO.OUT)
#logging.debug("swith off gpio")
GPIO.output(config.GPIO_RUN_PUMP,GPIO.HIGH) # stop water pump

# arguments
parser = argparse.ArgumentParser()
parser.add_argument("--now", action='store_true')
parser.add_argument("--time")
parser.add_argument("--check_water_level", action='store_true')
args = parser.parse_args()
if args.time:
    config.DEF_TIME_WATER_S=int(args.time)

if args.check_water_level:
    logging.debug("water level: " + ("ok" if check_water_level() else "low"))
    exit()

logging.debug( "Script started " + get_time())
logging.debug( "time for watering="+str(config.DEF_TIME_WATER_S))

last_updated=watering_info()
logging.debug( "readed last_updated time "+get_time(last_updated.time)+", count= "+str(last_updated.count))

def GetWaterLevel():
    return water_low_level

init_bot(GetWaterLevel,do_watering)

#   MAIN
if __name__ == "__main__":
    time_wait=config.DEF_TIME_WAIT_DAYS
    while True:        
        try:
            if (datetime.now() - last_updated.time) > timedelta(time_wait) or args.now:             
                time_wait=do_watering()
            else:
                sleep(300)
        #        logging.debug("time not expired, sleeping " + get_time())
            if args.now:
                break
        except Exception as e:
            GPIO.output(config.GPIO_RUN_PUMP,GPIO.HIGH) # disable pump
            logging.exception("main exception:")      
            pass
    logging.debug( "Script ended " + get_time())
