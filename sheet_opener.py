# from __future__ import print_function
import os.path
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


class SheetObject:
    def __init__(self, sheet_id, name, key=None):
        self.name = name
        if not key:
            self.key = name
        else:
            self.key = key
        self.sheet_id = sheet_id
        self.sheet_names = None  # Opener will fill it
        SheetOpener.add_sheet_names_to_sheet_object(SheetOpener(), self)


class SheetOpener:
    def __init__(self):
        self.creds = None
        self.service = None
        self.establish_connection()
        self.sheet_objs = dict()

    def establish_connection(self):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            create_new_flow = True
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                    print("[INFO] Refreshing credentials for connection with google")
                    create_new_flow = False
                except RefreshError as ex:
                    create_new_flow = True
                    print(f"[ERROR] Refreshing is not possible: {ex}\n"
                          "Probably it's because the app is in testing mode so token expires\n"
                          "Anyway, it's safer to create new token")
            if create_new_flow:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        try:
            self.service = build('sheets', 'v4', credentials=self.creds)
        except HttpError as err:
            print(err)

    def add_sheet_object(self, sheet_object: SheetObject):
        self.sheet_objs[sheet_object.key] = sheet_object

    def add_sheet_names_to_sheet_object(self, sheet_object: SheetObject):
        sheet_metadata = self.service.spreadsheets().\
            get(spreadsheetId=sheet_object.sheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        titles = []
        for i in range(len(sheets)):
            titles.append(sheets[i].get("properties", {}).get("title"))
        sheet_object.sheet_names = titles

    '''
    def load_saved(self):
        try:
            with open('pickle/sheets.pkl', 'rb') as file_sheets:
                sheet_objs = pickle.load(file_sheets)
                self.sheet_objs = sheet_objs
                print("[INFO] Remembered sheets are extracted")
        except FileNotFoundError:
            print("[INFO] Building new sheets")
            self.add_sheet_object(SheetObject(
                '1_YSjF5Pakm4NhEc50HfCdy5nPmfAeFeQv2emSuW9UNE',
                'Local Python', 'python_group_rating'))
            self.add_sheet_object(SheetObject(
                '1s8zPnl0-c1yY1PHNxxatJc9XTajO15v0aFxj6Hcvkug',
                'Algorithms', 'algo'))
            self.save_sheets()

    def save_sheets(self):
        os.makedirs('pickle', exist_ok=True)
        with open('pickle/sheets.pkl', 'wb') as output:
            pickle.dump(self.sheet_objs, output, pickle.HIGHEST_PROTOCOL)
    '''
    def create_dummy_self(self):
        print("[INFO] Building new sheets")
        self.add_sheet_object(SheetObject(
            '1_YSjF5Pakm4NhEc50HfCdy5nPmfAeFeQv2emSuW9UNE',
            'Local Python', 'python_group_rating'))
        self.add_sheet_object(SheetObject(
            '1s8zPnl0-c1yY1PHNxxatJc9XTajO15v0aFxj6Hcvkug',
            'Algorithms', 'algo'))

    def open_table(self, sheet_key, page, number_of_line):
        try:
            sheet = self.service.spreadsheets()
            range_name = "{name}!{row}:{row}".format(
                name=self.sheet_objs[sheet_key].sheet_names[page],
                row=number_of_line)
            result = sheet.values().get(
                spreadsheetId=self.sheet_objs[sheet_key].sheet_id,
                range=range_name).execute()
            values = result.get('values', [])

            if not values:
                print('No data found.')
                return None
            return values

        except HttpError as err:
            print(err)
