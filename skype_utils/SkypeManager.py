from skpy import Skype


class SkypeManager:

    __skypeInstance__ = Skype

    @property
    def contacts(self):
        return self.skypeInstance.contacts

    @property
    def chats(self):
        return self.skypeInstance.chats

    def __init__(self, userId, password):
        try:
            self.skypeInstance = Skype(userId, password)
            print('Successfully access to "%s" Skype account' % userId)
        except Exception:
            print('Can not access to "%s" Skype account. Have incorrect password or account Id' % userId)

    def get_user(self):
        return self.skypeInstance.user

    def get_chat(self, username, type_of_chat='8'):
        return self.chats['%s:%s' % (type_of_chat, username)]

    def get_contact(self, contactID):
        return self.contacts[contactID]




