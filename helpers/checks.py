from objects import glob

def isAdmin(user_id):
    return user_id == 236965366

def isDonator(user_id):
    return str(user_id) in glob.config["donators"]

def isMainChat(chat_id):
    """
    :param chat_id: айди беседы
    """
    return chat_id == 2000000001

def hasPrivileges(user_id):
    return isAdmin(user_id) or isDonator(user_id)
    