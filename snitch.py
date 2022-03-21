import telebot
from telebot.types import InputMediaPhoto
from sys import argv
from log import logger
from db import *
from snitch_exceptions import *
from telebot.types import InlineKeyboardButton , InlineKeyboardMarkup

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


def send_error(message, error):
    msg = f"**{error}**"
    tb.send_message(message.chat.id, msg, parse_mode="markdown")
    logger.warning(error)


@tb.message_handler(commands=["start"])
def start(message):

    Markup = InlineKeyboardMarkup()
    Markup.row_width = 3
    msg = "Hey, I'm a snitch 🤫, And I'll send you every profile photo your target has, What do you think about that! cool ha?"
    btn1_text = "View your targets"
    btn2_text = "Help !!"
    btn1 = InlineKeyboardButton(btn1_text, callback_data = f"{message.chat.id}@{message.from_user.id}#{'targets'}")
    btn2 = InlineKeyboardButton(btn2_text, callback_data = f"{message.chat.id}@NULL#{'help'}")
    Markup.add(btn1,btn2)
    tb.send_message(message.chat.id, msg, reply_markup = Markup)
    logger.debug(f"Starting message has been sent to user {message.from_user.id}") 

@tb.callback_query_handler(func=lambda call: True)
def handle_query(call):
    data, cmd = call.data.split('#')
    data = data.split('@')
    data_len = len(data)
    id1 = data[0]
    id2 = data[1] if data_len > 1 else None
    id3 = data[2] if data_len > 2 else None

    if cmd == "targets":
        targets_menu(int(id2),int(id1))
    elif cmd == "help":
        help(int(id1))
    elif cmd == "target":
        target_menu(id1, id2, id3)
    elif cmd == "show_data":
        send_target_data(id1, id2)
    elif cmd == "show_photos":
        send_target_photos(id1 ,id2)
    elif cmd == "delete":
        send_delete_target(id1, id3, id2)

def send_target_data(chat_id,target_id):
    data = fetch_target_data(target_id)
    msg = f"ID: {data['target_id']}\nUsername: {data['username']}\nName: {data['first_name']} {data['last_name']}"
    tb.send_message(chat_id, msg)

def send_target_photos(target_id):
    pass

def send_delete_target(chat_id, spyer_id,target_id):
    delete_target(spyer_id, target_id)
    msg = "Target has been deleted"
    tb.send_message(chat_id, msg)

def target_menu(chat_id,target_id,spyer_id):
    Markup = InlineKeyboardMarkup()
    Markup.row_width = 3
    data_btn_text = "Target's data"
    photos_btn_text = "Profile photos"
    delete_btn_text = "Delete"
    data_btn = InlineKeyboardButton(data_btn_text, callback_data = f"{chat_id}@{target_id}@NULL#show_data")
    photos_btn = InlineKeyboardButton(photos_btn_text, callback_data = f"{chat_id}@{target_id}@NULL#show_photos")
    delete_btn = InlineKeyboardButton(delete_btn_text, callback_data = f"{chat_id}@{target_id}@{spyer_id}#delete")
    Markup.add(data_btn, photos_btn, delete_btn)
    tb.send_message(chat_id,"Choose an option", reply_markup = Markup)

def help(chat_id):
    msg = "explain how this bot work"
    tb.send_message(chat_id, msg)

def targets_menu(user_id,chat_id):
    if fetch_targets(user_id):
        
        Markup = InlineKeyboardMarkup()
        Markup.row_width = 3
        targets = fetch_targets(user_id) 
        
        for target in targets:
            text = f"{target['first_name']} {target['last_name']}"
            btn = InlineKeyboardButton(text, callback_data =f"{chat_id}@{target['target_id']}@{user_id}#target")
            Markup.add(btn)
        msg = "This is your targets list click on any of them to view details 🕵🏻"
        tb.send_message(chat_id, msg, reply_markup = Markup)
        logger.debug(f"Target menu has been sent to user {user_id}") 
    
    else:
        msg = "You don't have any targets\nplease forward a message from your target"
        tb.send_message(chat_id, msg)
        logger.debug(f"Instruction message {user_id}") 



@tb.message_handler()
def send_photo(message):
    if not is_forwarded_msg(message):
        send_error(message,
                   "Please forward a message from the user you want to track")
        logger.warning(f"Message forwarded from {message.forward_from} is not valid")
        return

    try:
        spyer_id = message.from_user.id
        spyer_username = message.from_user.username
        spyer_first_name = message.from_user.first_name
        commit_user(spyer_id, spyer_username, spyer_first_name)
        logger.info(f"Added user {spyer_id} to db")

        if not message.forward_from:
            raise PrivateUserError

        target_username = message.forward_from.username
        if not target_username:
            target_username = "Not Available"
        target_id = message.forward_from.id
        target_first_name = message.forward_from.first_name
        target_last_name = message.forward_from.last_name
        logger.debug(f"Got id {target_id} for target")
        commit_target(spyer_id, target_id, target_username, target_first_name, target_last_name)
        logger.info(f"Added target {target_id} to db")

        user_profile_photos = tb.get_user_profile_photos(target_id)
        logger.debug("Got user profile photos")
         
        photos = user_profile_photos.photos
        for photo in photos:
            photo=photo[0]
            commit_photo(str(photo.file_id), str(photo.file_unique_id), "Null", target_id )
        media = [
            InputMediaPhoto(photo[0].file_id, f"{index}")
            for index, photo in enumerate(photos)
        ]
        logger.debug("Created media group")

        if len(media) < 1:
            logger.error("No photos to be sent")
            return

        groups_list = []
        media_group = []
        media_len = len(media)
        for index, media_photo in enumerate(media):
            media_group.append(media_photo)
            if index % 10 == 0 and index != 0:
                groups_list.append(media_group)
                media_group = []
            if index == media_len - 1 and media_group:
                groups_list.append(media_group)

        for group in groups_list:
            tb.send_media_group(message.chat.id, group)
            logger.debug("Sent Media Group")

    except PrivateUserError:
        send_error(message, "Can't access this user, It is a private user")
        logger.error("Message forwarded from a private user")
        return

    except Exception as e:
        raise


if __name__ == "__main__":
    create_tables()
#    tb.polling()
    tb.infinity_polling(interval = 0, timeout = 0)
