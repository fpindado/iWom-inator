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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path

CONFIG_FILE = "config_sendemail.ini"
LOG_DATE_FORMAT = "%Y/%m/%d %H:%M:%S" # too many special characters for .ini file


def load_config():
    """Loads all configuration parameters, and assigns them to global
    variables, to be used along the program
    """
    
    global EMAIL_FROM, EMAIL_TO, EMAIL_SUBJECT, EMAIL_SERVER, EMAIL_PORT
    global LOG_FILE, OUTPUT_LOG, SERVER_LOGIN, SERVER_PASSWD
    
    conf = get_config(CONFIG_FILE)
    LOG_FILE = conf['Files']['Log']
    OUTPUT_LOG = conf['Files']['email-attachment']
    EMAIL_FROM = conf['email']['from']
    EMAIL_TO = conf['email']['to']
    EMAIL_SUBJECT = conf['email']['subject']
    EMAIL_SERVER = conf['email']['smtp-server-url']
    EMAIL_PORT = conf['email']['smtp-server-port']
    SERVER_LOGIN = conf['credentials']['server-login']
    SERVER_PASSWD = conf['credentials']['server-password']


def get_config(file):
    """returns the configuration from file"""
    
    config = configparser.ConfigParser()
    config.read(file)
    return config


def log_entry(text):
    """prints text in a log, including a timestamp and formatting"""
    
    msg = f"{dt.datetime.now().strftime(LOG_DATE_FORMAT)}: {text}"
    print(msg)
    log_msg.append(msg+"\n")



######################## MAIN ##################################

log_msg = list()

# get global configuration, specific hours to enter, vacation information and user credentials
log_entry ("Loading sending email configuration file.")
load_config()

log_entry ("Building email message.")
msg = MIMEMultipart()
msg['From'] = EMAIL_FROM
msg['To'] = EMAIL_TO
msg['Subject'] = EMAIL_SUBJECT

# Open file to include in message in read only and text mode
# and attach it as message
log_entry ("Reading LOG to send in email.")
file_to_send = open(OUTPUT_LOG)
read_data = file_to_send.read()
msg.attach(MIMEText(read_data, 'plain'))
file_to_send.close()

try:
    log_entry ("Connecting with email server.")
    server = smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT)
    server.ehlo()
    server.starttls()
    log_entry ("Login into email server.")
    server.login(SERVER_LOGIN, SERVER_PASSWD)
    log_entry ("Sending email.")
    server.send_message(msg)
    del msg
    log_entry ("email sent.")
    server.quit()
except:
    log_entry ("SMPT server connection error.")

# write log messages to file
with open(LOG_FILE, mode='at', encoding='utf-8') as log:
    log.writelines(log_msg)
