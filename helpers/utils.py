import requests
from objects import glob
from constants.roles import Roles


def upload_picture(url, decode_content = False):
    """
    Upload image to the server
    :param url: image URL
    """
    session = requests.Session()
    image = session.get(url, stream=True).raw
    image.decode_content = decode_content
    photo = glob.upload.photo_messages(photos=image)[0]
    return "photo{}_{}".format(photo['owner_id'], photo['id'])

def find_largest_attachment(attachments):
    """
    Find the largest attached image
    :param attachments: attachments list
    """
    largest = 0
    for image in attachments:
        larger = image["width"]*image["height"]
        if larger>largest:
            largest = larger
            largest_pic = image["url"]
    return largest_pic

def get_role(user_id):
    return glob.c.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()[0]

def has_role(user_id, required_role):
    role = get_role(user_id)
    return role & required_role.value > 0

def is_creator(user_id):
    return user_id == 236965366