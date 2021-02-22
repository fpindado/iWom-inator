# iWom-inator
iWom daily filling automation. It only fills today information, not multi-day filling.

It allows for multiple user filling, using the login and passwords saved in a .csv file, and detects whether the day is Friday or not, so it uses the right amount of hours. It is also able to take into account different type of absences and report them into iWom.


## Documentation about *Selenium*
- Link to *Selenium* homepage: https://selenium.dev/
- Link to documentation: https://selenium.dev/documentation/en/
- Link to complete API reference: https://selenium.dev/selenium/docs/api/py/api.html
- Link to selenium python package: https://pypi.org/project/selenium/


## Installation and execution

### Windows:

  1. Get the latest release from python, under folder `releases\`.
  2. Unzip on a folder in your PC
  3. Update the configuration files under `config/` folder:
      - file `config/users.csv` with your login(s) and password(s).
      - file `config/time` contains the hours to be logged.
      - file `config/absences.ini` with the absences dates. Follow instructions on the file to configure.
      - file `config/config.ini` app options, allows to change URLs of the app, or codes to be used for absences. In general, you don't need to change this file.
  4. The script is launched by one of the .bat files under `bin/` folder. Depending on the browser you use, pick the one that is right. Recommended options are firefox or chrome, as they will launch silently.
  5. You can add the launcher in the windows scheduler, so it runs every day to update the time.

### Linux

You only need the python script `iWom-update.py`, and the config files as above.

  1. **Pre-requisites**: you need to have `python3` installed, and the `selenium` package. You can get the selenium package by executing:
     - `pip3 install seleniunm`
  2. Get the latest release from python, under folder `releases\`.
  3. Unzip on a folder in your PC
  4. Update the configuration files under `config/` folder:
      - file `config/users.csv` with your login(s) and password(s).
      - file `config/time` contains the hours to be logged.
      - file `config/absences.ini` with the absences dates. Follow instructions on the file to configure.
      - file `config/config.ini` app options, allows to change URLs of the app, or codes to be used for absences. In general, you don't need to change this file.
  5. To execute you have two options:
     - execute the following: `python3 iWom-update.py <<browser>>`, where _browser_ is one of the following: 'firefox' or 'chrome'.
     - make the script executable, and then launch the script directly:
       - `chmod +x iWom-update.py`
       - `iWom-update.py <<browser>>`


## Dependencies / issues

This script uses [Selenium package](https://selenium.dev/) to automate the entry of hours, and it depends on having the right webdriver to interact with the browser. The script is ready to run on any of the browsers: Firefox, Chrome and Edge (in the latest version we removed support for Internet Explorer). The webdrivers for Firefox, Chrome and Edge are included in the distribution, but you need to make sure you have the right version for Edge, as its installation is quite dependent on the version; if you want to execute in Edge, you will need to install the latest webdriver from here:

https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

In case you have issues with the webdriver that is included in the distribution, because using a different version of web browser, you can download the appropriate driver from here:

https://selenium.dev/documentation/en/webdriver/driver_requirements/#quick-reference

And place it under the same folder as the iWom-update.exe program.
