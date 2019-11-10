import modules
import logging

class Invoker:
    def __init__(self, vk, event):
        self.vk = vk
        self.event = event.obj
        self.cmd = None
        if self.is_command():
            logging.info("It's a command, going next")
            self.set_command()
            logging.info("Command has been set, it's {}, going next".format(self._key))
            self.get_command()
            logging.info("Got a command, it's {}".format(self.cmd))

    def is_command(self):
        if self.event.text.startswith("!"):
            return True
        return False

    def get_command(self):
        if self._key in ["roll", "ролл"]:
            self.cmd = modules.fun.Roll(self._value)
        elif self._key in ["weather", "погода"]:
            self.cmd = modules.fun.Weather(self._value)
        elif self._key in ["osu", "осу"]:
            raise NotImplementedError()
            # self.cmd = modules.osu.OsuStatsPicture

    def set_command(self):
        message = self.event.text.split()
        self._key = message[0][1:].lower()
        self._value = " ".join(message[1:])

    def send_message(self, peer_id = None, **kwargs):
        if peer_id is None:
            self.vk.messages.send(peer_id=self.event.peer_id, **kwargs)
        else:
            self.vk.messages.send(peer_id=peer_id, **kwargs)

    def invoke(self):
        if self.cmd is None:
            return
        logging.info("Sending a message")
        executed = self.cmd.execute()
        logging.info(executed)
        self.send_message(executed)