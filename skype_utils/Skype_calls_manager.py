import os
from skpy import SkypeCallMsg
from time import gmtime, strftime
from skype_utils.call import Call
from communication.models import CallEntity
from accounts.models import PrivateDoctor, Patient
from skype_utils.skype_format_parser import content_parser
from datetime import datetime, timedelta
from skype_utils.db_utils import get_patients_skype_accounts
import json

CONFIG = os.path.join('skype_utils', 'config.json')
LAST_TIME_ATTR = 'LastRunOfProcedure'
INTERVAL_ATTR = 'Interval'
LOCALTIME = 'Local_time'


def string_to_datetime(string):
    try:
        return datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
    except Exception:
        return 0


def set_time_as_local(time):
    return time + timedelta(hours=int(get_data_from_conf(LOCALTIME)))


def get_last_time_of_update():
    with open(CONFIG, 'r') as f:
        config = json.load(f)
    return config[LAST_TIME_ATTR]


def get_data_from_conf(attr):
    with open(CONFIG, 'r') as f:
        config = json.load(f)
    return config[attr]


def set_last_time_of_update(time=strftime("%Y-%m-%d %H:%M:%S", gmtime())):
    config = None
    with open(CONFIG, 'r', encoding='utf-8') as f:
        config = json.load(f)
        config[LAST_TIME_ATTR] = time.__str__()

    with open(CONFIG, 'w') as f:
        json.dump(config, f)


def get_all_calls_until_last_time(messages):
    res = []
    for message in messages:
        if message.type.__str__() == "Event/Call" \
                and message.state is SkypeCallMsg.State.Ended:
            call = Call(message)
            res.append(call)

    return res


def is_a_patient(userID):
    if userID in get_patients_skype_accounts():
        return True
    return False


def sort_calls_by_time(calls):
    res = []
    time = get_last_time_of_update()
    for call in calls:
        if set_time_as_local(call.Ended) > set_time_as_local(string_to_datetime(time)):
            res.append(call)
    return res


def insert_call_into_db(_call, doctors_id, patients_skype):
    call = CallEntity()
    call.doctor = PrivateDoctor.objects.get(id=doctors_id)
    call.patient = Patient.objects.get(skype=patients_skype)
    call.end = _call.Ended
    call.duration = int(content_parser(_call.Content, 'duration'))
    call.start = call.end - timedelta(seconds=call.duration)
    call.save(force_insert=True)


def update_skype_calls_for_a_doctor(account, doctor_id):
    contacts = account.retrieve_contacts()
    total_time = 0
    for contact in contacts:
        if is_a_patient(contact):
            while True:
                try:
                    chat = account.get_messages(contact)
                    break
                except Exception:
                    pass
            calls = get_all_calls_until_last_time(chat)
            calls = sort_calls_by_time(calls)
            for call in calls:
<<<<<<< HEAD
                insert_call_into_db(call, doctor_id, contact)
=======
                secondsS = content_parser(call.Content, 'duration')
                total_time += int(secondsS)

    return total_time
>>>>>>> 276e9c736f85da28a3e6c16347aa1c5e0ee1ac4a
