import main_sheet
import sheet_opener
import user

import logging

from telegram import Bot, MessageEntity, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    Updater,
    filters
)

# Enable logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
CHOOSING, PARAMETERS_CHOICE = range(2)

reply_keyboard = [
    ["Add row", "Add spreadsheet"],
    ["Display sheets", "Display sheet keys"],
    ["Display targets", "Track all targets"],
    ["Exit"]
]
bookmark_tabs_emoji = '\U0001F4D1'
winking_face_emoji = '\U0001F609'
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
with open('bot_token.txt', 'r') as file:
    TOKEN = file.readline()


def return_bot():
    return Bot(token=TOKEN)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.user_data:
        reply_text = f"{winking_face_emoji} Hi again, {update.message.from_user['username']}!"
        await update.message.reply_text(reply_text, reply_markup=markup)
        await main_sheet.EnqProcessor.read_input(context, 'track all targets')
    else:
        reply_text = f"{bookmark_tabs_emoji}Hi! I am Check Sheets Bot. I can track your"\
                    f" spreadsheets in Google docs and inform you about changes!\n"
        reply_text += (
            "You are newcomer so it will be good of you to tell me what to track."
        )
        context.user_data['sheet_opener'] = sheet_opener.SheetOpener()
        context.user_data['sheet_opener'].create_dummy_self()
        context.user_data['user_obj'] = user.User(update, return_bot)
        await update.message.reply_text(reply_text, reply_markup=markup)
    return CHOOSING


'''
async def callback_30(context: ContextTypes.DEFAULT_TYPE, second_par):
    print(context.user_data)
    # await context.bot.send_message(chat_id='@examplechannel', text='One message every minute')
    await main_sheet.EnqProcessor.read_input(context, 'track_all_targets')
'''


async def command_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Perform predefined choice or ask for parameters."""
    context.user_data.pop('current_routine', None)
    text = update.message.text.lower()
    if text == '/start':
        await update.message.reply_text("It seems that you've already done int")
        return CHOOSING
    res = await main_sheet.EnqProcessor.read_input(context, text)
    if res and res != 'UnknownCommand':
        context.user_data['current_routine'] = text
        await update.message.reply_text(res)
        return PARAMETERS_CHOICE
    if res == 'UnknownCommand':
        await update.message.reply_text("Sorry I didn't understand it.")
    '''
    global application
    job_queue = application.job_queue
    job_queue.run_once(callback_30, 2)
    '''
    return CHOOSING


async def parameters_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if 'current_routine' not in context.user_data.keys():
        await update.message.reply_text('Seems that you want to insert parameters,'
                                        ' but not said earlier for what')
        return CHOOSING
    command = context.user_data['current_routine']
    context.user_data.pop('current_routine', None)
    words = update.message.text.split()
    res = await main_sheet.EnqProcessor.read_input(context,
                                                   command, words)
    if res == 'BadText':
        await update.message.reply_text('Seems that you tried to insert '
                                        'parameters for something invalid')
    elif res:
        await update.message.reply_text(res)
    return CHOOSING


async def exit_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        f"Ok, {update.message.from_user.full_name}, until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    global application
    persistence = PicklePersistence(filepath="checksheets_data")
    application = Application.builder().token(TOKEN).\
        persistence(persistence).build()

    # Add conversation handler with the states CHOOSING, PARAMETERS_CHOICE
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.TEXT & ~filters.Regex("^Exit$"), command_choice)
            ],
            PARAMETERS_CHOICE: [
                MessageHandler(
                    filters=filters.TEXT | filters.Entity(MessageEntity.URL),
                    callback=parameters_choice)
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Exit$"), exit_bot)],
        name="my_conversation",
        persistent=True,
    )
    application.add_handler(conv_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


application = None
if __name__ == "__main__":
    main()
