from skype_utils.Skype_calls_manager import update_skype_calls_for_a_doctor
from skype_utils.Skype_calls_manager import set_last_time_of_update
from skype_utils.db_utils import *
import sys


def skype_billing():
    doctors_count = 0
    credentials = get_all_doctors_credentials()
    for credential in credentials:
        try:
            account = authorize(credential)
            update_skype_calls_for_a_doctor(account, credential['id'])
            doctors_count += 1
        except Exception:
            print("a problem occurred during processing doctorID: %s" % credential['id'])
            print(sys.exc_info())

    print("Successfully updated %s doctors" % doctors_count)
    set_last_time_of_update()
    print("finish procedure")