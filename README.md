# CheckSheets

This repository contains python code for running CheckSheetsBot, which gives user an opportunity to check spreadsheets on Google Sheets.

As of 4th of December 2022, you need to install on your computer these libraries to run the app:

Sheets Api (https://developers.google.com/sheets/api?hl=en_US)
Python-Telegram-Bot (https://github.com/python-telegram-bot/python-telegram-bot)

How to make it ready:
* Check https://developers.google.com/sheets/api/quickstart/python for extensive instructions. In a nutshell:
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
* You can see all in requirements.txt, but it seems that google libraries download successfully only in PyCharm
* Open new issue in this repo and write there your email address on google if you want to use the app. Now it's in testing mode and only users with emails from set of testers (which is defined by developer) can use the app

## About CheckSheets App
It's comfy way (or it was intended to be) to check all your spreadsheet data from google by running a single line (after attuning all things).
You may use CheckSheets for any purpose you wish to, but we see it as the best program to check your results while studying. For example, if your teacher owns a spreadsheet where he/she posts results of tests your class passes and you can't wait to see results of the new one, all you need is to run this checker program.
Though the main force of CheckSheets is it's support of multitasking. You can track all sheets, not only the hottest, but some updating only once a month. And you won't miss new changes with CheckSheets.

## Language of CheckSheets
For now you can run the app in console or in IDE. By the way, we have plans to make convenient telegram bot of console version. Using of CheckSheets consists of writing some instructions:
* `add spreadsheet [link] name=[title of your sheet] key=[short name for fast instructions]`
Example: `add spreadsheet 1ASedAXVIiPtzgeDKf1LI3Fh_VsV87SDgh-4_j1uk8Xw name=ListOfProjects key=201pythonlist` # you can omit first and last part of link
* `add row key=[of your sheet] page=[starting from 0] row=[as in Google Sheets]`
Example: `add row key=algo page=0 row=20` # algo and 
* `display sheets` # see all spreadsheets you added
* `display sheet keys` # see all keys of spreadsheets you added
* `display targets` # see all target rows you added
* `track all targets` # check all targets rows
* `exit` # stop the app

## Possible improvements:
* deleting of target sheets and rows
