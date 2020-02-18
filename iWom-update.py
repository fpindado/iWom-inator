# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 18:15:06 2020

@author: opujo
"""

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from time import asctime, mktime, localtime


NAME = "Oriol Pujol"
PWD = "iWom-2019"

# to work in silent mode
opts = Options()
opts.headless = True
assert opts.headless  # Operating in headless mode

# open login page, enter credentials
browser = Firefox(options=opts)
browser.get('https://www.bpocenter-dxc.com/iwom_web5/portal_apps.aspx')

browser.find_element_by_id("LoginApps_UserName").send_keys(NAME)
browser.find_element_by_id("LoginApps_Password").send_keys(PWD)
browser.find_element_by_id("LoginApps_btnlogin").click()
browser.find_element_by_id("MainContent_LVportalapps_ctrl0_imgLogo_App_0").click()

# open entry page, and introduce data
t1 = mktime(localtime())
t2 = mktime(localtime())
while t2-t1 < 2:   # wait 2 sec.
    t2 = mktime(localtime())


browser.get('https://www.bpocenter-dxc.com/hp_web2/es-corp/app/Jornada/Reg_jornada.aspx')
hstart = browser.find_element_by_id("ctl00_Sustituto_d_hora_inicio1")
mstart = browser.find_element_by_id("ctl00_Sustituto_D_minuto_inicio1")
hend = browser.find_element_by_id("ctl00_Sustituto_d_hora_final1")
mend = browser.find_element_by_id("ctl00_Sustituto_d_minuto_final1")
horas = browser.find_element_by_id("ctl00_Sustituto_T_efectivo")

# in case some values exist already, they need to be removed
hstart.send_keys(Keys.HOME+'09')
mstart.send_keys(Keys.HOME+'0')
hend.send_keys(Keys.HOME+'18')
mend.send_keys(Keys.HOME+'0')
horas.send_keys(Keys.BACKSPACE*5+'08:32')

# save, and close browser
browser.find_element_by_id("ctl00_Sustituto_Btn_Guardar").click()
browser.quit()
