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

from selenium.webdriver import Firefox, Chrome, Edge
from selenium.webdriver.firefox.options import Options as f_Options
from selenium.webdriver.chrome.options import Options as c_Options
from selenium.webdriver.common.keys import Keys
from time import sleep
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
    TIME_FILE = conf['Files']['Time']
    CREDENTIALS_FILE = conf['Files']['Credentials']
    ABSENCE_FILE = conf['Files']['Absences']
    LOG_FILE = conf['Files']['Log']

    ABSENCE = dict(conf['Absences'])

    WEB=dict()
    WEB['URLbase'] = conf['Web elements']['URL base']
    WEB['URLjornada'] = conf['Web elements']['URL jornada']
    WEB['Disponible'] = conf['Web elements']['Disponible']
    WEB['Hinicio'] = conf['Web elements']['Hora inicio']
    WEB['Minicio'] = conf['Web elements']['Minuto inicio']
    WEB['Hfinal'] = conf['Web elements']['Hora final']
    WEB['Mfinal'] = conf['Web elements']['Minuto final']
    WEB['Horas'] = conf['Web elements']['Horas']
    WEB['Submit'] = conf['Web elements']['Submit hours']
    WEB['Absence'] = conf['Web elements']['Absence type']
    WEB['Submit2'] = conf['Web elements']['Submit absences']


def calculate_hours(conf): # calculate hours
    """Calculates the number of hours, and start/end time based on the
    date and config file.

    Returns a dictionary with:
        start time (h and min),
        end time (h and min),
        and number of hours
    """

    # check if date is within range
    start = conf['Jornada normal'].get('start date')
    start = dt.date.fromisoformat(start)
    end = conf['Jornada normal'].get('end date')
    end = dt.date.fromisoformat(end)
    if today < start or today > end:
        log_entry ("Date is out of range. Please update your config file and \
                   run again. ", with_user=False)
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
    """get credentials from file"""

    with open (CREDENTIALS_FILE, encoding='utf-8-sig') as f:
        credentials = f.readlines()

    users = dict()
    for line in credentials:
        if line[0] == '#':
            continue
        u, p = line.split(',')
        users[u] = p.strip() # removing \n characters
    return users


def get_config(file):
    """returns the configuration from file"""

    config = configparser.ConfigParser()
    config.read(file)
    return config


def user_absence(login, conf):
    """returns the type of absence, based on the configuration of
    login
    """
    if today.isoweekday() > 5: # weekend
        return '00'

    abs_days = dict()
    for typ in ABSENCE:
        abs_days[typ] = set()
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
                [ abs_days[n].add(day) for n in ABSENCE if key.lower().startswith(n) ]
                day += delta
        else:
            day = dt.date.fromisoformat(period)
            [ abs_days[n].add(day) for n in ABSENCE if key.lower().startswith(n) ]

    ret = [ ABSENCE[n] for n in ABSENCE if today in abs_days[n] ]

    return set_priority(ret)


def set_priority(var):
    """from the list var, it determines the right variable to return
    taking into account the priorities of the different absences in
    case of overlapping
    """

    if len(var) == 0: # if list empty, return empty string
        ret = ''
    elif len(var) == 1: # if only one value, return the value
        ret = var[0]
    else:               # need to set the right priority
        if '00' in var:
            ret = '00'
        else:
            ret = sorted(var, reverse=True)[0]

    return ret


def log_entry(text, with_user=True):
    """prints text in a log, including a timestamp and formatting"""

    if with_user:
        msg = f"{dt.datetime.now().strftime(LOG_DATE_FORMAT)}: [{user}] {text}"
    else:
        msg = f"{dt.datetime.now().strftime(LOG_DATE_FORMAT)}: {text}"
    print(msg)
    log_msg.append(msg+"\n")



class EnterHours:
    """Object to create a session and interact
    with browser to enter the hours
    """

    def __init__(self, browser):
        self.open_session(browser)

    def open_session(self, browser):
        """opens a session using the browser specified"""
        if browser == 'firefox':
            opts = f_Options()
            opts.headless = True
            assert opts.headless  # Operating in headless mode
            self.session = Firefox(options=opts)
        elif browser == 'chrome':
            opts = c_Options()
            opts.add_argument('--headless')
            self.session = Chrome(options=opts)
        elif browser == 'edge':
            self.session = Edge(executable_path=r".\msedgedriver.exe")

    def login(self, username, userpwd):
        """login to iWom app, using the login and password"""

        self.session.get(WEB['URLbase'])
        self.session.find_element_by_id("LoginApps_UserName").send_keys(username)
        self.session.find_element_by_id("LoginApps_Password").send_keys(userpwd)
        self.session.find_element_by_id("LoginApps_btnlogin").click()
        sleep(2)

    def open_app(self):
        """clicks the button to open the app"""

        self.session.find_element_by_id("MainContent_lblSubtitulo_app4").click()
        sleep(2)

    def entry_hours(self):
        """enter the hours into the app"""

        self.session.get(WEB['URLjornada'])
        sleep(2)
        btn_disponible = self.session.find_element_by_id(WEB['Disponible'])
        if not btn_disponible.is_selected():
            btn_disponible.click()
            sleep(2)
        hstart = self.session.find_element_by_id(WEB['Hinicio'])
        mstart = self.session.find_element_by_id( WEB['Minicio'])
        hend = self.session.find_element_by_id(WEB['Hfinal'])
        mend = self.session.find_element_by_id(WEB['Mfinal'])
        horas = self.session.find_element_by_id(WEB['Horas'])

        # in case some values exist already, they need to be removed
        hstart.send_keys(Keys.HOME + hours['start_h'])
        mstart.send_keys(Keys.HOME + hours['start_m'])
        hend.send_keys(Keys.HOME + hours['end_h'])
        mend.send_keys(Keys.HOME + hours['end_m'])
        horas.send_keys(Keys.BACKSPACE*5 + hours['value'])
        self.session.find_element_by_id(WEB['Submit']).click()
        sleep(2) # to ensure it has time to save

    def entry_absent(self, abs_type):
        """mark the current day as vacation"""

        self.session.get(WEB['URLjornada'])
        btn_disponible = self.session.find_element_by_id(WEB['Disponible'])
        if btn_disponible.is_selected():
            btn_disponible.click()
            sleep(2)

        self.session.find_element_by_id(WEB['Absence']).send_keys(Keys.HOME + abs_type)
        sleep(2) # wait to give time to update the page
        self.session.find_element_by_id(WEB['Submit2']).click()
        sleep(2) # to ensure it has time to save

    def quit_session(self):
        """close the session and quit the browser"""
        self.session.quit()


######################## MAIN ##################################

if len(sys.argv) < 2: # no arguments
    browser = 'firefox'
else:
    browser = sys.argv[1]

log_msg = list()
today = dt.date.today()

# get global configuration, specific hours to enter, vacation information and user credentials
log_entry ("Loading configuration files.", with_user=False)
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
