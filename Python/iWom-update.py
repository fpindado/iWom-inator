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
from time import sleep
import datetime as dt
import sys
import configparser

CREDENTIALS = "config/users.csv"
CONFIG = "config/config.ini"
VACATION = "config/vacation.ini"
LOG_DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
LOG_FILE = "config/sessions.log"


def calculate_hours(conf): # calculate hours
    ''' calculates the number of hours, and start/end time based on the date 
    and config file. 
    Returns a dictionary with: 
        start time (h and min), 
        end time (h and min), 
        and number of hours
    '''
    
    # check if date is within range
    start = conf['Jornada normal'].get('start date')
    start = dt.date.fromisoformat(start)
    end = conf['Jornada normal'].get('end date')
    end = dt.date.fromisoformat(end)    
    if today < start or today > end:
        print('Date is out of range. Please update your config file and run again.')
        input('Press enter to finish')
        exit(0)
    
    start = conf['Jornada reducida'].get('start date')
    start = dt.date.fromisoformat(start)
    end = conf['Jornada reducida'].get('end date')
    end = dt.date.fromisoformat(end)    
   
    if (today > start and today < end) or today.isoweekday() == 5:
        section = 'Jornada reducida'
    elif today.isoweekday() < 5:
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
    ''' get credentials from file '''
    with open (CREDENTIALS, encoding='utf-8-sig') as f:
        credentials = f.readlines()
    
    users = dict()
    for line in credentials:
        if line[0] == '#':
            continue
        u, p = line.split(',')
        users[u] = p.strip() # removing \n characters
    return users
    

def get_config(file):
    ''' returns the configuration from file '''
    config = configparser.ConfigParser()
    config.read(file)
    return config


def user_vacation(login, conf):
    ''' returns a set with all vacation days from the user '''
    vacation = set()
    delta = dt.timedelta(days=1)
    if login in conf:
        user = login
    else:
        user = 'DEFAULT'
    for key in conf[user]:
        period = conf[user][key]
        if ' to ' in period:
            start, end = period.split(' to ')
            start = dt.date.fromisoformat(start)
            end = dt.date.fromisoformat(end)
            day = start
            while day <= end:
                vacation.add(day)
                day += delta
        else:
            vacation.add(dt.date.fromisoformat(period))
    return vacation

    

def log_entry(text):
    ''' prints text in a log, including a timestamp and formatting '''
    msg = dt.datetime.now().strftime(LOG_DATE_FORMAT) + ": " + text
    print(msg)
    log_msg.append(msg+"\n")



class EnterHours:
    ''' Object to create a session and interact 
    with browser to enter the hours
    '''
    def __init__(self, browser):
        self.open_session(browser)
    
    def open_session(self, browser):
        ''' opens a session using the browser specified '''
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
        ''' login to iWom app, using the login and password '''
        self.session.get('https://www.bpocenter-dxc.com/iwom_web5/portal_apps.aspx')
        self.session.find_element_by_id("LoginApps_UserName").send_keys(username)
        self.session.find_element_by_id("LoginApps_Password").send_keys(userpwd)
        self.session.find_element_by_id("LoginApps_btnlogin").click()
        sleep(2)
    
    def open_app(self):   
        ''' clicks the button to open the app '''
        self.session.find_element_by_id("MainContent_LVportalapps_ctrl0_imgLogo_App_0").click()
        sleep(2)

    def entry_hours(self):
        ''' enter the hours into the app '''
        self.session.get('https://www.bpocenter-dxc.com/hp_web2/es-corp/app/Jornada/Reg_jornada.aspx')
        btn_disponible = self.session.find_element_by_id("ctl00_Sustituto_Ch_disponible")
        if not btn_disponible.is_selected():
            btn_disponible.click()
            sleep(2)
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

    def entry_absent(self):
        ''' mark the current day as vacation '''
        self.session.get('https://www.bpocenter-dxc.com/hp_web2/es-corp/app/Jornada/Reg_jornada.aspx')
        btn_disponible = self.session.find_element_by_id("ctl00_Sustituto_Ch_disponible")
        if btn_disponible.is_selected():
            btn_disponible.click()
            sleep(2)
            self.session.find_element_by_id("ctl00_Sustituto_D_absentismo").send_keys("01")
            self.session.find_element_by_id("ctl00_Sustituto_Btn_Guardar2").click()
            sleep(2) # to ensure it has time to save
        else:
            log_entry(f'Already configured as vacation. Skiping action.')

    def quit_session(self):
        self.session.quit()


######################## MAIN ##################################

if len(sys.argv) < 2: # no arguments
    browser = 'firefox'
else:
    browser = sys.argv[1]

log_msg = list()
today = dt.date.today()

# get global configuration, specific hours to enter, vacation information and user credentials
log_entry ("Loading configuration files.")
conf = get_config(CONFIG)
hours = calculate_hours(conf)
vac = get_config(VACATION)
users = get_credentials()


# for each user in users file, enter its hours except if it's on vacations
for user in users:
    log_entry(f'Starting registration of hours for user {user}.')
    username = user
    userpwd = users[user]
    log_entry('Opening browser.')
    session = EnterHours(browser)
    log_entry('Login into iWom.')
    session.login(username, userpwd)
    session.open_app()
    if today in user_vacation(user, vac):
        log_entry(f'Entering information in iWom: on vacation today.')
        session.entry_absent()
    else:
        log_entry(f'Entering information in iWom: {hours["value"]} hours.')
        session.entry_hours()
    log_entry(f'Closing session for user {user}')
    session.quit_session()

# write log messages to file
with open(LOG_FILE, mode='at', encoding='utf-8') as log:
    log.writelines(log_msg)

