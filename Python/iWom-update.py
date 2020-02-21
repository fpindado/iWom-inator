# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 18:15:06 2020

@author: opujo
"""

from selenium.webdriver import Firefox, Chrome, Ie, Edge
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from time import localtime, sleep, strptime
import sys
import configparser

CREDENTIALS = "config/users.csv"
CONFIG = "config/config.ini"
    

def calculate_hours(conf): # calculate hours
    ''' calculates the number of hours, and start/end time based on the date and config
    returns a dictionary with: start time (h and min), end time (h and min), and number of hours
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
    # get credentials from file
    config = configparser.ConfigParser()
    config.read(CONFIG)
    return config


class EnterHours:
    def __init__(self, browser, username, userpwd):
        self.username = username
        self.userpwd = userpwd
        self.open_session(browser)
    
    def open_session(self, browser):
        if browser == 'firefox':
            opts = Options()
            opts.headless = True
            assert opts.headless  # Operating in headless mode
            self.session = Firefox(options=opts)
        elif browser == 'ie':
            self.session = Ie()
        elif browser == 'chrome':
            self.session = Chrome()
        elif browser == 'edge':
            self.session = Edge()
    
    def login(self):
        self.session.get('https://www.bpocenter-dxc.com/iwom_web5/portal_apps.aspx')
        self.session.find_element_by_id("LoginApps_UserName").send_keys(self.username)
        self.session.find_element_by_id("LoginApps_Password").send_keys(self.userpwd)
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

    def quit_session(self):
        self.session.quit()


######################## MAIN ##################################

if len(sys.argv) < 2: # no arguments
    browser = 'firefox'
else:
    browser = sys.argv[1]

conf = get_config()
hours = calculate_hours(conf)
users = get_credentials()

for user in users:
    username = user
    userpwd = users[user]
    session = EnterHours(browser, username, userpwd)
    session.login()
    session.open_app()
    session.entry_data()
    session.quit_session()
