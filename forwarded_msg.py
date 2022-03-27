#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db import *
from log import logger


class ForwardedMessage:

    def __init__(self, tb, msg):
        self.tb = tb
        self.message = msg
        self.text = msg.text
        self.from_user = msg.from_user
        self.forward_date = msg.forward_date
        self.forward_from = msg.forward_from
        self.id = msg.id
        self.message_id = msg.message_id
        self.chat = msg.chat

    def from_private_user(self):
        if not self.forward_from:
            return True
        return False

    def is_forwarded(self):
        if self.forward_date:
            return True
        else:
            return False

    def commit_user(self):
        user_id = self.from_user.id
        username = self.from_user.username
        first_name = self.from_user.first_name

        commit_user(user_id, username, first_name)
        logger.info(f"Added user {user_id} to db")

    def commit_target(self):
        target_username = self.forward_from.username
        if not target_username:
            target_username = " "

        spyer_id = self.from_user.id
        target_id = self.forward_from.id
        target_first_name = self.forward_from.first_name
        target_last_name = self.forward_from.last_name
        if not target_last_name:
            target_last_name = " "

        commit_target(spyer_id, target_id, target_username, target_first_name,
                      target_last_name)
        logger.info(f"Added target {target_id} to db")

    def commit_photos(self):
        photos = self.get_photos()
        owner_id = self.forward_from.id
        for index, photo in enumerate(photos):
            photo_id = photo[0].file_id
            photo_uniq_id = photo[0].file_unique_id
            commit_photo(photo_id, photo_uniq_id, owner_id)
            logger.debug(f"Commited Photo {photo_id} to db")

    def get_photos(self):
        owner_id = int(self.forward_from.id)
        UserProfilePhotos = self.tb.get_user_profile_photos(owner_id)
        photos = UserProfilePhotos.photos
        logger.debug("Got user profile photos")

        return photos
