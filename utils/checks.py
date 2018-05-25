from accounts.models import Relationships


def has_relationships(doctor_pk: int, patient_pk: int) -> bool:
    return Relationships.objects.filter(doctor__id=doctor_pk, patient__id=patient_pk).exists()
