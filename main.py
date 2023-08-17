from create import create
from helpers import bold
from Request import Request

from view import view


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
        "add": {"description": "Add a task to a board"},
        "edit": {"description": "Edit specific task"},
    }

    username = input(bold("What's your JIRA email? ")).strip().lower()
    apikey = input(bold("What's your JIRA API key? ")).strip()
    url = input(bold("Input Atlassian URL (e.g. 'https://jira-project-tests.atlassian.net'): ")).strip()

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
