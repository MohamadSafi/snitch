import sqlite3
import os

DB_PATH = "snitch.db"


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    with open("create_database.sql", "r") as fd:
        cur.executescript(fd.read())
    conn.commit()
    conn.close()


def commit_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (user_id, username, first_name)
    query = "INSERT OR REPLACE INTO Users (user_id, username, first_name) VALUES (?,?,?);"
    cur.execute(query, data)
    conn.commit()
    conn.close()


def commit_target(spyer_id,
                  target_id,
                  username,
                  first_name,
                  last_name=" ",
                  last_seen="Unknown",
                  bio="NULL",
                  status="OFF",
                  phone_number="Not Available"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (target_id, username, first_name, last_name, last_seen, bio, status,
            phone_number, spyer_id)
    query = "INSERT OR REPLACE INTO Targets (target_id, username, first_name, last_name, last_seen, bio, status,phone_number,spyer_id) VALUES (?,?,?,?,?,?,?,?,?);"
    cur.execute(query, data)
    conn.commit()
    conn.close()


def commit_photo(photo_id, photo_uniq_id, owner_id, photo_url="Null"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (photo_id, photo_uniq_id, photo_url, owner_id)
    query = "INSERT OR REPLACE INTO Photos (photo_id, photo_uniq_id, photo_url, owner_id) VALUES (?,?,?,?);"
    cur.execute(query, data)
    conn.commit()
    conn.close()


def fetch_targets(spyer_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (spyer_id, )
    query = "SELECT * FROM Targets WHERE spyer_id = ?;"
    cur.execute(query, data)
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


def fetch_target_data(target_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (target_id, )
    query = "SELECT * FROM Targets WHERE target_id = ?;"
    cur.execute(query, data)
    rows = cur.fetchall()
    data = {}
    conn.close()

    for row in rows:
        data["target_id"] = row[0]
        data["username"] = row[1]
        data["first_name"] = row[2]
        data["last_name"] = row[3]

    return data


def delete_target(spyer_id, target_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (spyer_id, target_id)
    query = "DELETE FROM Targets WHERE spyer_id = ? AND target_id = ?;"
    cur.execute(query, data)
    conn.commit()
    conn.close()
    delete_target_photos(target_id)

def delete_target_photos(target_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (target_id,)
    query = "DELETE FROM Photos WHERE owner_id = ?;" 
    cur.execute(query, data)
    conn.commit()
    conn.close()

def fetch_photos(owner_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (owner_id, )
    query = "SELECT *  FROM Photos WHERE owner_id = ?;"
    cur.execute(query, data)
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
