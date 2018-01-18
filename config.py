# -*- coding: utf-8 -*-

#   HARDWARE CONFIG
GPIO_RUN_PUMP=18          # pin for run water pump
GPIO_OUT_LEVEL=23           # pin for water level check - out 5V
GPIO_IN_LEVEL=24               # pin for water level check - in
DEF_TIME_WATER_S=90     # time for watering process, seconds, minimum 5s - so water level will be checked
DEF_TIME_WAIT_DAYS=3    # delay time between waterings, days

#   MESSAGES
warning_message="Warning, water finished for plants in Paris!"

#   email
smtp_server = 'smtp.server.com'
smtp_user = "maxim"
smtp_pass = "big password"
email_sender = 'watering_bot@gmail.com'
email_destination = ['maxim@gmail.com']

#   telegram
tokenBot = '512345678:AAE_FmMGcxEMTrSRQnFwd3xnjWUJDGhtTSg'
my_telegram_id=123456789
