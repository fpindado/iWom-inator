# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 17:25:32 2020
Script to create standard configuration file
@author: opujo
"""

FILE = "config/config.ini"

import configparser

config = configparser.ConfigParser()

config['DEFAULT'] = {
        'Start time': '09:00',
        'End time': '18:00',
        'Hours': '08:32',
        'Start date': '2020-01-01',
        'End date': '2020-12-31',
        }

config['Jornada normal'] = {}

config['Jornada reducida'] = {
        'Hours': '06:30',
        'End time': '16:00',
        'Start date': '2020-06-15',
        'End date': '2020-09-15',
        }

config['Weekends'] = {
        'Start time': '00:00',
        'End time': '00:00',
        'Hours': '00:00',
        }

with open(FILE, 'w') as configfile:
    config.write(configfile)
