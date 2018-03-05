import logging
import config
import signal 
import os
from threading import Thread
from time import sleep


import telebot
from telebot import types
from telebot import util


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
            #logging.exception("bot exception:")    
            sleep(60)  
            pass
  
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

def get_markup():
    reply_markup = types.InlineKeyboardMarkup(row_width=1)
    reply_markup.add(   
        types.InlineKeyboardButton("Water status",              callback_data="water_status'"),
        types.InlineKeyboardButton("Measure water level", callback_data="measure_water"),
        types.InlineKeyboardButton("Water plants now!",    callback_data="do_watering_now"),        
                    )                      
    return reply_markup

def send_msg_bot_long_check(channel, message, markup=None):
    #because telegram not sending very long messages, we divide it into small parts
    msgs = [message[i:i + 4096] for i in range(0, len(message), 4096)]
    for text in msgs[:-1]:
        bot.send_message(channel, text)             
    bot.send_message(channel, msgs[-1], reply_markup=markup)    
   
def check_water_status_and_send_responce(chat_id):
    if GetWaterLevel() == None:
        send_msg_bot_long_check(chat_id, "Water level not measured yet", get_markup())
    else :
        if GetWaterLevel():
            send_msg_bot_long_check(chat_id, "Water level is low, need water !",get_markup())
        else:
            send_msg_bot_long_check(chat_id, "Water level is ok",get_markup())

# Handles all text messages that contains the commands '/start' or '/help'.    
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    try:    
        bot.send_message(str(config.my_telegram_id), "Choose:", reply_markup=get_markup())      
        #bot.send_message(message.chat.id, "/water_status - status of plant water\n/measure_water - measure water level\n/do_watering_now - do watering now")
    except Exception as e:
        logging.exception("main exception:")      
        pass

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call): 
    try:     
        if call.message:                   
                if call.data == "water_status'":
                    check_water_status_and_send_responce(call.message.chat.id)
                elif call.data == "measure_water":
                    DoWatering(5)
                    check_water_status_and_send_responce(call.message.chat.id)
                elif call.data == "do_watering_now" :
                    DoWatering()    
                    bot.send_message(call.message.chat.id, "Watering done !")
                else:                           
                    send_msg_bot_long_check(str(config.my_telegram_id), "unknown call data: "+call.data, get_markup())               
        elif call.inline_message_id:
            if call.data == "test":
                bot.edit_message_text(inline_message_id=call.inline_message_id, text="forbidden !!!")
    except Exception as e:
        logging.exception("callback_inline:")      
        pass
    finally:
       pass

#@bot.message_handler(commands=['water_status'])
#def handle_water_status(message):    
#    check_water_status_and_send_responce()

#@bot.message_handler(commands=['measure_water'])
#def handle_measure_water(message):    
#    DoWatering(5)
#    check_water_status_and_send_responce()

#@bot.message_handler(commands=['do_watering_now'])
#def handle_do_watering_now(message):    
#    DoWatering()

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, "sorry, I not understan you ?")
    
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
