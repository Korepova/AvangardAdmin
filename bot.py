from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = ''
# CHANNEL_ID = '-1002542161157' # admin chat
CHANNEL_ID = '-1002115530256' # Avangard chat

ALLOWED_USERS = [
    178448316, # Dasha
    393374272, # Alena admin
    293592224  # Alena Yar
]

def check_access(update: Update):
    """Проверяет, разрешено ли пользователю обращаться к боту"""
    user_id = update.effective_user.id
    return user_id in ALLOWED_USERS

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        await update.message.reply_text("Привет! Я бот для управления лучшей на свете группой - КП Авангард." \
        " Упс, доступ к моим командам доступен ограниченному кругу лиц, к сожалению, Вы в этот круг не входите :(")
        return
    await update.message.reply_text("Привет, админ! Приятного управления каналом :)")

# /sendmessage <text>
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        await update.message.reply_text("Доступ запрещён")
        return

    message_text = ' '.join(context.args)

    if not message_text.strip():
        await update.message.reply_text('Используйте команду /send <текст>')
        return

    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=message_text)
        await update.message.reply_text(f"Сообщение отправлено успешно!")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

# /remove <user_id>
async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        await update.message.reply_text("Доступ запрещён")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text('Укажите правильный user_id!')
        return

    user_id = int(context.args[0])

    try:
        await context.bot.ban_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        await update.message.reply_text(f"Участник с ID {user_id} удалён из канала.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

# /help
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        await update.message.reply_text("Привет! Я бот для управления лучшей на свете группой - КП Авангард." \
        " Упс, доступ к моим командам доступен ограниченному кругу лиц, к сожалению, Вы в этот круг не входите :(")
        return

    help_text = """

Девчонки, напоминаю:

- 📌 **Отправка сообщений:**
/send <текст> - для отправки ругательств в канал.

- ⚠️ **Удаление участников:**
/remove <user_id> - тут нужен именно id. Чтобы узнать id пользователя, воспользуйтесь ботом @UserInfoBot:
1. Перешлите боту любое сообщение нарушителя
2. получите ID пользователя в ответном сообщении.
3. Вернитесь сюда и напишите команду "/remove <полученный_id>"

- 📄 **Информация о возможностях:**
/help - отображает это сообщение.
"""
    await update.message.reply_text(help_text)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("send", send_message))
    application.add_handler(CommandHandler("remove", remove_user))
    application.add_handler(CommandHandler("help", show_help))

    print("Bot is running...")
    application.run_polling()
