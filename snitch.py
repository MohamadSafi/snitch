import telebot
from telebot.types import InputMediaPhoto
import logging
from sys import argv

if len(argv) > 1:
    TOKEN = argv[1]
else:
    print("Please provide your bot token")
    exit(1)

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


@tb.message_handler()
def send_photo(message):
    if not is_forwarded_msg(message):
        send_error(message,
                   "Please forward a message from the user you want to track")
        return

    try:
        username = message.forward_from.username
        user_id = message.forward_from.id
        logger.debug(f"Got id {user_id} for user {username}")

        user_profile_photos = tb.get_user_profile_photos(user_id)
        logger.debug("Got user profile photos")

        photos = user_profile_photos.photos
        media = [
            InputMediaPhoto(photo[0].file_id, f"{index}")
            for index, photo in enumerate(photos)
        ]
        logger.debug("Created media group")

        tb.send_media_group(message.chat.id, media)
        logger.debug("Sent ")

    except AttributeError:
        send_error(message, "Can't access this user, It is a private user")
        return

    except Exception as e:
        raise


tb.polling()
