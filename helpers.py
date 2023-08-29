from termcolor import colored


def bold(s):
    """returns bold text"""
    return colored(s, attrs=['bold'])


def red(s):
    """returns red text"""
    return colored(s, "red")


def get_available_types(text, types, type_str):
    """
    Get all available types, e.g. priorities, issue_types, statuses
    Checks input and validates if it exists for specific type
    """
    while True:
        print(bold(text))
        for t in types:
            print(t["name"])
        input_type = input(bold(f"{type_str}: ")).strip().lower()
        t = check_exists(input_type, types)
        if t:
            return t
        else:
            print(f"Wrong {type_str.lower()} type\n")
            continue


def check_exists(input_type, types):
    """Check if a type exists in a list of types dictionaries"""
    if any(t["name"].lower() == input_type for t in types):
        return input_type