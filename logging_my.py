import logging
import os
import sys
import datetime
from time import sleep

#   LOGGING

def check_dir_exist(filename):
    if not os.path.exists(os.path.dirname(filename)):
        logging.debug("lock path not exist, trying to recreate it");
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def init_logging_my(_level=logging.DEBUG):
    work_dir=os.path.dirname(os.path.abspath(__file__))
    log_file=work_dir+"/log/application.log"
    check_dir_exist(log_file)

    try:
        if os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):
            print 'Running in foreground.'
            logging.basicConfig(level=_level)
        else:
            raise Exception('background detected') # Don't! If you catch, likely to hide bugs.
    except Exception as e:    
        print 'Running in background.'
        logging.basicConfig(stream=sys.stderr, filename=log_file,level=_level)        
        logging.debug("--------------------------------------   "+str(datetime.datetime.now()))
        if str(e) != "background detected":
            logging.exception("unk exception:")  

    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("requests").setLevel(logging.ERROR)
    logging.getLogger("TeleBot").setLevel(logging.CRITICAL)
