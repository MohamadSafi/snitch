import telebot
from telebot.types import InputMediaPhoto

import logging

log_file_path = "snitch.log"
logging.basicConfig(filename=log_file_path,
                    format="%(levelname)s - %(asctime)s - %(message)s",
                    filemode="w")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

tb = telebot.TeleBot(TOKEN)


def is_forwarded_msg(message):
    if not message.forward_sender_name:
        return False
    else:
        return True


def send_error(message, error):
    msg = f"**{error}**"
    tb.send_message(message.chat.id, msg, parse_mode="markdown")
    logger.warning(error)


@tb.message_handler(commands=["start"])
def send_welcome(message):
    msg = "Hey, I'm a snitch 🤫, And I'll send you every profile photo your target has, What do you think about that! cool ha?"
    tb.send_message(message.chat.id, msg)
    logger(f"welcome message sent to {message.from_user.username}")
