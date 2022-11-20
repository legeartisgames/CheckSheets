import pickle

import sheet_opener


class UserEnq:
    def __init__(self, key, row_to_track, page=0):
        self.page = int(page)
        self.row_to_track = row_to_track
        self.sheet_key = key
        self.key = UserEnq.get_key_by_sheet_key(key, page, row_to_track)
        self.last_result = None

    @staticmethod
    def get_key_by_sheet_key(sheet_key, page, row_to_track):
        return f"key: {sheet_key}, page: {page}, row: {row_to_track}"


class User:
    def __init__(self, name):
        self.name = name
        self.sheets_of_interest = {}

    def add_enq(self, sheet: sheet_opener.SheetObject, row_to_track, page=0):
        key = UserEnq.get_key_by_sheet_key(sheet.key, page, row_to_track)
        if key not in self.sheets_of_interest.keys():
            new_user_sheet = UserEnq(sheet.key, row_to_track, page)
            self.sheets_of_interest[key] = new_user_sheet
            print(f'[INFO] {self.name} added enquiry "{key}" to his/her pocket')
        else:
            print(f'[INFO] {self.name} already has enquiry "{key}" in his/her pocket')

    def enquire(self, key):
        if key not in self.sheets_of_interest:
            raise Exception('Problems with key for enquiry')
        value = self.sheets_of_interest[key]
        print(f'Tracking "{value.sheet_key}" spreadsheet on page '
              f'{value.page} in row {value.row_to_track}')
        result = sheet_opener.SheetOpener().open_table(
            value.sheet_key, value.page, value.row_to_track)[0]
        last_result = self.sheets_of_interest[key].last_result
        self.sheets_of_interest[key].last_result = result
        if not last_result:
            print(f'[INFO] That was the first result for enquiry \"{key}\". '
                  "We'll keep tabs on it")
            return
        if len(result) > len(last_result):
            print(f'[RESULT] Row {value.row_to_track} increased in length')
        elif len(result) < len(last_result):
            print(f'[RESULT] Row {value.row_to_track} diminished in length')
        else:
            were_differences = False
            for i in range(len(result)):
                if result[i] != last_result[i]:
                    if not were_differences:
                        print("Differences:")
                    print(f'* Was: "{last_result[i]}", now: "{result[i]}"')
                    were_differences = True
            if not were_differences:
                print(f'Row {value.row_to_track} is the same: {result}')

    def save(self):
        with open('pickle/user_{}_info.pkl'.format(self.name), 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def upload_user(name):
        try:
            with open('pickle/user_{}_info.pkl'.format(name), 'rb') as user_info_file:
                user_info = pickle.load(user_info_file)
        except FileNotFoundError:
            print("[INFO] Creating new user")
            user_info = User(name)
            user_info.save()
        return user_info
