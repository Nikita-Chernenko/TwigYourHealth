from skpy import Skype
from skype_utils.skype_format_parser import parse_skype_contacts


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

    def get_chat(self, username, type_of_chat='8'):
        return self.chats['%s:%s' % (type_of_chat, username)]

    def get_contact(self, contactID):
        return self.contacts[contactID]

    def get_messages(self, userId):
        chat = self.get_chat(userId)
        result = []
        while True:
            temp_response = chat.getMsgs()
            if temp_response.__len__() == 0:
                break
            result.extend(temp_response)
        return result

    def retrieve_contacts(self):
        result = []
        contacts = parse_skype_contacts(self.contacts)

        for contact in contacts:
            result.append(contact["Id"])

        return result