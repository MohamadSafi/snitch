import telebot
import sys

from telebot.types import InputMediaPhoto
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from threading import Thread

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
    msg = """Let me help you a little 🤖
1️⃣First if you don't have any targets to track them
Add some ... it's easy just forward me a message
from him/her and I will start tracking 😉
-_-_-_-_-_-_-_-_-_-_-_-_-
2️⃣Now after adding your targets, You will be notified
every time they update their profile photo 
You can view all of your targets
by pressing on 'View your targets' button 💁🏻‍♂️
You will see a list of your targets just chose one 👀
-_-_-_-_-_-_-_-_-_-_-_-_-
3️⃣Next you will see three options :
⚙️'Target's data' will send you back all the data available
on your target (user id , username , name, ....)
🖼'Profile phtos' will send you back all the profile
photos your target ever had
❌'Delete' will remove the user from your target list
-_-_-_-_-_-_-_-_-_-_-_-_-
4️⃣That's it .... but for the best experience use
the '/start' command every time you want to
check on something 👍🏻"""
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
    msg = "Hey, I'm a snitch 🤫, I will track your targets 24/7 👁"
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


def notify_spyers(target_id, msg):
    pass


def get_target_uniq_photos(target_id):
    uniq_photos = []
    photos = tb.get_user_profile_photos(target_id)
    for photo in photos:
        photo_id = photo[0].file_id
        photo_uniq_id = photo[0].file_unique_id
        if is_uniq_photo(photo_uniq_id):
            logger.debug(
                f"Unique photo has been detected for user {target_id}")
            uniq_photos.append(photo_id)
            commit_photos(photo_id, photo_uniq_id, target_id)
            logger.debug(f"Commited Photo {photo_id} to db")

    return uniq_photos


def listen_for_targets_changes():
    targets = fetchall_targets()
    for target in targets:
        target_id = target["target_id"]
        uniq_photos = get_target_uniq_photos(target_id)
        if uniq_photos:
            msg = f"{Target <Name: {target['first_name']} {target['last_name']}, Username: target['username']> Has New Photos}"
            notify_spyers(target_id, msg)
            logger.debug(f"Notified spyers of target {target_id}")


def main():
    create_tables()
    listener_thread = Thread(target = listen_for_targets_changes, args = ())
    listener_thread.start()
    logger.debug("Listener Thread has been started")
    tb.infinity_polling(interval=0, timeout=0)
    return True


if __name__ == "__main__":
    main()
