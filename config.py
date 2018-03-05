# -*- coding: utf-8 -*-

#   HARDWARE CONFIG
GPIO_RUN_PUMP=18          # pin for run water pump
GPIO_OUT_LEVEL=23           # pin for water level check - out 5V
GPIO_IN_LEVEL=24               # pin for water level check - in
DEF_TIME_WATER_S=90     # time for watering process, seconds, minimum 5s - to measure water level
DEF_TIME_WAIT_DAYS=3    # delay time between waterings, days

#   MESSAGES
warning_message="Warning, no water !"

#   email
smtp_server = 'smtp.server.com'
smtp_user = "login"
smtp_pass = "pass"
email_sender = 'from@servce.com'
email_destination = ['to@server.com']

#   telegram
tokenBot = 'telegram token'
my_telegram_id=12312332123
