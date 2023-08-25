import sys

from helpers import bold

from Request import Request

from create import create
from view import view
from add import add


def main():
    # modes:
    # create project (kanban or scrum)
    # see tasks
    # add task
    # edit task

    modes = {
        "create": {
            "description": "Create a new project. Either Kanban or Scrum",
            "call_fn": create,
        },
        "view": {"description": "View project board", "call_fn": view,},
        "add": {"description": "Add a task to a board", "call_fn": add},
        "edit": {"description": "Edit specific task"},
    }

    # username = input(bold("What's your JIRA email? ")).strip().lower()
    # apikey = input(bold("What's your JIRA API key? ")).strip()
    # url = input(bold("Input Atlassian URL (e.g. 'https://jira-project-tests.atlassian.net'): ")).strip()

    try:
        url = sys.argv[1]
    except IndexError:
        sys.exit("JIRA URL is required")

    try:
        username = sys.argv[2]
    except IndexError:
        sys.exit("Email is required")
    
    try:
        apikey = sys.argv[3]
    except IndexError:
        sys.exit("API key is required")

    request = Request(username=username, apikey=apikey, url=url)
    request.clean_url()

    while True:
        print()
        for key in modes:
            print(f"{bold(key)}: {modes[key]['description']}")

        selected_mode = input(bold("Select mode: ")).strip().lower()

        if selected_mode != "done":
            modes[selected_mode]["call_fn"](request)
        else:
            break


if __name__ == "__main__":
    main()
