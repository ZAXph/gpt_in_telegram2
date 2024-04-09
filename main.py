from config import *
from repository import DATABASE
from gpt import GPT
from transformers import AutoTokenizer

table = DATABASE()
gpt = GPT()
bot = TeleBot(TOKEN)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)

table.create_table()


def check_commands(message):
    return "/" in message.text.lower()


@bot.message_handler(commands=['start'])
def send_logs(message):
    bot.send_message(chat_id=message.chat.id, text="...")


@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(commands=["solve_task"])
def mode_gpt(message):
    markup = markup_create(modes)
    msg = bot.send_message(chat_id=message.chat.id, text="Выберите режим работы", reply_markup=markup)
    bot.register_next_step_handler(msg, lvl_gpt)


def lvl_gpt(message):
    if message.text not in modes:
        bot.send_message(chat_id=message.chat.id, text="Вы не нажали на кнопку. Попробуйте снова!")
        bot.register_next_step_handler(message, mode_gpt)
    result = table.get_data("user_id", message.from_user.id)
    if (message.from_user.id,) not in result:
        table.add_data(message.from_user.id, modes[message.text])
        logging.info("Пользователь добавлен в базу данных")
    else:
        table.update_data(message.from_user.id, "subject", modes[message.text])
    markup = markup_create(levels)
    msg = bot.send_message(chat_id=message.chat.id, text="Выберите уровень ответа", reply_markup=markup)
    bot.register_next_step_handler(msg, task_user)


def lvl_gpt_error(message):
    msg = bot.send_message(chat_id=message.chat.id, text="Выберите уровень ответа")
    bot.register_next_step_handler(msg, task_user)


def task_user(message):
    if message.text not in levels:
        bot.send_message(chat_id=message.chat.id, text="Вы не нажали на кнопку. Попробуйте снова!")
        bot.register_next_step_handler(message, lvl_gpt_error)
    table.update_data(message.from_user.id, "level", levels[message.text])
    msg = bot.send_message(chat_id=message.chat.id, text="Введите свой запрос", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, response_processing)


def task_user_error(message):
    msg = bot.send_message(chat_id=message.chat.id, text="Введите свой запрос")
    bot.register_next_step_handler(msg, response_processing)


def response_processing(message):
    if "/" in message.text:
        bot.send_message(chat_id=message.chat.id, text="Вы не нажали на кнопку. Попробуйте снова!")
        bot.register_next_step_handler(message, task_user_error)
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")  # название модели
    tokens = tokenizer.encode(message.text)
    if len(tokens) < MAX_TOKEN:
        result = table.get_data("*", message.from_user.id)
        resp = gpt.gpt_processing(message.text, result[0][3], result[0][2])
        if resp.status_code == 200 and 'choices' in resp.json():
            logging.info("Запрос прошел успешно")
            table.update_data(message.from_user.id, "answer", resp.json()['choices'][0]['message']['content'])
            bot.send_message(chat_id=message.chat.id, text=resp.json()['choices'][0]['message']['content'])
            markup = markup_inline()
            bot.send_message(chat_id=message.chat.id, text="Нажми: 'Продолжить' для продолжения объяснения.", reply_markup=markup)

        else:
            logging.warning("Ошибка от GPT")
            bot.send_message(chat_id=message.chat.id, text=resp.json())


@bot.callback_query_handler(func=lambda call: call.data == 'next_gpt')
def send_text_next(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    result = table.get_data("*", call.from_user.id)
    resp = gpt.gpt_processing_next(result[0][-1], result[0][3], result[0][2])
    if resp.status_code == 200 and 'choices' in resp.json():
        logging.info("Запрос прошел успешно")
        table.update_data(call.from_user.id, "answer",
                          result[0][-1] + " " + resp.json()['choices'][0]['message']['content'])
        bot.send_message(chat_id=call.message.chat.id, text=resp.json()['choices'][0]['message']['content'])
        markup = markup_inline()
        bot.send_message(chat_id=call.message.chat.id, text="Нажми: 'Продолжить' для продолжения объяснения.", reply_markup=markup)

    else:
        logging.warning("Ошибка от GPT")
        bot.send_message(chat_id=call.message.chat.id, text=resp.json())


@bot.message_handler(func=check_commands)
def check_commands(message):
    logging.info("Пользователь ввел неизвестную команду")
    bot.send_message(chat_id=message.chat.id, text="Данных команд не существует")


@bot.message_handler(content_types=["video", "audio", "voice", "photo", "text"])
def send_not_text(message):
    logging.warning("Пользователь не отправил текст")
    bot.send_message(chat_id=message.chat.id, text="Бот не работает ни с чем, кроме текста")


bot.polling()
