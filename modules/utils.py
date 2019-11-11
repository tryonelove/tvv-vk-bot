import requests

def uploadPicture(upload, url, decode_content = False):
    session = requests.Session()
    image = session.get(url, stream=True).raw
    image.decode_content = decode_content
    photo = upload.photo_messages(photos=image)[0]
    return "photo{}_{}".format(photo['owner_id'], photo['id'])

    