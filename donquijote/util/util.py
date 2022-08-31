import re


def int_cast(input):
    try:
        return int(input)
    except ValueError:
        return None


def time_cast(input):
    time_regex = re.compile(r"^\d\d:\d\d$")

    if time_regex.match(input):
        if 24 >= int(input[:2]) >= 0 and 59 >= int(input[-2:]) >= 0:
            return input

    return None
