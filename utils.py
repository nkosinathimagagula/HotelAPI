from random import choices
from string import ascii_letters, digits, hexdigits


def query_filter(query_dictionary):
    filtered_dictionary = {}
    for key in query_dictionary:
        if query_dictionary[key] is not None:
            filtered_dictionary.update({key: query_dictionary[key]})
    return filtered_dictionary


def createReferenceNumber(room_number):
    chars = room_number[0:2] + room_number[-1]
    rand = chars.join(choices(ascii_letters, k=2)) + ''.join(choices(hexdigits + digits, k=8))
    return rand.upper()
