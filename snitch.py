import telebot
from telebot.types import InputMediaPhoto
from sys import argv
from log import logger
from db import *
from snitch_exceptions import *
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

if len(argv) > 1:
    TOKEN = argv[1]
else:
    print("Please provide your bot token")
    exit(1)

tb = telebot.TeleBot(TOKEN)


def is_forwarded_msg(message):
    if message.forward_date:
        return True
    else:
        return False


def is_from_private_user(message):
    if message.forward_from:
        return False
    return True


def send_error(message, error):
    msg = f"**{error}**"
    tb.send_message(message.chat.id, msg, parse_mode="markdown")
    logger.warning(error)


def send_msg(message, text):
    tb.send_message(message.chat.id, text, parse_mode="markdown")
    logger.info(
        f"Send a message to user {message.from_user.id}, message = {text}")


@tb.message_handler(commands=["start"])
def start(message):

    Markup = InlineKeyboardMarkup()
    Markup.row_width = 3
    msg = "Hey, I'm a snitch 🤫, And I'll send you every profile photo your target has, What do you think about that! cool ha?"

    targets_btn_text = "View your targets"
    help_btn_text = "Help !!"
    targets_btn = InlineKeyboardButton(
        targets_btn_text,
        callback_data=f"{message.chat.id}@{message.from_user.id}#{'targets'}")
    help_btn = InlineKeyboardButton(
        help_btn_text, callback_data=f"{message.chat.id}@NULL#{'help'}")
    Markup.add(targets_btn, help_btn)
    tb.send_message(message.chat.id, msg, reply_markup=Markup)
    logger.debug(
        f"Starting message has been sent to user {message.from_user.id}")


@tb.callback_query_handler(func=lambda call: True)
def handle_query(call):
    data, cmd = call.data.split('#')
    data = data.split('@')
    data_len = len(data)
    id1 = data[0]
    id2 = data[1] if data_len > 1 else None
    id3 = data[2] if data_len > 2 else None

    if cmd == "targets":
        targets_menu(int(id2), int(id1))
    elif cmd == "help":
        help(int(id1))
    elif cmd == "target":
        target_menu(id1, id2, id3)
    elif cmd == "show_data":
        send_target_data(id1, id2)
    elif cmd == "show_photos":
        send_target_photos(id1, id2)
    elif cmd == "delete":
        send_delete_target(id1, id3, id2)


def send_target_data(chat_id, target_id):
    data = fetch_target_data(target_id)
    msg = f"ID: {data.get('target_id')}\nUsername: {data.get('username')}\nName: {data.get('first_name')} {data.get('last_name')}"
    tb.send_message(chat_id, msg)


def send_target_photos(chat_id, target_id):
    photos = fetch_photos(target_id)
    media_group = create_media_group(photos)

    try:
        if len(media_group) < 1: raise NoProfilePhotosError
        send_media_groups_list(chat_id, media_group)

    except NoProfilePhotosError:
        errmsg = "No profile photos available"
        tb.send_message(chat_id, errmsg)
        return


def send_delete_target(chat_id, spyer_id, target_id):
    delete_target(spyer_id, target_id)
    msg = "Target has been deleted"
    tb.send_message(chat_id, msg)


def target_menu(chat_id, target_id, spyer_id):
    Markup = InlineKeyboardMarkup()
    Markup.row_width = 3
    data_btn_text = "Target's data"
    photos_btn_text = "Profile photos"
    delete_btn_text = "Delete"
    data_btn = InlineKeyboardButton(
        data_btn_text, callback_data=f"{chat_id}@{target_id}@NULL#show_data")
    photos_btn = InlineKeyboardButton(
        photos_btn_text,
        callback_data=f"{chat_id}@{target_id}@NULL#show_photos")
    delete_btn = InlineKeyboardButton(
        delete_btn_text,
        callback_data=f"{chat_id}@{target_id}@{spyer_id}#delete")
    Markup.add(data_btn, photos_btn, delete_btn)
    tb.send_message(chat_id, "Choose an option", reply_markup=Markup)


def help(chat_id):
    msg = "explain how this bot work"
    tb.send_message(chat_id, msg)


def targets_menu(user_id, chat_id):
    if fetch_targets(user_id):

        Markup = InlineKeyboardMarkup()
        Markup.row_width = 3
        targets = fetch_targets(user_id)

        for target in targets:
            text = f"{target['first_name']} {target['last_name']}"
            btn = InlineKeyboardButton(
                text,
                callback_data=
                f"{chat_id}@{target['target_id']}@{user_id}#target")
            Markup.add(btn)
        msg = "This is your targets list click on any of them to view details 🕵🏻"
        tb.send_message(chat_id, msg, reply_markup=Markup)
        logger.debug(f"Target menu has been sent to user {user_id}")

    else:
        msg = "You don't have any targets\nplease forward a message from your target"
        tb.send_message(chat_id, msg)
        logger.debug(f"Instruction message {user_id}")

    logger.debug(f"welcome message sent to {user_id}")


def commit_user_from_message(message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    user_first_name = message.from_user.first_name

    commit_user(user_id, user_username, user_first_name)
    logger.info(f"Added user {user_id} to db")


def commit_target_from_message(message):
    target_username = message.forward_from.username
    if not target_username:
        target_username = " "

    spyer_id = message.from_user.id
    target_id = message.forward_from.id
    target_first_name = message.forward_from.first_name
    target_last_name = message.forward_from.last_name
    if not target_last_name:
        target_last_name = " "

    logger.debug(f"Got id {target_id} for target name`{target_id}`")
    commit_target(spyer_id, target_id, target_username, target_first_name,
                  target_last_name)
    logger.info(f"Added target {target_id} to db")


def commit_photos(photos, owner_id):
    for index, photo in enumerate(photos):
        photo_id = photo[0].file_id
        photo_uniq_id = photo[0].file_unique_id
        commit_photo(photo_id, photo_uniq_id, owner_id)
        logger.debug(f"Commited Photo {photo_id} to db")


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


def get_photos_from_message(message):
    owner_id = int(message.forward_from.id)
    user_profile_photos = tb.get_user_profile_photos(owner_id)
    photos = user_profile_photos.photos
    logger.debug("Got user profile photos")

    return photos


def send_media_groups_list(chat_id, groups):
    for group in groups:
        tb.send_media_group(chat_id, group)
        logger.debug("Sent Media Group")


@tb.message_handler()
def spy(message):
    try:
        # Checking if the message is a forwarded message
        if not is_forwarded_msg(message): raise NotForwardedMessageError

        send_msg(message, "Fetching data, Please wait")
        # Get user from Message and Commit it to db
        commit_user_from_message(message)

        # Get target from Message and Commit it to db
        if is_from_private_user(message): raise PrivateUserError
        commit_target_from_message(message)

        # Get target's photos
        photos = get_photos_from_message(message)

        # Commiting photos to db
        commit_photos(photos, message.forward_from.id)
        send_msg(message, "Target's data and profile photos have been stored")

    except PrivateUserError:
        errmsg = "Can't access this user, It is a private user"
        send_error(message, errmsg)
        return

    except NoProfilePhotosError:
        errmsg = "No profile photos available"
        send_error(message, errmsg)
        return

    except NotForwardedMessageError:
        errmsg = "Please forward a message from the user you want to track"
        send_error(message, errmsg)
        return

    except Exception as e:
        raise


if __name__ == "__main__":
    create_tables()
    tb.infinity_polling(interval=0, timeout=0)
