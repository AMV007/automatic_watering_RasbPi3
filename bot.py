import logging
import config
import telebot
import signal 
import os
from threading import Thread
from time import sleep


#   GLOBAL
work_dir=os.path.dirname(os.path.abspath(__file__))
thread = None
killAll=False

sleep(20)
bot = telebot.TeleBot(config.tokenBot)        

#   TELEGRAM BOT HANDLERS

def threaded_function(arg):   
    while not killAll:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.exception("bot exception:")      
  
GetWaterLevel=None
def init_bot(CallBack_water_level, CallBack_watering):
    global thread
    global GetWaterLevel
    global DoWatering

    GetWaterLevel=CallBack_water_level
    DoWatering=CallBack_watering
    thread = Thread(target = threaded_function, args = (10, ))
    thread.start()       

def stop_bot(): 
    killAll=True
    bot.stop_polling() 
    thread.kill_received = True
    os.kill(os.getpid(), 9) # otherwise bot will not stop

def check_water_status_and_send_responce():
    if GetWaterLevel() == None:
        bot.send_message(str(config.my_telegram_id), "water level not measured yet")
    else :
        if GetWaterLevel():
            bot.send_message(str(config.my_telegram_id), "water level is low, need water !")
        else:
            bot.send_message(str(config.my_telegram_id), "water level is ok")

# Handles all text messages that contains the commands '/start' or '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(str(config.my_telegram_id), "/water_status - status of plant water\n/measure_water - measure water level\n/do_watering_now - do watering now")

@bot.message_handler(commands=['water_status'])
def handle_start_help(message):    
    check_water_status_and_send_responce()

@bot.message_handler(commands=['measure_water'])
def handle_start_help(message):    
    DoWatering(5)
    check_water_status_and_send_responce()

@bot.message_handler(commands=['do_watering_now'])
def handle_start_help(message):    
    DoWatering()

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, message.text)
    
    try:
        user = message.from_user
        if user.id!=config.my_telegram_id :       
            bot.send_message(str(config.my_telegram_id), user.username+"\n"+message.text)
        with open(work_dir+"/log/Messages.txt", "a") as myfile:
            myfile.write("user: " +str(user)+"\nMessage: "+message.text.encode('utf8')+"\n")
    except Exception as e:    
        logging.exception("message")              

def send_water_warning_telegram():    
    bot.send_message(str(config.my_telegram_id), config.warning_message) 
