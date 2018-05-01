from skype_utils.Skype_calls_manager import update_skype_calls_for_a_doctor
from skype_utils.Skype_calls_manager import set_last_time_of_update
from skype_utils.db_utils import *


def skype_billing():
    doctors_count = 0
    credentials = get_all_doctors_credentials()
    for credential in credentials:
        try:
            account = authorize(credential)
            seconds = update_skype_calls_for_a_doctor(account)
            update_doctors_call_time(credential['id'], seconds)
            doctors_count += 1
        except Exception:
            print("a problem occurred during processing doctorID: %s" % credential['id'])
            print(Exception)

    print("Successfully updated %s doctors" % doctors_count)
    set_last_time_of_update()
    print("finish procedure")