import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, ConversationHandler, CallbackQueryHandler
from datetime import date, timedelta

import DbHandler
from Config import *

TYPING_REPLY, CHOOSING, TYPING_CHOICE = range(3)

bot = telegram.Bot(telegram_bot_token)

def main():
    print("*** Telegram bot is running ***")

    updater = Updater(telegram_bot_token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CallbackQueryHandler(menu_handler))

    dp.add_handler(telegram.ext.CommandHandler("help", help))
    dp.add_handler(telegram.ext.CommandHandler("cdb", check_and_or_create_db))
    # dp.add_handler(telegram.ext.CommandHandler('reserve', reserve_car))

    conv_res_handler = telegram.ext.ConversationHandler(
        entry_points=[telegram.ext.CommandHandler("reserve", reserve_car)],
        states={TYPING_REPLY: [telegram.ext.MessageHandler(telegram.ext.Filters.text, reservation_time)],
                TYPING_CHOICE: [telegram.ext.MessageHandler(telegram.ext.Filters.text, reservation_place)]},
        fallbacks=[telegram.ext.MessageHandler(telegram.ext.Filters.regex('^Done$'), done)]
    )

    conv_register_handler = telegram.ext.ConversationHandler(
        entry_points=[telegram.ext.CommandHandler("register", register)],
        states={TYPING_REPLY: [telegram.ext.MessageHandler(telegram.ext.Filters.text, user_register)]},
        fallbacks=[telegram.ext.MessageHandler(telegram.ext.Filters.regex('^Done$'), done)]
    )

    dp.add_handler(conv_res_handler)
    dp.add_handler(conv_register_handler)


    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

def menu_handler(update, context):
    query = update.callback_query
    query_option = str(query.data)
    chat_id = query.message.chat.id

    if query.data == 'normal_cars':
        keyboard = [[telegram.InlineKeyboardButton("Volvo S40", callback_data='volvo_chosen'),
                     telegram.InlineKeyboardButton("Hyundai Getz", callback_data='hyundai_chosen')],
                    [telegram.InlineKeyboardButton("Opel Vectra C", callback_data='opel_chosen')]]
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        query.edit_message_text("Here is a list of normal cars currently available for reservation:", reply_markup=reply_markup)
    elif query.data == 'special_cars':
        keyboard = [[telegram.InlineKeyboardButton("Volvo S40 with ramp", callback_data='volvo_special_chosen'),
                     telegram.InlineKeyboardButton("Hyundai Getz with ramp", callback_data='hyundai_special_chosen')]]
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        query.edit_message_text("Here is a list of special needs cars currently available for reservation:",
                                reply_markup=reply_markup)
    elif '_chosen' in query.data:
        car = '-' + str(query.data).split('_')[0]
        day1 = date.today().strftime("%d/%m/%Y")
        day2 = date.today() + timedelta(days=1)
        day3 = day2 + timedelta(days=1)
        day5 = day3 + timedelta(days=2)

        keyboard = [[telegram.InlineKeyboardButton(str(day1), callback_data='date_' + str(day1) + car),
                     telegram.InlineKeyboardButton(str(day2.strftime("%d/%m/%Y")), callback_data='date_' + str(day2.strftime("%d/%m/%Y") + car)),
                     telegram.InlineKeyboardButton(str(day3.strftime("%d/%m/%Y")), callback_data='date_' + str(day3.strftime("%d/%m/%Y") + car))],
                    [telegram.InlineKeyboardButton(str(day5.strftime("%d/%m/%Y")), callback_data='date_' + str(day5.strftime("%d/%m/%Y") + car))]]
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        query.edit_message_text("Please choose a date for your chosen car",
                                reply_markup=reply_markup)
    elif 'date_' in query.data:
        car_and_date = '-' + str(query.data).split('_')[1]
        keyboard = [[telegram.InlineKeyboardButton("AM", callback_data='AM_' + car_and_date),
                     telegram.InlineKeyboardButton("PM", callback_data='PM_' + car_and_date)]]
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        query.edit_message_text("Morning or evening?", reply_markup=reply_markup)

    elif 'AM_' in query.data:
        car_and_date = '-' + str(query.data).split('_')[1]
        context.user_data['choice'] = 'time'
        return TYPING_REPLY


# Show a list of available commands to the user
def help(update, context):
    update.message.reply_text(
        "Dit is de Call-a-car bot\n"
        "Bruikbare commando's zijn:\n "
        "/start\n"
        "/help\n"
        "/info\n"
        "/account"
    )


def register(update, context):
    chat_id = update.message.chat.id
    result = DbHandler.check_user(chat_id)
    if not result:
        DbHandler.create_new_user(chat_id, 'a', 'a')
        update.message.reply_text("You have been registered")
    else:
        update.message.reply_text("You are already registered")


def user_register(update, context):
    print("a")


def check_and_or_create_db(update, context):
    DbHandler.check_if_db_exsists()

def reserve_car(update, context):
    chat_id = update.message.chat.id
    result = DbHandler.check_user(chat_id)
    if not result:
        update.message.reply_text("Please register yourself with /register to start using this bot")
    else:
        keyboard = [[InlineKeyboardButton("Regular cars", callback_data='normal_cars'),
                     InlineKeyboardButton("Cars with special needs", callback_data='special_cars')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('What kind of car would you like to reserve', reply_markup=reply_markup)

def reservation_time(update, context):
    update.message.reply_text("Geeft een tijd op")
    return TYPING_REPLY


def reservation_place(update, context):
    update.message.reply_text("Geeft een adres op")
    return TYPING_REPLY


def done():
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    # logger.exception('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':
    main()
