from accounts.models import Doctor, Patient
from skype_utils.SkypeManager import SkypeManager


def get_all_doctors_credentials():
    res = Doctor.objects\
        .exclude(skype=None)\
        .exclude(skype_password=None)\
        .values('id', 'skype', 'skype_password')

    return res


def authorize(doctors_credentials):
    print("authorizing doctor, id: %s" % doctors_credentials['id'])
    return SkypeManager(doctors_credentials['skype'], doctors_credentials['skype_password'])


def get_patients_skype_accounts():
    return Patient.objects\
        .exclude(skype=None)\
        .values_list('skype', flat=True)


def update_doctors_call_time(doctor_id, seconds):
    doc = Doctor.objects.get(id=int(doctor_id))
    doc.seconds = int(seconds)
    doc.save()