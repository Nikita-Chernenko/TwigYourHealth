from skpy import SkypeCallMsg


class Call:

    def __init__(self, message):
        self.Id = message.id
        self.Patient = message.userId
        self.Ended = message.time
        self.Content = message.content