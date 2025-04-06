from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext


user_data = {}

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Привет! Я калькулятор CO₂ выбросов от автомобиля. 🚗\n",
        reply_markup=ReplyKeyboardMarkup([['Пройти опрос', "Статистика"]], one_time_keyboard=True)
    )
    return 0

def stats(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Интересная статистика')
    return ConversationHandler.END


def survey(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Бензин', 'Дизель']]
    update.message.reply_text(
        
        "Сначала выбери тип топлива:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return 1

def fuel_type(update: Update, context: CallbackContext) -> int:
    user_data['fuel_type'] = update.message.text.lower()
    update.message.reply_text("Теперь введи расход топлива в л/100 км (например: 7.5):")
    return 2

def fuel_consumption(update: Update, context: CallbackContext) -> int:
    try:
        user_data['fuel_consumption'] = float(update.message.text)
    except ValueError:
        update.message.reply_text("Пожалуйста, введи число. Пример: 6.3")
        return 2

    update.message.reply_text("Сколько дней в неделю ты обычно используешь автомобиль? (например: 3)")
    return 3

def ask_days_per_week(update: Update, context: CallbackContext) -> int:
    try:
        context.user_data['days_per_week'] = int(update.message.text)
    except ValueError:
        update.message.reply_text("Пожалуйста, введи число. Например: 4")
        return 3
    update.message.reply_text("Сколько километров ты обычно проезжаешь в день, когда пользуешься машиной?")
    return 4 

def ask_km_per_day(update: Update, context: CallbackContext) -> int:
    try:
        context.user_data['days_per_week'] = int(update.message.text)
    except ValueError:
        update.message.reply_text("Пожалуйста, введи число. Например: 4")
        return 4

    fuel_type = context.user_data['fuel_type']
    fuel_consumption = context.user_data['fuel_consumption']
    days_per_week = context.user_data['days_per_week']
    km_per_day = context.user_data['km_per_day']


    coef = 2.31 if fuel_type == 'бензин' else 2.68    #сколько CO2 выбрасывает автомобиль за литр
    co2 = (fuel_consumption / 100) * (days_per_week * 4 * km_per_day) * coef    #литров на 100 км / 100 --> литров на 1 км  * километров в месяц (дней в неделе * 4 недели * км в день) * CO2 за литр 

    update.message.reply_text(
        f"🌱 По твоему обычному режиму ты выбрасываешь примерно:\n"
        f"💨 *{co2:.2f} кг CO₂ в месяц*.",
        parse_mode='Markdown'
    )

    context.user_data.clear()
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Окей, пока! 👋')
    return ConversationHandler.END

def main():
    updater = Updater("", use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        0: {
            [MessageHandler(Filters.regex('^Пройти опрос$'), survey)]
            [MessageHandler(Filters.regex('^Статистика$'), stats)]
            },
        1: [MessageHandler(Filters.regex('^(Бензин|Дизель)$'), fuel_type)],
        2: [MessageHandler(Filters.text & ~Filters.command, fuel_consumption)],
        3: [MessageHandler(Filters.text & ~Filters.command, ask_days_per_week)],
        4: [MessageHandler(Filters.text & ~Filters.command, ask_km_per_day)],

    },
    fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

    

if __name__ == '__main__':
    main()
