import psutil

import program_info
import sheet_opener
import user


def first_greeting():
    users = psutil.users()
    names = []
    for i in range(0, len(users)):
        names.append(users[i][0])
    names.append('Mr X')  # remove it in final version
    if len(names) == 1:
        print('Nice to meet you, {}!'.format(names[0]))
        user_name = names[0]
    else:
        print("You are {}, aren't you? Press Y for confirmation, else press N: ".format(names[0]), end='')
        s = input()
        if s == 'Y':
            print('So now we know that you are {}'.format(names[0]))
            user_name = names[0]
        if s == 'N':
            print('Other available users are:')
            for i in range(1, len(names)):
                print('#{}: {}'.format(i, names[i]))
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
            print('OK, hi, {}!'.format(names[number]))
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
        opener.add_sheet_object(sheet_opener.SheetObject(new_sheet_id,
                                                         new_sheet_name, new_sheet_key))
        print("[RESULTS] Spreadsheet {} was added to your list!".format(new_sheet_name))


def display_sheets(to_display='name'):
    sheets_list = []
    for sheet_obj in sheet_opener.SheetOpener().sheet_objs.values():
        sheets_list.append(getattr(sheet_obj, to_display))
    if len(sheets_list) == 0:
        print("No available spreadsheets yet. You can add them via add_spreadsheet url name=... key=...")
    else:
        result = to_display[0].upper() + to_display[1:] + "s of available spreadsheets are: "
        sheets_list.sort()
        for i in sheets_list:
            result += i + ', '
        result = result[:-2]
        print(result)


def display_targets():
    targets = []
    for sheet_obj in current_user.sheets_of_interest.values():
        targets.append(sheet_obj.key)
    if len(targets) == 0:
        print("No available rows to watch yet. You can add them via add_row key=... page=... row=...")
    else:
        print("Available targets are:")
        targets.sort()
        for i in targets:
            print('*', i)


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

    while True:
        s = input()
        words = s.split()
        if 'add spreadsheet' in s:
            add_spreadsheet(words)
            words = words[5:]
        if 'add row' in s:
            add_row(words)
            words = words[5:]
        if 'display sheets' in s:
            display_sheets()
        if 'display sheet keys' in s:
            display_sheets('key')
        if 'display targets' in s:
            display_targets()
        if 'watch all targets' in s:
            for key in current_user.sheets_of_interest:
                current_user.enquire(key)
        if 'exit' in s:
            print("Goodbye, {}!".format(current_user.name))
            break

    current_user.save()
    opener.save_sheets()
    prog_info.save()


current_user = None
if __name__ == '__main__':
    main()

