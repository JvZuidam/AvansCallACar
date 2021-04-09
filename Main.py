import telegram
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, ConversationHandler, CallbackContext, Filters, MessageHandler, \
    CommandHandler, CallbackQueryHandler

from datetime import date, timedelta

import DbHandler
import telegramcalendar
from Config import *

CAR, DATE, DATE_SELECT, TIME, ADDRESS_FROM, ADDRESS_TO, FINISH, = range(7)
NAME, PHONE_NUMBER = range(2)

bot = telegram.Bot(telegram_bot_token)

def main():
    print("*** Telegram bot is running ***")

    updater = Updater(telegram_bot_token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("cdb", check_and_or_create_db))
    dp.add_handler(CommandHandler("finish", res_finish))
    dp.add_handler(CommandHandler("reservations", get_reservation))

    conv_res_handler = ConversationHandler(
        entry_points=[CommandHandler("reserve", reserve_car)],
        states={CAR: [MessageHandler(Filters.regex('^(Normal cars|Special needs cars)$'), res_car_select)],
                ADDRESS_FROM: [MessageHandler(Filters.text, res_address_from_select)],
                ADDRESS_TO: [MessageHandler(Filters.text, res_address_to_select)],
                TIME: [MessageHandler(Filters.text, res_time_select)],
                DATE: [MessageHandler(Filters.text, res_date_select)],
                DATE_SELECT: [CallbackQueryHandler(inline_handler)]},
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    )

    conv_register_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={PHONE_NUMBER: [MessageHandler(Filters.text, register_phonenumber)]},
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    )

    dp.add_handler(conv_res_handler)
    dp.add_handler(conv_register_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


# Show a list of available commands to the user
def help(update, context):
    update.message.reply_text(
        "This is the Call-a-car bot\n"
        "Usable commands consist of:\n "
        "/help\n"
        "/register\n"
        "/reserve\n"
        "/reservations\n"
        "/account"
    )


def register(update: Update, _: CallbackContext) -> int:
    chat_id = update.message.chat.id
    result = DbHandler.check_user(chat_id)
    if not result:
        update.message.reply_text("Please insert your phone number",
                                  reply_markup=ReplyKeyboardRemove())
        return PHONE_NUMBER
    else:
        update.message.reply_text("You are already registered")


def register_phonenumber(update: Update, _: CallbackContext):
    user = update.message.from_user
    phone_number = update.message.text
    chat_id = update.message.chat.id
    DbHandler.create_new_user(chat_id, user.first_name, phone_number)

def check_and_or_create_db(update, context):
    DbHandler.check_if_user_db_exsists()


def reserve_car(update: Update, _: CallbackContext) -> int:
    reply_keyboard = [['Normal cars', 'Special needs cars']]
    update.message.reply_text(
        "What's the kind of car you need?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return CAR


def res_car_select(update: Update, _: CallbackContext) -> int:
    selected_car = update.message.text
    DbHandler.write_away_reservation(selected_car + "-")
    reply_keyboard = [['Volvo', 'Audi', 'Bmw']]

    update.message.reply_text(
        "Here's a list of cars that are available:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return ADDRESS_FROM


def res_address_from_select(update: Update, _: CallbackContext) -> int:
    DbHandler.write_away_reservation(update.message.text + "-")
    update.message.reply_text("Specify pickup location \n"
                              "Please use this format: {Street} {Building/Apartment} {Postal code} {Town} {Country}",
                              reply_markup=ReplyKeyboardRemove())
    return ADDRESS_TO


def res_address_to_select(update: Update, _: CallbackContext) -> int:
    DbHandler.write_away_reservation(update.message.text + "-")
    update.message.reply_text("Specify droposs location \n"
                              "Please use this format: {Street} {Building/Apartment} {Postal code} {Town} {Country}",
                              reply_markup=ReplyKeyboardRemove())
    return TIME


def res_time_select(update: Update, _: CallbackContext) -> int:
    DbHandler.write_away_reservation(update.message.text + "-")
    reply_keyboard = [['8:00', '9:00', '11:30'], ['13:00', '15:00', '16:00'], ['18:30', '20:30', '21:00']]

    update.message.reply_text(
        "Here's a list of time slots that are available:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return DATE


def res_date_select(update: Update, _: CallbackContext) -> int:
    selected_car = update.message.text
    DbHandler.write_away_reservation(selected_car + "-")

    update.message.reply_text(
        "Choose a date for your reservation:",
        reply_markup=telegramcalendar.create_calendar(),
    )
    return DATE_SELECT


def inline_handler(update: Update, _: CallbackContext):
    selected, date = telegramcalendar.process_calendar_selection(bot, update)

    if selected:
        bot.send_message(chat_id=update.callback_query.from_user.id,
                        text="You selected %s" % (date.strftime("%d/%m/%Y") + "\n" + "To finish your reservation user /finish"),
                        reply_markup=ReplyKeyboardRemove())
    DbHandler.write_away_reservation(date.strftime("%d/%m/%Y") + "-")


def res_finish(update: Update, _: CallbackContext):
    DbHandler.create_new_reservation(update.message.chat.id)
    bot.send_message(update.message.chat.id, "Reservation succesfull to see your reservations use /reservations")


def get_reservation(update: Update, _: CallbackContext):
    user = update.message.from_user
    print(user)
    message_list = DbHandler.get_reservation(update.message.chat.id)
    reservations = ""
    for message in message_list:
        reservations += message + '\n\n'
    bot.send_message(update.message.chat.id, reservations)

def done():
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    # logger.exception('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':
    main()
