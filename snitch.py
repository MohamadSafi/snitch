import telebot
from telebot.types import InputMediaPhoto
from sys import argv
from log import logger
from db import *
from snitch_exceptions import *

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
def send_welcome(message):
    msg = "Hey, I'm a snitch 🤫, And I'll send you every profile photo your target has, What do you think about that! cool ha?"
    tb.send_message(message.chat.id, msg)
    logger.debug(f"welcome message sent to {message.from_user.username}") 

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
        logger.debug(f"Got id {target_id} for target name`{target_username}`")
        commit_target(spyer_id, target_id, target_username, target_first_name)
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
