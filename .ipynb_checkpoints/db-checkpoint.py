import sqlite3
import os

DB_PATH = "snitch.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    with open("create_database.sql","r") as fd:
        cur.executescript(fd.read())
    cur.commit()
    conn.close()

def commit_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (user_id, username, first_name)
    query = "INSERT INTO Users (user_id, username, first_name) VALUES (?,?,?);"
    cur.execute(query, data)
    cur.commit()
    conn.close()

def commit_target(target_id, username, first_name, last_name, last_seen, bio, status,phone_number,spyer_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (target_id, username, first_name, last_name, last_seen, bio, status,phone_number,spyer_id)
    query = "INSERT INTO Targets (target_id, username, first_name, last_name, last_seen, bio, status,phone_number,spyer_id) VALUES (?,?,?,?,?,?,?,?,?);"
    cur.execute(query, data)
    cur.commit()
    conn.close()

def commit_photo(photo_id, photo_uniq_id, photo_url, owner_id ):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.sursor()
    data = (photo_id, photo_uniq_id, photo_url, owner_id)
    query = "INSERT INTO Photos (photo_id, photo_uniq_id, photo_url, owner_id) VALUES (?,?,?,?);"
    cur.execute(query,data)
    cur.commit()
    conn.close()

def fetch_targets(spyer_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (spyer_id,)
    query = "SELECT * FROM Targets WHERE spyer_id = ?;"
    cur.execute(query, data)
    conn.close()

def fetch_photos(owner_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (owner_id,)
    query = "SELECT photo_id FROM Photos WHERE owner_id = ?;"
    cur.execute(query, data)
    conn.close()















