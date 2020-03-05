#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 10:10:35 2020

@author: opujo & fpindado
"""

from selenium.webdriver import Firefox, Chrome, Ie, Edge
from selenium.webdriver.firefox.options import Options as f_Options
from selenium.webdriver.chrome.options import Options as c_Options
from selenium.webdriver.common.keys import Keys
from time import localtime, sleep, strptime
from datetime import datetime
import sys
import configparser

CREDENTIALS = "config/users.csv"
CONFIG = "config/config.ini"
VACATIONS = "config/vacations.ini"
LOG_DATE_FORMAT = "%Y/%m/%d %H:%M:%S"

def calculate_hours(conf): # calculate hours
    ''' calculates the number of hours, and start/end time based on the date 
    and config file. 
    Returns a dictionary with: 
        start time (h and min), 
        end time (h and min), 
        and number of hours
    '''
    today = localtime()
    
    # check if date is within range
    start = conf['Jornada normal'].get('start date')
    start = strptime(start, "%Y-%m-%d")
    end = conf['Jornada normal'].get('end date')
    end = strptime(end, "%Y-%m-%d")    
    if today < start or today > end:
        print('Date is out of range. Please update your config file and run again.')
        input('Press enter to finish')
        exit(0)
    
    start = conf['Jornada reducida'].get('start date')
    start = strptime(start, "%Y-%m-%d")
    end = conf['Jornada reducida'].get('end date')
    end = strptime(end, "%Y-%m-%d")
   
    if (today > start and today < end) or today.tm_wday == 4:
        section = 'Jornada reducida'
    elif today.tm_wday < 4:
        section = 'Jornada normal'
    else:
        section = 'Weekends'
    
    t = dict()
    t['value'] = conf[section].get('hours')
    t['start_h'], t['start_m'] = conf[section].get('start time').split(':')
    t['end_h'], t['end_m'] = conf[section].get('end time').split(':')
    
    # replace '00' by '0' to avoid issues with app
    for key in ['start_h', 'start_m', 'end_h', 'end_m']:
        if t[key] == '00':
            t[key] = '0'

    return t


def get_credentials():
    # get credentials from file
    with open (CREDENTIALS, encoding='utf-8-sig') as f:
        credentials = f.readlines()
    
    users = dict()
    for line in credentials:
        if line[0] == '#':
            continue
        u, p = line.split(',')
        users[u] = p.strip() # removing \n characters
    return users
    

def get_config():
    # get configuration from file
    config = configparser.ConfigParser()
    config.read(CONFIG)
    return config


def get_vacations():
    # get vacations from file
    vacations = configparser.ConfigParser()
    vacations.read(VACATIONS)
    return vacations


def user_in_vacation(user,vacations):
    '''
    Determines if an specific user is on vacation 
    Returns true if user is on vacation or False if not in vacation
    '''
    today = localtime()
    
    # check if date is within vacation range
    start_1 = strptime(vacations[user].get('Vacation Start 1'), "%Y-%m-%d")
    start_2 = strptime(vacations[user].get('Vacation Start 2'), "%Y-%m-%d")
    start_3 = strptime(vacations[user].get('Vacation Start 3'), "%Y-%m-%d")
    end_1 = strptime(vacations[user].get('Vacation End 1'), "%Y-%m-%d")
    end_2 = strptime(vacations[user].get('Vacation End 2'), "%Y-%m-%d")
    end_3 = strptime(vacations[user].get('Vacation End 3'), "%Y-%m-%d")

    if (today > start_1 and today < end_1) or (today > start_2 and today < end_2) or (today > start_3 and today < end_3):
        return True
        
    return False

class EnterHours:
    def __init__(self, browser):
        self.open_session(browser)
    
    def open_session(self, browser):
        if browser == 'firefox':
            opts = f_Options()
            opts.headless = True
            assert opts.headless  # Operating in headless mode
            self.session = Firefox(options=opts)
        elif browser == 'ie':
            self.session = Ie()
        elif browser == 'chrome':
            opts = c_Options()
            opts.add_argument('--headless')
            self.session = Chrome(options=opts)
        elif browser == 'edge':
            self.session = Edge()
    
    def login(self, username, userpwd):
        self.session.get('https://www.bpocenter-dxc.com/iwom_web5/portal_apps.aspx')
        self.session.find_element_by_id("LoginApps_UserName").send_keys(username)
        self.session.find_element_by_id("LoginApps_Password").send_keys(userpwd)
        self.session.find_element_by_id("LoginApps_btnlogin").click()
        sleep(2)
    
    def open_app(self):        
        self.session.find_element_by_id("MainContent_LVportalapps_ctrl0_imgLogo_App_0").click()
        sleep(2)

    def entry_data(self):
        self.session.get('https://www.bpocenter-dxc.com/hp_web2/es-corp/app/Jornada/Reg_jornada.aspx')
        hstart = self.session.find_element_by_id("ctl00_Sustituto_d_hora_inicio1")
        mstart = self.session.find_element_by_id("ctl00_Sustituto_D_minuto_inicio1")
        hend = self.session.find_element_by_id("ctl00_Sustituto_d_hora_final1")
        mend = self.session.find_element_by_id("ctl00_Sustituto_d_minuto_final1")
        horas = self.session.find_element_by_id("ctl00_Sustituto_T_efectivo")
        
        # in case some values exist already, they need to be removed
        hstart.send_keys(Keys.HOME + hours['start_h'])
        mstart.send_keys(Keys.HOME + hours['start_m'])
        hend.send_keys(Keys.HOME + hours['end_h'])
        mend.send_keys(Keys.HOME + hours['end_m'])
        horas.send_keys(Keys.BACKSPACE*5 + hours['value'])
        self.session.find_element_by_id("ctl00_Sustituto_Btn_Guardar").click()
        sleep(2) # to ensure it has time to save

    def quit_session(self):
        self.session.quit()


######################## MAIN ##################################

if len(sys.argv) < 2: # no arguments
    browser = 'firefox'
else:
    browser = sys.argv[1]

# get global configuration, specific hours to enter, vacation information and user credentials
print(datetime.now().strftime(LOG_DATE_FORMAT), ": Loading configuration.", sep="")
conf = get_config()
print(datetime.now().strftime(LOG_DATE_FORMAT), ": Calculating hours.", sep="")
hours = calculate_hours(conf)
print(datetime.now().strftime(LOG_DATE_FORMAT), ": Loading vacations.", sep="")
vacs = get_vacations()
print(datetime.now().strftime(LOG_DATE_FORMAT), ": Loading users/credentials.", sep="")
users = get_credentials()

# for each user in users file, enter its hours except if it's on vacations
for user in users:
    if user_in_vacation(user,vacs) == True:
        print("{}: The user: {}, is on vacations.".format(datetime.now().strftime(LOG_DATE_FORMAT),user))
        continue
    print("{}: Starting registration of hours for user: {}.".format(datetime.now().strftime(LOG_DATE_FORMAT),user))
    username = user
    userpwd = users[user]
    print(datetime.now().strftime(LOG_DATE_FORMAT), ": Opening browser.", sep="")
    session = EnterHours(browser)
    print(datetime.now().strftime(LOG_DATE_FORMAT), ": Login into iWom.", sep="")
    session.login(username, userpwd)
    session.open_app()
    print(datetime.now().strftime(LOG_DATE_FORMAT), ": Entering information in iWom.", sep="")
    session.entry_data()
    print("{}: Closing session for user: {}".format(datetime.now().strftime(LOG_DATE_FORMAT),user))
    session.quit_session()
