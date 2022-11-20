import psutil

import program_info
import sheet_opener
import user


def first_greeting():
    users = psutil.users()
    names = []
    for i in range(0, len(users)):
        names.append(users[i][0])
    user_name = None
    if len(names) == 1:
        print(f'Nice to meet you, {names[0]}!')
        user_name = names[0]
    else:
        print("You are {}, aren't you? Press Y for confirmation, else press N: ".
              format(names[0]), end='')
        s = input()
        if s == 'Y':
            print(f'So now we know that you are {names[0]}')
            user_name = names[0]
        if s == 'N':
            print('Other available users are:')
            for i in range(1, len(names)):
                print(f'#{i}: {names[i]}')
            print('Who are you? Print index: #', end='')
            while True:
                number = input()
                try:
                    number = int(number)
                except ValueError:
                    print("You've typed some cringe, try again: #", end='')
                    continue
                if number >= len(names):
                    print("There aren't so many options, enter smaller number: #", end='')
                    continue
                break
            print(f'OK, hi, {names[number]}!')
            user_name = names[number]
            if number == 0:
                print("We are wondering why you at first refused to agree that you are {}".
                      format(names[number]))
    return user.User.upload_user(user_name)


def add_row(words):
    opener = sheet_opener.SheetOpener()
    words_set = set(words[1:])
    key = None
    page = None
    row = None
    for i in words_set:
        if i.startswith("key="):
            key = i.removeprefix("key=")
        if i.startswith("page="):
            page = i.removeprefix("page=")
        if i.startswith("row="):
            row = i.removeprefix("row=")

    current_user.add_enq(opener.sheet_objs[key], row, page)


def add_spreadsheet(words):
    opener = sheet_opener.SheetOpener()
    words_set = set(words[1:])
    new_sheet_id = None
    new_sheet_name = None
    new_sheet_key = None
    for i in words_set:
        if i.startswith('https://docs.google.com/spreadsheets/d/'):
            new_sheet_id = i.removeprefix('https://docs.google.com/spreadsheets/d/')
            new_sheet_id = new_sheet_id[:new_sheet_id.find('/edit')]
        if i.startswith("name="):
            new_sheet_name = i.removeprefix("name=")
        if i.startswith("key="):
            new_sheet_key = i.removeprefix("key=")

    was_existing = False
    for i in opener.sheet_objs.values():
        if i.sheet_id == new_sheet_id:
            print("[ERROR] You've already registered that table")
            was_existing = True
            break
        if i.key == new_sheet_key:
            print("[ERROR] You've already used that key, choose another one")
            was_existing = True
            break
        if i.name == new_sheet_name:
            print("[ERROR] You've already used that name, choose another one")
            was_existing = True
            break
    if not was_existing:
        opener.add_sheet_object(
            sheet_opener.SheetObject(new_sheet_id, new_sheet_name, new_sheet_key))
        print(f'[RESULTS] Spreadsheet {new_sheet_name} was added to your list!')


def display_sheets():
    sheets_list = []
    for sheet_obj in sheet_opener.SheetOpener().sheet_objs.values():
        sheets_list.append(sheet_obj.name)
    if len(sheets_list) == 0:
        print("No available spreadsheets yet. You can add them via:\n"
              "add spreadsheet url name=... key=...")
    else:
        result = ''  # before was "Names of available spreadsheets are: ", it was found redundant
        sheets_list.sort()
        for i in sheets_list:
            result += i + ', '
        result = result[:-2]
        print(result)


def display_sheet_keys():
    keys_list = {}
    for sheet_obj in sheet_opener.SheetOpener().sheet_objs.values():
        keys_list[sheet_obj.key] = sheet_obj.name
    if len(keys_list) == 0:
        print("No available spreadsheets yet. You can add them via:\n"
              "add spreadsheet url name=... key=...")
    else:
        for key, value in keys_list.items():
            print(f'"{key}" for spreadsheet "{value}"')


def display_targets():
    targets = []
    for sheet_obj in current_user.sheets_of_interest.values():
        targets.append(sheet_obj.key)
    if len(targets) == 0:
        print("No available rows to watch yet. "
              "You can add them via add row key=... page=... row=...")
    else:
        print("Available targets are:")
        targets.sort()
        for i in targets:
            print('*', i)


def words_starts_with(words_list, string):
    string_list = string.split()
    if len(string_list) > len(words_list):
        return False
    for i in range(len(string_list)):
        if string_list[i] != words_list[i]:
            return False
    return True


def main():
    global current_user
    prog_info = program_info.ProgramInfo.upload()
    if not prog_info.last_user_name:
        current_user = first_greeting()
        prog_info.last_user_name = current_user.name
        prog_info.save()
    else:
        print('Hi, {}!'.format(prog_info.last_user_name))
        current_user = user.User.upload_user(prog_info.last_user_name)
    opener = sheet_opener.SheetOpener()
    opener.load_saved()

    for key in current_user.sheets_of_interest:
        current_user.enquire(key)

    exit_loop = False
    while not exit_loop:
        s = input()
        words = s.split()
        for i in range(10):
            if not words:
                break
            if words_starts_with(words, 'add spreadsheet'):
                add_spreadsheet(words)
                words = words[5:]
            elif words_starts_with(words, 'add row'):
                add_row(words)
                words = words[5:]
            elif words_starts_with(words, 'display sheets'):
                display_sheets()
                words = words[2:]
            elif words_starts_with(words, 'display sheet keys'):
                display_sheet_keys()
                words = words[3:]
            elif words_starts_with(words, 'display targets'):
                display_targets()
                words = words[2:]
            elif words_starts_with(words, 'track all targets'):
                words = words[3:]
                for key in current_user.sheets_of_interest:
                    current_user.enquire(key)
            elif words_starts_with(words, 'exit'):
                print('Goodbye, {}!'.format(current_user.name))
                exit_loop = True
                break
            else:
                print(f'[Misprint] "{words[0]}" is unknown command, skipping it')
                words = words[1:]

    current_user.save()
    opener.save_sheets()
    prog_info.save()


current_user = None
if __name__ == '__main__':
    main()
