# WorkdayAutomatedJobApp
Script that automatically signs up/signs in and fills out workday job app

Current Version is 1.01:
Program will automatically fill out Workday job application forms. Information for filling out the forms is entered into an excel file "Answers.xlsx". UI prompts user to input a link to the job app which then allow them to press "Start Application" which will load the page, create an account, and sign in. Once signed in can press "continue" to fill out the appliation. If an issue, such as there is no answer to a given question, the program will throw an error. User can correct error and press "continue" to continue auto filling out the application.

Currently the program is still very buggy and in development. However, it is currently usable for myself. Further work in the future will be done to allow it to work for others. For example, such that they don't need to change the hard coded directories.

Script has not yet been exported to .py file. Still using jupyter notebook Main.ipynb as it's easier for debugging piecewise.

Code works but is still in internal testing phase. Final product should only required launching the script or .exe and using the UI.

requires selenium, and pandas libraries

Before running script must have chromedriver in a PATH folder and then run a command prompt as an adminstrator. In cmd input the following: chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\JoshG\Documents\Machine Learning\JobApp_Automation\ChromeProfile"
This will open a chrome script in debug mode. Currently works by having the chrome window viewable on the screen (I usually put it on the side). If the chrome window is not viewable when being run errors may be encountered due to some items not showing until the screen is viewed.
