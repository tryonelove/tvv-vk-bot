class MessageObject:
    def __init__(self, message=None, attachment=None, peer_id=None):
        self.message = message
        self.attachment = attachment
        self.peer_id = peer_id