import re


def parse_skype_message(message):
    rows = message.__str__().split("\n")
    result = dict()
    result["info_type"] = rows.pop(0)
    for row in rows:
        temp_array = row.split(": ")
        if temp_array.__len__() > 1:
            result[temp_array[0]] = temp_array[1]
        else:
            result[temp_array[0]] = "null"

    return result


def parse_skype_contacts(contacts):
    result = []
    for contact in contacts:
        serialized_contact = parse_skype_message(contact)
        result.append(serialized_contact)

    return result


def content_parser(content, tag):
    pattern = r'<%s>(.*?)</%s>' % (tag, tag)
    res = re.findall(pattern, content, re.DOTALL)
    if res.__len__() >= 1:
        return res[0].__str__()
    return '0'
