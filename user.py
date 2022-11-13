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
        return "key: {}, page: {}, row: {}".format(sheet_key,
                                                   page, row_to_track)


class User:
    def __init__(self, name):
        self.name = name
        self.sheets_of_interest = {}

    def add_enq(self, sheet: sheet_opener.SheetObject, row_to_track, page=0):
        key = UserEnq.get_key_by_sheet_key(sheet.key, page, row_to_track)
        if key not in self.sheets_of_interest.keys():
            new_user_sheet = UserEnq(sheet.key, row_to_track, page)
            self.sheets_of_interest[key] = new_user_sheet
            print('[INFO] User {u_name} added enquiry "{enq_name}" to his/her pocket'.format(u_name=self.name,
                                                                                             enq_name=key))
        else:
            print('[INFO] User {u_name} already has enquiry "{enq_name}" in his/her pocket'.format(u_name=self.name,
                                                                                                   enq_name=key))

    def enquire(self, key):
        if key not in self.sheets_of_interest:
            raise Exception('Problems with key for enquiry')
        value = self.sheets_of_interest[key]
        print(f'Tracking "{value.sheet_key}" spreadsheet on page {value.page} in row {value.row_to_track}')
        result = sheet_opener.SheetOpener().open_table(value.sheet_key, value.page, value.row_to_track)[0]
        last_result = self.sheets_of_interest[key].last_result
        self.sheets_of_interest[key].last_result = result
        if not last_result:
            print("[INFO] That was the first result for enquiry \"{}\". We'll keep tabs on it".format(key))
            return
        if len(result) > len(last_result):
            print("[RESULT] Row {} increased in length".format(value.row_to_track))
        elif len(result) < len(last_result):
            print("[RESULT] Row {} diminished in length".format(value.row_to_track))
        else:
            were_differences = False
            for i in range(len(result)):
                if result[i] != last_result[i]:
                    if not were_differences:
                        print("Differences:")
                    print('* Was: "{}", now: "{}"'.format(last_result[i], result[i]))
                    were_differences = True
            if not were_differences:
                print(f"Row {value.row_to_track} is the same: {result}")

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


'''
add spreadsheet https://docs.google.com/spreadsheets/d/1ItG8pVyAZbAgO5lt7yseaBz3V11X5gW6DvyBCj47URc/edit#gid=0 name=LuntikPosvyat key=luntik
add row key=luntik page=0 row=10
'''