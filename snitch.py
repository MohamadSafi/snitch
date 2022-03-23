import telebot
import sys

from telebot.types import InputMediaPhoto
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from forwarded_msg import ForwardedMessage
from error_messages import *
from db import *
from log import logger

if len(sys.argv) > 1:
    TOKEN = sys.argv[1]
else:
    print("Please provide your bot token")
    exit(1)

tb = telebot.TeleBot(TOKEN)


def send_msg(chat_id, text, parse_mode="markdown"):
    tb.send_message(chat_id, text, parse_mode="markdown")
    logger.info(f"Sent a message = {text}")


def send_error(chat_id, error):
    msg = f"**{error}**"
    tb.send_message(chat_id, msg)


def send_help_msg(chat_id):
    msg = "explain how this bot work"
    tb.send_message(chat_id, msg, parse_mode="markdown")


def send_target_data(chat_id, target_id):
    data = fetch_target_data(target_id)
    if data:
        msg = f"ID: {data['target_id']}\nUsername: {data['username']}\nName: {data['first_name']} {data['last_name']}"
    else:
        msg = "No data for this user"

    tb.send_message(chat_id, msg)


def send_target_photos(chat_id, target_id):
    photos = fetch_photos(target_id)
    media_group = create_media_group(photos)

    if len(media_group) < 1: send_error(chat_id, NoProfilePhotosError)
    send_media_groups_list(chat_id, media_group)


def delete_target_send_msg(chat_id, spyer_id, target_id):
    delete_target(spyer_id, target_id)
    msg = "Target has been deleted"
    tb.send_message(chat_id, msg)


def start_menu_markup():

    Markup = InlineKeyboardMarkup()
    Markup.row_width = 3

    targets_btn_text = "View your targets"
    help_btn_text = "Help !!"

    targets_btn = InlineKeyboardButton(targets_btn_text,
                                       callback_data=f"targets")

    help_btn = InlineKeyboardButton(help_btn_text,
                                    callback_data=f"send_help_msg")

    Markup.add(targets_btn, help_btn)

    return Markup


def targets_menu_markup(chat_id, user_id):
    Markup = InlineKeyboardMarkup()
    Markup.row_width = 3
    targets = fetch_targets(user_id)

    if not targets:
        send_error(chat_id, NoTargetsError)
        return None

    for target in targets:
        text = f"{target['first_name']} {target['last_name']}"
        btn = InlineKeyboardButton(
            text, callback_data=f"target#{target['target_id']}")
        Markup.add(btn)

    return Markup


def target_menu_markup(target_id):
    Markup = InlineKeyboardMarkup()
    Markup.row_width = 3

    data_btn_text = "Target's data"
    photos_btn_text = "Profile photos"
    delete_btn_text = "Delete"

    data_btn = InlineKeyboardButton(data_btn_text,
                                    callback_data=f"show_data#{target_id}")

    photos_btn = InlineKeyboardButton(photos_btn_text,
                                      callback_data=f"show_photos#{target_id}")

    delete_btn = InlineKeyboardButton(delete_btn_text,
                                      callback_data=f"delete#{target_id}")

    Markup.add(data_btn, photos_btn, delete_btn)

    return Markup


@tb.callback_query_handler(func=lambda call: True)
def handle_query(call):
    cmd, target_id = call.data.split("#") if "#" in call.data else (call.data,
                                                                    None)
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if cmd == "send_help_msg":
        send_help_msg(chat_id)

    elif cmd == "target":
        markup = target_menu_markup(target_id)
        msg = "Choose an option"
        tb.send_message(chat_id, msg, reply_markup=markup)

    elif cmd == "targets":
        markup = targets_menu_markup(chat_id, user_id)
        if markup:
            msg = "This is your targets list click on any of them to view details 🕵🏻"
            tb.send_message(chat_id, msg, reply_markup=markup)

    elif cmd == "show_data":
        send_target_data(chat_id, target_id)

    elif cmd == "show_photos":
        send_target_photos(chat_id, target_id)

    elif cmd == "delete":
        delete_target_send_msg(chat_id, user_id, target_id)


@tb.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    msg = "Hey, I'm a snitch 🤫, " \
        "And I'll send you every profile photo your target has, " \
        "What do you think about that! cool ha?"

    tb.send_message(message.chat.id, msg, reply_markup=start_menu_markup())
    logger.debug(f"Starting message has been sent to user {user_id}")


def create_media_group(photos):
    groups = []
    media_group = []
    for index, photo in enumerate(photos):
        photo_id = photo["photo_id"]

        if index % 10 == 0 and index != 0:
            groups.append(media_group)
            media_group = []

        media_group.append(InputMediaPhoto(photo_id, ""))

    if media_group:
        groups.append(media_group)

    logger.debug("Created Media groups")
    return groups


def send_media_groups_list(chat_id, groups):
    for group in groups:
        tb.send_media_group(chat_id, group)
        logger.debug("Sent Media Group")


@tb.message_handler()
def spy(message):
    try:
        forwarded_msg = ForwardedMessage(tb, message)
        chat_id = forwarded_msg.chat.id
        if not forwarded_msg.is_forwarded():
            send_error(chat_id, NotForwardedMessageError)
            return

        forwarded_msg.commit_user()

        if forwarded_msg.from_private_user():
            send_error(chat_id, PrivateUserError)
            return

        send_msg(forwarded_msg.chat.id, "Collecting data, Please wait")
        forwarded_msg.commit_target()
        forwarded_msg.commit_photos()
        send_msg(forwarded_msg.chat.id,
                 "Target's data and profile photos have been stored")

    except Exception as e:
        raise


def main():
    create_tables()
    tb.infinity_polling(interval=0, timeout=0)
    return True


if __name__ == "__main__":
    main()
