Summary:
Script that will automatically create an account/sign in and auto fill out a job application that uses the workday system.

Currently script is very early in it's progress.

Answer to questions are given in an excel file called "Answer"

requires selenium, and pandas libraries

Before running script must have chromedriver in a PATH folder and then run a command prompt as an adminstrator. In cmd input the following: chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\JoshG\Documents\Machine Learning\JobApp_Automation\ChromeProfile"
This will open a chrome script in debug mode. Currently works by having the chrome window viewable on the screen (I usually put it on the side). If the chrome window is not viewable when being run errors may be encountered due to some items not showing until the screen is viewed.
