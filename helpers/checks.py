from objects import glob

def isOwner(user_id):
    return user_id == 236965366

def isAdmin(user_id):
    return user_id in glob.config["admin"]

def isDonator(user_id):
    user = glob.c.execute("SELECT * FROM donators WHERE id = ?", (user_id,)).fetchone()
    if user is not None and len(user)>0:
        return True
    return False

def isMainChat(chat_id):
    """
    :param chat_id: айди беседы
    """
    return chat_id == 2000000001

def isChatInDB(chat_id):
    """
    :param chat_id: айди беседы
    """
    # return cursor.execute("SELECT * FROM sqlite_master WHERE table_name = ? ", (chat_id, )).fetchone()[0]==1

def hasPrivileges(user_id):
    return isAdmin(user_id) or isDonator(user_id) or isOwner(user_id)

def commandAdder(user_id, key):
    return isAdmin(user_id) or user_id == glob.commands[key].get("author")

def restrictedCommand(key):
    return key in ["osu","осу","taiko","тайко","addcom","delcom",""]
    