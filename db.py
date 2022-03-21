import sqlite3
import os
from log import logger

DB_PATH = "snitch.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    with open("create_database.sql","r") as fd:
        try:
            cur.executescript(fd.read())
        except Exception as e:
            logger.error(f"Creating tables, {e}")
    conn.commit()
    conn.close()

def commit_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (user_id, username, first_name)
    query = "INSERT OR REPLACE INTO Users (user_id, username, first_name) VALUES (?,?,?);"
    try:
        cur.execute(query, data)
    except Exception as e:
        logger.error(f"Commiting user {user_id}, {e}")
    conn.commit()
    conn.close()

def commit_target(target_id, username, first_name, last_name, last_seen, bio, status,phone_number,spyer_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (target_id, username, first_name, last_name, last_seen, bio, status,phone_number,spyer_id)
    query = "INSERT OR REPLACE INTO Targets (target_id, username, first_name, last_name, last_seen, bio, status,phone_number,spyer_id) VALUES (?,?,?,?,?,?,?,?,?);"
    try:
        cur.execute(query, data)
    except Exception as e:
        logger.error(f"Commitng target {target_id}, {e}")

    conn.commit()
    conn.close()

def commit_photo(photo_id, photo_uniq_id, photo_url, owner_id ):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (photo_id, photo_uniq_id, photo_url, owner_id)
    query = "INSERT OR REPLACE INTO Photos (photo_id, photo_uniq_id, photo_url, owner_id) VALUES (?,?,?,?);"
    try:
        cur.execute(query,data)
    except Exception as e:
        logger.error(f"Commitng target {target_id} photo, {e}")

    conn.commit()
    conn.close()

def fetch_targets(spyer_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (spyer_id,)
    query = "SELECT * FROM Targets WHERE spyer_id = ?;"
    try:
        cur.execute(query, data)
    except Exception as e:
        logger.error(f"fetching targets of user {spyer_id}, {e}")


    rows = cur.fetchall()
    res = []
    for row in rows:
        target = {}
        target["target_id"] = row[0]
        target["username"] = row[1]
        target["first_name"] = row[2]
        target["last_name"] = row[3]
        target["last_seen"] = row[4]
        target["bio"] = row[5]
        target["status"] = row[6]
        target["phone_number"] = row[7]
        target["spyer_id"] = row[8]
        res.append(target)

    conn.close()
    return res

def fetch_photos(owner_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (owner_id,)
    query = "SELECT *  FROM Photos WHERE owner_id = ?;"
    try:
        cur.execute(query, data)
    except Exception as e:
        logger.error(f"Fetching target {target_id} photos, {e}")


    rows = cur.fetchall()
    res = []
    for row in rows:
        photo = {}
        photo["photo_id"] = row[0]
        photo["photo_uniq_id"] = row[1]
        photo["photo_url"] = row[2]
        photo["owner_id"] = row[3]
        res.append(photo)

    conn.close()
    return res















