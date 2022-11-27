import random

from telegram import Update
from telegram.ext import ContextTypes
import sheet_opener

inquisitor_sticker = "CAACAgIAAxkBAAEaZExjg10siWYVc-564wkQkg5n8tpw8AACDQQAAs9fiwea5hLxrvLEZCsE"
owl_sticker = "CAACAgIAAxkBAAEaZHBjg2JAmnLxCJJrRH1uwHwvx42kHAACxwIAAs9fiwdxXUx0SM7_lSsE"
fellini_sticker = "CAACAgIAAxkBAAEaZHJjg2LrXLLy7t93XU68Jq53jJ4B-QACRAgAAnlc4glkrEpkZJoLWSsE"
dyno_laptop_sticker = "CAACAgIAAxkBAAEaZHhjg2N4HkErFruUmwNV5SE83zhpYAACeQADECECEDUyG6uAD9F_KwQ"
game_of_thrones_sticker = "CAACAgEAAxkBAAEaZIJjg2QO6YQ65dJHFO_hiaMEJVGb0AACqwkAAr-MkATh82QK_QHjPCsE"
neo_sticker = "CAACAgIAAxkBAAEaZIZjg2S4TLkEszxCLuvGEgzfeoPEwQACcQIAAtzyqwcgmnJDHdtEXSsE"
stickers = [inquisitor_sticker, owl_sticker, owl_sticker,
            fellini_sticker, dyno_laptop_sticker,
            neo_sticker, game_of_thrones_sticker]


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
    def __init__(self, update: Update, bot_func):
        self.name = update.message.from_user.username
        self.sheets_of_interest = {}
        self.bot_func = bot_func
        self.user_id = update.message.from_user.id

    async def add_enq(self, sheet: sheet_opener.SheetObject, row_to_track, page=0):
        key = UserEnq.get_key_by_sheet_key(sheet.key, page, row_to_track)
        if key not in self.sheets_of_interest.keys():
            new_user_sheet = UserEnq(sheet.key, row_to_track, page)
            self.sheets_of_interest[key] = new_user_sheet
            await self.tel_print(f'[INFO] {self.name} added enquiry "{key}" to his/her pocket')
        else:
            await self.tel_print(f'[INFO] {self.name} already has enquiry "{key}" in his/her pocket')

    async def enquire(self, key, context: ContextTypes.DEFAULT_TYPE):
        if key not in self.sheets_of_interest:
            raise Exception('Problems with key for enquiry')
        value = self.sheets_of_interest[key]
        message = f'Tracking "{value.sheet_key}" spreadsheet on page '\
                  f'{value.page} in row {value.row_to_track}:\n'
        result = context.user_data['sheet_opener'].open_table(
            value.sheet_key, value.page, value.row_to_track)[0]
        last_result = self.sheets_of_interest[key].last_result
        self.sheets_of_interest[key].last_result = result
        if not last_result:
            message += f'[INFO] That was the first result for enquiry \"{key}\". '\
                       "We'll keep tabs on it\n"
            await self.tel_print(message.strip())
            return
        sticker = random.choice(stickers)
        if len(result) > len(last_result):
            message += f'[RESULT] Row {value.row_to_track} increased in length\n'
            await self.bot_func().send_sticker(chat_id=self.user_id, sticker=sticker)
        elif len(result) < len(last_result):
            message += f'[RESULT] Row {value.row_to_track} diminished in length'
            await self.bot_func().send_sticker(chat_id=self.user_id, sticker=sticker)
        else:
            were_differences = False
            for i in range(len(result)):
                if result[i] != last_result[i]:
                    if not were_differences:
                        message += "Differences:\n"
                    message += f'* Was: "{last_result[i]}", now: "{result[i]}"\n'
                    were_differences = True
            if not were_differences:
                message += f'Row {value.row_to_track} is the same: {result}'
            else:
                await self.bot_func().send_sticker(chat_id=self.user_id, sticker=sticker)
        await self.tel_print(message.strip())

    async def tel_print(self, msg=''):
        await self.bot_func().sendMessage(chat_id=self.user_id, text=msg)
