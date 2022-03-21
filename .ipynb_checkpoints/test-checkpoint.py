from db import *
import sqlite3
commit_user(2, "userna", "bill")
commit_target(11, "username", "girl", "Bitch", "long", "", "on", "0988", 1)



conn = sqlite3.connect("snitch.db")
cur = conn.cursor()
data = (1,)
query = "SELECT * FROM Targets WHERE spyer_id = ?;"
cur.execute(query, data)
rows  = cur.fetchall()
print(rows)
conn.close()