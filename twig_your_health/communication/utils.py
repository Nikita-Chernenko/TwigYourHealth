def _user_belong_to_chat(user, chat):
    return not (user.is_patient and chat.patient != user.patient or user.is_doctor and chat.doctor != user.doctor)
