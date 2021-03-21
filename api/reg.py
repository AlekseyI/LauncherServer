import re
import json


class DecodeException(Exception):
    pass

def get_name_program(path):
    pat = r'\w+[.]\w+'
    comp = re.compile(pat)
    res = comp.search(path)
    return res.group(0)


def parse_to_list(data):
    try:
        decode = json.loads('[' + data + ']')
    except json.JSONDecodeError:
        raise DecodeException()
    return decode
