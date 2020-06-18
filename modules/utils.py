import requests
from objects import glob


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

def is_donator(user_id):
    return glob.c.execute("SELECT id FROM donators WHERE id = ?", (user_id,)).fetchone() is not None

def is_admin(user_id):
    return glob.c.execute("SELECT id FROM users WHERE admin = 1 AND id = ?", (user_id,)).fetchone() is not None

    