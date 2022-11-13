# CheckSheets

This repository contains python code for running CheckSheets app, which gives user an opportunity to check his/her spreadsheets on Google Sheets.

As of 13th of November, you need to install on your computer these libraries to run the app:

1) psutil (it's remnant of an idea to create project with amusing hardware-stuff analysis), now it's necessary only for retrieving user name
2) Sheets Api (https://developers.google.com/sheets/api?hl=en_US)

How to make it ready:
* pip install psutil
* Check https://developers.google.com/sheets/api/quickstart/python for extensive instructions. In a nutshell:
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
* Open new issue in this repo and write there your email address on google if you want to use the app. Now it's in testing mode and only users with emails from set of testers (which is defined by developer) can use the app

