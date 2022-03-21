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
def send_welcome(message):
    msg = "Hey, I'm a snitch 🤫, And I'll send you every profile photo your target has, What do you think about that! cool ha?"
    tb.send_message(message.chat.id, msg)
    logger.debug(f"welcome message sent to {message.from_user.id}")


def commit_user_from_message(message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    user_first_name = message.from_user.first_name

    commit_user(user_id, user_username, user_first_name)
    logger.info(f"Added user {user_id} to db")


def commit_target_from_message(message):
    target_username = message.forward_from.username
    if not target_username:
        target_username = "Not Available"

    spyer_id = message.from_user.id
    target_id = message.forward_from.id
    target_first_name = message.forward_from.first_name
    logger.debug(f"Got id {target_id} for target name`{target_id}`")
    commit_target(spyer_id, target_id, target_username, target_first_name)
    logger.info(f"Added target {target_id} to db")


def commit_get_media_groups(photos, owner_id):
    groups = []
    media_group = []

    for index, photo in enumerate(photos):
        photo_id = photo[0].file_id
        photo_uniq_id = photo[0].file_unique_id
        commit_photo(photo_id, photo_uniq_id, owner_id)
        logger.debug(f"Commited Photo {photo_id} to db")

        if index % 10 == 0 and index != 0:
            groups.append(media_group)
            media_group = []

        media_group.append(InputMediaPhoto(photo[0].file_id, ""))

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


def send_media_groups_list(groups, message):
    for group in groups:
        tb.send_media_group(message.chat.id, group)
        logger.debug("Sent Media Group")


@tb.message_handler()
def spy(message):
    try:
        send_msg(message, "Fetching data, Please wait")
        # Checking if the message is a forwarded message
        if not is_forwarded_msg(message): raise NotForwardedMessageError

        # Get user from Message and Commit it to db
        commit_user_from_message(message)

        # Get target from Message and Commit it to db
        if is_from_private_user(message): raise PrivateUserError
        commit_target_from_message(message)

        # Get target's photos
        photos = get_photos_from_message(message)

        # Commiting, Sending photos as a media group
        groups = commit_get_media_groups(photos, message.from_user.id)
        if len(groups) < 1: raise NoProfilePhotosError

        send_media_groups_list(groups, message)

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
