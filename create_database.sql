BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Photos" (
	"photo_id"	TEXT NOT NULL PRIMARY KEY,
	"photo_uniq_id"	TEXT NOT NULL,
	"photo_url"	TEXT,
	"owner_id"	INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "Targets" (
	"target_id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"username"	TEXT NOT NULL,
	"first_name"	TEXT NOT NULL,
	"last_name"	TEXT,
	"last_seen"	TEXT,
	"bio"	TEXT,
	"status"	TEXT,
	"phone_number"	TEXT,
	"spyer_id"	INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "Users" (
	"user_id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"username"	TEXT NOT NULL,
	"first_name"	TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "Chat" (
  "chat_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"user_id"	INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS "owner_index" ON "Photos" (
	"owner_id"	ASC
);

CREATE INDEX IF NOT EXISTS "Spyer_idx" ON "Targets" (
	"spyer_id"	ASC
);

COMMIT;
