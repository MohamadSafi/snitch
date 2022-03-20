import sqlite3
import os

DB_PATH = "snitch.py"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    with open("create_database.sql","r") as fd:
        cur.execute(fd.read())
    conn.close()

def commit_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (user_id, username, first_name)
    query = "INSERT INTO Users (user_id, username, first_name) VALUES (?,?,?);"
    cur.execute(query, data)
    conn.close()

def commit_target(target_id, username, first_name, last_name, last_seen, bio, status,phone_number,spyer_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (target_id, username, first_name, last_name, last_seen, bio, status,phone_number,spyer_id)
    query = "INSERT INTO Targets (target_id, username, first_name, last_name, last_seen, bio, status,phone_number,spyer_id) VALUSE (?,?,?,?,?,?,?,?,?);"
    cur.execute(query, data)
    conn.close()

def commit_photo(photo_id, photo_uniq_id, photo_url, owner_id ):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.sursor()
    data = (photo_id, photo_uniq_id, photo_url, owner_id)
    query = "INSERT INTO Photos (photo_id, photo_uniq_id, photo_url, owner_id) VALUES (?,?,?,?);"
    cur.execute(query,data)
    conn.close()
