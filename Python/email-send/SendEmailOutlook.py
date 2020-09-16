#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 10:10:35 2020
iWom daily filling automation. It only fills today information, not
multi-day filling.

It allows for multiple user filling, using the login and passwords
saved in a .csv file, and detects whether the day is Friday or not, so
it uses the right amount of hours. It is also able to take into
account vacation and bank holidays, and mark them as vacation.

@author: opujol & fpindado
"""

import datetime as dt
import sys
import configparser

CONFIG_FILE = "config/config.ini"
LOG_DATE_FORMAT = "%Y/%m/%d %H:%M:%S" # too many special characters for .ini file



def load_config():
    """Loads all configuration parameters, and assigns them to global
    variables, to be used along the program
    """
    
    global TIME_FILE, CREDENTIALS_FILE, ABSENCE_FILE, LOG_FILE, ABSENCE, WEB
    
    conf = get_config(CONFIG_FILE)
    LOG_FILE = conf['Files']['Log']
    
    ABSENCE = dict(conf['Absences'])
    

def get_config(file):
    """returns the configuration from file"""
    
    config = configparser.ConfigParser()
    config.read(file)
    return config



def log_entry(text, with_user=True):
    """prints text in a log, including a timestamp and formatting"""
    
    if with_user:
        msg = f"{dt.datetime.now().strftime(LOG_DATE_FORMAT)}: [{user}] {text}"
    else:
        msg = f"{dt.datetime.now().strftime(LOG_DATE_FORMAT)}: {text}"
    print(msg)
    log_msg.append(msg+"\n")




######################## MAIN ##################################

log_msg = list()
today = dt.date.today()

# get global configuration, specific hours to enter, vacation information and user credentials
log_entry ("Loading sending email configuration file.", with_user=False)
load_config()
time_conf = get_config(TIME_FILE)
hours = calculate_hours(time_conf)
absence_conf = get_config(ABSENCE_FILE)
users = get_credentials()


# for each user in users file, enter its hours except or absence code
for user in users:
    username = user
    userpwd = users[user]
    abs_code = user_absence(user, absence_conf)
    if abs_code == '00':
        log_entry('Non-working day, no need to enter hours.')
        continue
    log_entry('Opening browser.')
    session = EnterHours(browser)
    log_entry('Login into iWom.')
    session.login(username, userpwd)
    session.open_app()
    if abs_code:
        log_entry(f'Entering information in iWom: absence {abs_code}.')
        session.entry_absent(abs_code)
    else:
        log_entry(f'Entering information in iWom: {hours["value"]} hours.')
        session.entry_hours()
    log_entry(f'Closing session.')
    session.quit_session()

# write log messages to file
with open(LOG_FILE, mode='at', encoding='utf-8') as log:
    log.writelines(log_msg)

