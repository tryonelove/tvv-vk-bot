import os

CREATOR_ID = 236965366

GROUP_ID_TEST = os.getenv("GROUP_ID_TEST")
GROUP_ID = os.getenv("GROUP_ID")
API_KEY_TEST = os.getenv("API_KEY_TEST")
API_KEY = os.getenv("API_KEY")

OSU_API_KEY = os.getenv("OSU_API_KEY")
OSU_MATCHMAKING_KEY = os.getenv("OSU_MATCHMAKING_KEY") 

RESTRICTED_HIGHLIGHTS = ["@all", "@online", "@тут", "@все"]

DATABASE_INIT = """
    CREATE TABLE IF NOT EXISTS "users" (
        "id"	INTEGER,
        "name"	TEXT,
        "server"	TEXT,
        "username"	TEXT,
        "role"	INTEGER DEFAULT 1,
        PRIMARY KEY("id")
    );

    CREATE TABLE IF NOT EXISTS "users_experience" (
        "chat_id" INTEGER,
        "user_id" INTEGER,
        "experience" FLOAT DEFAULT 0,
        "level" INTEGER DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES "users"("id")
    );

    CREATE TABLE IF NOT EXISTS "osu" (
        "id" INTEGER NOT NULL UNIQUE,
        "main_server" TEXT,
        "bancho_username" TEXT,
        "gatari_username" TEXT,
        FOREIGN KEY("id") REFERENCES "users"("id") ON UPDATE CASCADE ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS "weather" (
        "id"	INTEGER NOT NULL UNIQUE,
        "city"	TEXT,
        FOREIGN KEY("id") REFERENCES "users"("id") ON UPDATE CASCADE
    );
    CREATE TABLE IF NOT EXISTS "donators" (
        "id"	int,
        "expires"	INTEGER,
        "role"	text,
        FOREIGN KEY("id") REFERENCES "users"("id") ON UPDATE CASCADE ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS "commands" (
        "key"	INTEGER NOT NULL UNIQUE,
        "message"	TEXT,
        "attachment"	TEXT,
        "author"	INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS "beatmapsets" (
        "beatmapset_id"	INTEGER NOT NULL UNIQUE,
        "artist"	TEXT,
        "title"	TEXT,
        "background_url"	TEXT,
        PRIMARY KEY("beatmapset_id")
    );
    CREATE TABLE IF NOT EXISTS "beatmaps" (
        "beatmapset_id"	INTEGER,
        "beatmap_id"	INTEGER,
        "version"	TEXT,
        "max_combo"	INTEGER,
        PRIMARY KEY("beatmap_id"),
        FOREIGN KEY("beatmapset_id") REFERENCES "beatmapsets"("beatmapset_id")
    );
"""