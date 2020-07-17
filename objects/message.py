from constants.messageTypes import MessageTypes

class MessageObject:
    def __init__(self, message=None, attachment=None, message_type=MessageTypes.CHAT):
        """
        Message object

        :param message: message text
        :param attachment: message attachment
        :param message_type: type of message (private or public)
        """
        self.message = message
        self.attachment = attachment
        self.message_type = message_type