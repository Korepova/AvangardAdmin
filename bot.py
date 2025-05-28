from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = ''

# Каналы:
AVANGARD_CHANNEL_ID = '-1002115530256'  # Канал Avangard с темами
ADMIN_CHANNEL_ID = '-1002542161157'     # Канал Admin (используется в режиме Debug)

ALLOWED_USERS = [
    178448316,  # Dasha
    393374272,  # Alena admin
    293592224   # Alena Yar
]

def check_access(update: Update):
    """Проверяет, разрешено ли пользователю обращаться к боту"""
    user_id = update.effective_user.id
    return user_id in ALLOWED_USERS

# Валидные идентификаторы тем (только для канала Avangard)
VALID_TOPICS = {
    1: "Общая болталка",
    2: "ЧП/SOS/АСАП/HELP",
    563: "Сад и огород",
    2938: "Ремонт дороги",
    6: "Любимые питомцы",
    18: "Реклама услуг/товаров",
    8484: "Попутчики",
    13115: "Спорт",
    11: "Полезные контакты",
    53: "Адреса соседей",
    17081: "Вода и ее качество",
    26677: "Детская площадка",
    14: "Обсуждение откачки септиков"
}

# Хранение текущего состояния беседы (текста сообщения)
current_messages = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        await update.message.reply_text("Привет! Я бот для управления лучшей на свете группой - КП Авангард."
                                       "\n Упс, доступ к моим командам доступен ограниченному кругу лиц,"
                                       "\n к сожалению, Вы в этот круг не входите :(")
        return
    await update.message.reply_text("Привет, админ! Приятного управления каналом :)")

# /send
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        await update.message.reply_text("Доступ запрещён")
        return

    args = context.args
    if len(args) == 0:
        await update.message.reply_text('Используйте команду /send <текст>')
        return

    # Проверяем наличие режима DEBUG
    use_debug = False
    if args[-1].lower() == 'debug':
        use_debug = True
        args = args[:-1]  # Отсекаем последнее слово ('debug')

    # Собираем текст сообщения
    message_text = ' '.join(args)

    # Сохраняем состояние (текст сообщения)
    current_messages.update({update.effective_user.id: message_text})

    # Устанавливаем целевой канал в зависимости от режима
    dest_channel = ADMIN_CHANNEL_ID if use_debug else AVANGARD_CHANNEL_ID

    # Если канал Avangard, предлагаем выбрать тему
    if dest_channel == AVANGARD_CHANNEL_ID:
        # Генерируем клавиатуру выбора темы
        keyboard_buttons = []
        for tid, tname in VALID_TOPICS.items():
            button = InlineKeyboardButton(tname, callback_data=f'send_{tid}')
            keyboard_buttons.append([button])
        reply_markup = InlineKeyboardMarkup(keyboard_buttons)
        await update.message.reply_text("Выберите тему:", reply_markup=reply_markup)
    else:
        # Если канал Admin, отправляем сообщение напрямую
        try:
            await context.bot.send_message(chat_id=ADMIN_CHANNEL_ID, text=message_text)
            await update.message.reply_text(f"Сообщение отправлено в канал Admin.")
        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка: {e}")

# Обработчик выбора темы (только для канала Avangard)
async def handle_topic_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Получаем выбранную тему
    selected_topic_id = int(query.data.split('_')[1])

    # Достаем информацию о сообщении
    message_text = current_messages.pop(query.from_user.id, "")
    if not message_text:
        await query.edit_message_text(text="Сообщение потерялось. Повторите попытку.")
        return

    try:
        # Отправляем сообщение в выбранную тему
        await context.bot.send_message(chat_id=AVANGARD_CHANNEL_ID, text=message_text, message_thread_id=int(selected_topic_id))
        await query.edit_message_text(text=f"Сообщение отправлено в тему \"{VALID_TOPICS[int(selected_topic_id)]}\"!")
    except Exception as e:
        await query.edit_message_text(text=f"Произошла ошибка: {e}")

# /warn
async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        await update.message.reply_text("Доступ запрещён")
        return

    args = context.args
    if len(args) < 1:
        await update.message.reply_text('Используйте команду /warn <username>')
        return

    # Проверяем наличие режима DEBUG
    use_debug = False
    if args[-1].lower() == 'debug':
        use_debug = True
        args = args[:-1]  # Отсекаем последнее слово ('debug')

    username = args[0].strip('@')

    warning_message = f"""
        ✨ **Внимание, @{username}!**

        Вам выдано предупреждение за нарушение правил сообщества.
        Повторное нарушение приведет к Вашему удалению из группы.
        """

    # Устанавливаем целевой канал в зависимости от режима
    dest_channel = ADMIN_CHANNEL_ID if use_debug else AVANGARD_CHANNEL_ID

    # Генерируем клавиатуру выбора темы (только для Avangard)
    try:
        await context.bot.send_message(chat_id=dest_channel, text=warning_message)
        await update.message.reply_text(f"✅ Предупреждение отправлено пользователю @{username} в канал админов.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

# /remove <user_id>
async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        await update.message.reply_text("Доступ запрещён")
        return

    args = context.args
    if len(args) < 1 or not context.args[0].isdigit():
        await update.message.reply_text('Используйте команду /remove <user_id>')
        return

    # Проверяем наличие режима DEBUG
    use_debug = False
    if args[-1].lower() == 'debug':
        use_debug = True
        args = args[:-1]  # Отсекаем последнее слово ('debug')

    user_id = int(args[0])

    # Устанавливаем целевой канал в зависимости от режима
    dest_channel = ADMIN_CHANNEL_ID if use_debug else AVANGARD_CHANNEL_ID

    try:
        await context.bot.ban_chat_member(chat_id=dest_channel, user_id=user_id)
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

Админы, напоминаю:

- 📌 **Отправка сообщений:**
/send <текст> - для отправки сообщений в канал Авангард. Бот предложит выбрать тему, куда отправить текст.\n
/send <текст> debug - тренируемся на жен.совете.

- ⚠️ **Предупреждение пользователей:**
/warn <username> - для выдачи предупреждения пользователю в канал Авангард, в общую болталку.\n
/warn <username> debug - тренируемся на жен.совете.

- ⚠️ **Удаление участников:**
/remove <user_id> - для исключения пользователя из канала Авангард.\n
/remove <user_id> debug - тренируемся на жен.совете.

- 📄 **Информация о возможностях:**
/help - отображает это сообщение.
"""
    await update.message.reply_text(help_text)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("send", send_message))
    application.add_handler(CommandHandler("warn", warn_user))
    application.add_handler(CommandHandler("remove", remove_user))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(CallbackQueryHandler(handle_topic_selection, pattern=r'^send'))

    print("Bot is running...")
    application.run_polling()
