# iWom-inator
iWom daily filling automation. It only fills today information, not multi-day filling.

It allows for multiple user filling, using the login and passwords saved in a .csv file, and detects whether the day is Friday or not, so it uses the right amount of hours.


## Documentation about *Selenium*
- Link to *Selenium* homepage: https://selenium.dev/
- Link to documentation: https://selenium.dev/documentation/en/
- Link to complete API reference: https://selenium.dev/selenium/docs/api/py/api.html
- Link to selenium python package: https://pypi.org/project/selenium/


## Installation and execution
1. Get the latest release from python, under folder `releases\`.
2. Unzip on a folder in your PC
3. Update the file `config/users.csv` with your login(s) and password(s).
4. Run file `iWom-update`.
5. You can add the file in the windows scheduler, so it runs every day to update the time


## Dependencies / issues

This script uses [Selenium package](https://selenium.dev/) to automate the entry of hours, and it depends on having the right webdriver to interact with the browser. The script is ready to run on any of the browsers: Firefox, Chrome, Edge and Internet Explorer. The webdrivers for Firefox, Chrome and Edge are included in the distribution, but not for Edge, as its installation is quite dependant on the version; if you want to execute in Edge, you will need to install the latest webdriver from here:

https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

At the moment, it only works with Firefox. In later releases we will include launchers for each browser.

In case you have issues with the webdriver that is included in the distribution, because using a different version of web browser, you can download the appropriate driver from here:

https://selenium.dev/documentation/en/webdriver/driver_requirements/#quick-reference

And place it under the same folder as the executable.
