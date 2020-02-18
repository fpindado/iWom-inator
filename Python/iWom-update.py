# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 18:15:06 2020

@author: opujo
"""

from selenium.webdriver import Firefox, Chrome, Ie, Edge
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from time import asctime, mktime, localtime

CREDENTIALS = "users.csv"

def wait(sec):
    t1 = mktime(localtime())
    t2 = mktime(localtime())
    while t2-t1 < sec:   # wait a number of seconds
        t2 = mktime(localtime())
    

def calculate_hours(): # calculate hours
    weekday = asctime()[:3]
    if weekday == 'Fri':
        h = '6:30'
    elif weekday in ['Mon', 'Tue', 'Wed', 'Thu']:
        h = '8:32'
    else:
        print ("You can't run the macro during weekends!")
        h = '0:00'
    return h

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
    


class EnterHours:
    def __init__(self, browser, username, userpwd, hours):
        self.username = username
        self.userpwd = userpwd
        self.hours_value = hours
        
        self.open_session(browser)
        self.login()
        self.open_app()
        self.entry_data()
        self.save_quit()
    
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
    
    def open_app(self):
        wait(2)
        self.session.find_element_by_id("MainContent_LVportalapps_ctrl0_imgLogo_App_0").click()
        wait(2)

    def entry_data(self):
        self.session.get('https://www.bpocenter-dxc.com/hp_web2/es-corp/app/Jornada/Reg_jornada.aspx')
        hstart = self.session.find_element_by_id("ctl00_Sustituto_d_hora_inicio1")
        mstart = self.session.find_element_by_id("ctl00_Sustituto_D_minuto_inicio1")
        hend = self.session.find_element_by_id("ctl00_Sustituto_d_hora_final1")
        mend = self.session.find_element_by_id("ctl00_Sustituto_d_minuto_final1")
        horas = self.session.find_element_by_id("ctl00_Sustituto_T_efectivo")
        
        # in case some values exist already, they need to be removed
        hstart.send_keys(Keys.HOME+'09')
        mstart.send_keys(Keys.HOME+'0')
        hend.send_keys(Keys.HOME+'20')
        mend.send_keys(Keys.HOME+'0')
        horas.send_keys(Keys.BACKSPACE*5 + hours_value)

    def save_quit(self):
        self.session.find_element_by_id("ctl00_Sustituto_Btn_Guardar").click()
        self.session.quit()


######################## MAIN ##################################

hours = calculate_hours()
users = get_credentials()

for each in users:
    username = each
    userpwd = users[each]
    EnterHours('firefox', username, userpwd, hours)