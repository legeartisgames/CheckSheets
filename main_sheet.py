import sheet_opener

from telegram.ext import ContextTypes


class CustomException(Exception):
    def __init__(self, msg='Default exception', *args, **kwargs):
        self.msg = msg
        super().__init__(msg, *args, **kwargs)


class EnqProcessor:
    @staticmethod
    async def read_input(context: ContextTypes.DEFAULT_TYPE, text='', words=None):
        if text == 'track all targets':
            if not context.user_data['user_obj'].sheets_of_interest:
                await context.user_data['user_obj'].tel_print(
                    "No available rows to watch yet. "
                    "You can add them via Add row key=... page=... row=...")
            for key in context.user_data['user_obj'].sheets_of_interest:
                await context.user_data['user_obj'].enquire(key, context)
        elif text == 'display sheets':
            await EnqProcessor.display_sheets(context)
        elif text == 'display sheet keys':
            await EnqProcessor.display_sheet_keys(context)
        elif text == 'display targets':
            await EnqProcessor.display_targets(context)
        else:
            if not words:
                if text == 'add row':
                    return 'Please insert parameters: key=..., page=..., row=...'
                elif text == 'add spreadsheet':
                    return 'Please insert parameters: link=..., name=..., key=...'
                else:
                    return 'UnknownCommand'
            if text == 'add row':
                try:
                    await EnqProcessor.add_row(context, words)
                except CustomException as e:
                    if e.msg == 'no sheet key':
                        return "\U00002757 You haven't set sheet key!"
                    if e.msg == 'no row':
                        return "[ERROR] You haven't set row to track!"
                    if e.msg == 'no page':
                        return "[ERROR] You haven't set page to track!"

            elif text == 'add spreadsheet':
                try:
                    await EnqProcessor.add_spreadsheet(context, words)
                except CustomException as e:
                    if e.msg == 'no sheet name':
                        return "[ERROR] You haven't set sheet name!"
                    if e.msg == 'no sheet link':
                        return "[ERROR] You haven't set sheet link!"
            else:
                return 'BadText'

    @staticmethod
    async def add_row(context: ContextTypes.DEFAULT_TYPE, words):
        words_set = set(words)
        key = None
        page = 0
        row = None
        for i in words_set:
            if i.startswith("key="):
                key = i.removeprefix("key=")
            if i.startswith("page="):
                page = i.removeprefix("page=")
            if i.startswith("row="):
                row = i.removeprefix("row=")
        if not key:
            raise CustomException('no sheet key')
        if not row:
            raise CustomException('no row')
        await context.user_data['user_obj'].add_enq(
            context.user_data['sheet_opener'].sheet_objs[key], row, page)

    @staticmethod
    async def add_spreadsheet(context: ContextTypes.DEFAULT_TYPE, words):
        words_set = set(words)
        new_sheet_id = None
        new_sheet_name = None
        new_sheet_key = None
        for i in words_set:
            if i.startswith('link=') or i.startswith('https://docs.google.com/spreadsheets/d'):
                new_sheet_id = i.removeprefix('link=')
                new_sheet_id = new_sheet_id.removeprefix('https://docs.google.com/spreadsheets/d/')
                new_sheet_id = new_sheet_id[:new_sheet_id.find('/edit')]
            if i.startswith("name="):
                new_sheet_name = i.removeprefix("name=")
            if i.startswith("key="):
                new_sheet_key = i.removeprefix("key=")
        if not new_sheet_key:
            new_sheet_key = new_sheet_name
        if not new_sheet_name:
            raise CustomException('no sheet name')
        if not new_sheet_id:
            raise CustomException('no sheet link')
        was_existing = False
        for i in context.user_data['sheet_opener'].sheet_objs.values():
            if i.sheet_id == new_sheet_id:
                await context.user_data['user_obj'].tel_print(
                    "[ERROR] You've already registered that table")
                was_existing = True
                break
            if i.key == new_sheet_key:
                await context.user_data['user_obj'].tel_print(
                    "[ERROR] You've already used that key, choose another one")
                was_existing = True
                break
            if i.name == new_sheet_name:
                await context.user_data['user_obj'].tel_print(
                    "[ERROR] You've already used that name, choose another one")
                was_existing = True
                break
        if not was_existing:
            context.user_data['sheet_opener'].add_sheet_object(
                sheet_opener.SheetObject(new_sheet_id, new_sheet_name, new_sheet_key))
            await context.user_data['user_obj'].tel_print(
                f'[RESULTS] Spreadsheet {new_sheet_name} was added to your list!')

    @staticmethod
    async def display_sheets(context: ContextTypes.DEFAULT_TYPE):
        sheets_list = []
        for sheet_obj in context.user_data['sheet_opener'].sheet_objs.values():
            sheets_list.append(sheet_obj.name)
        if len(sheets_list) == 0:
            await context.user_data['user_obj'].tel_print(
                "No available spreadsheets yet. You can add them via:\n"
                "add spreadsheet url name=... key=...")
        else:
            result = ''  # before was "Names of available spreadsheets are: ", it was found redundant
            sheets_list.sort()
            for i in sheets_list:
                result += i + ', '
            result = result[:-2]
            await context.user_data['user_obj'].tel_print(result)

    @staticmethod
    async def display_sheet_keys(context: ContextTypes.DEFAULT_TYPE):
        keys_list = {}
        for sheet_obj in context.user_data['sheet_opener'].sheet_objs.values():
            keys_list[sheet_obj.key] = sheet_obj.name
        if len(keys_list) == 0:
            await context.user_data['user_obj'].tel_print(
                "No available spreadsheets yet. You can add them via:\n"
                "add spreadsheet url name=... key=...")
        else:
            output = ''
            for key, value in keys_list.items():
                output += f'"{key}" for "{value}"\n'
            output = output.strip()
            await context.user_data['user_obj'].tel_print(output)

    @staticmethod
    async def display_targets(context: ContextTypes.DEFAULT_TYPE):
        targets = []
        for sheet_obj in context.user_data['user_obj'].sheets_of_interest.values():
            targets.append(sheet_obj.key)
        if len(targets) == 0:
            await context.user_data['user_obj'].tel_print(
                "No available rows to watch yet. "
                "You can add them via add row key=... page=... row=...")
        else:
            output = 'Available results are:\n'
            targets.sort()
            for i in targets:
                output += '* ' + str(i) + '\n'
            await context.user_data['user_obj'].tel_print(output)


def words_starts_with(words_list, string):
    string_list = string.split()
    if len(string_list) > len(words_list):
        return False
    for i in range(len(string_list)):
        if string_list[i] != words_list[i]:
            return False
    return True
