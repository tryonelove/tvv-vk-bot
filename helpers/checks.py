from objects import glob

def isOwner(user_id):
    return user_id == 236965366

def isAdmin(user_id):
    return user_id in glob.config["admin"]

def isDonator(cursor, user_id):
    return len(cursor.execute("SELECT * FROM donators WHERE id = ?", (user_id,)).fetchone())>0

def isMainChat(chat_id):
    """
    :param chat_id: айди беседы
    """
    return chat_id == 2000000001

def isChatInDB(cursor, chat_id):
    """
    :param chat_id: айди беседы
    """
    # return cursor.execute("SELECT * FROM sqlite_master WHERE table_name = ? ", (chat_id, )).fetchone()[0]==1

def hasPrivileges(cursor, user_id):
    return isAdmin(user_id) or isDonator(cursor, user_id) or isOwner(user_id)

def commandAdder(user_id, key):
    return isAdmin(user_id) or user_id == glob.commands[key].get("author")

def restrictedCommand(key):
    return key in ["osu","осу","taiko","тайко","addcom","delcom",""]
    