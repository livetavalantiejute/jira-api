from termcolor import colored


def bold(s):
    return colored(s, attrs=['bold'])


def red(s):
    return colored(s, "red")


def get_available_types(text, types, type_str):
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
    if any(t["name"].lower() == input_type for t in types):
        return input_type