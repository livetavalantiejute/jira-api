import sys
from dotenv import load_dotenv
import os

from helpers import bold

from Request import Request

from create import create
from view import view
from add import add
from edit import edit
from download import download


def main():
    """Main function to call.
    Calls other functions depending on mode and checks for validity of data for API"""

    modes = {
        "create": {
            "description": "Create a new project. Either Kanban or Scrum",
            "call_fn": create,
        },
        "view": {
            "description": "View project board",
            "call_fn": view,
        },
        "add": {"description": "Add a task to a board", "call_fn": add},
        "edit": {"description": "Edit specific task", "call_fn": edit},
        "download": {"description": "Download project data", "call_fn": download},
        "done": {"description": "Exit the program"},
    }

    load_dotenv()

    # try getting command line arguments
    try:
        url = sys.argv[1]
        url = url.strip()
    except IndexError:
        sys.exit("JIRA URL is required")

    try:
        username = sys.argv[2]
        username = username.strip()
    except IndexError:
        sys.exit("Email is required")

    # try getting api key from .env
    apikey = os.environ.get("APIKEY")

    if not apikey:
        sys.exit("Input you API key into environment")

    # constructing a request object - used to pass to other functions, where API call is needed.
    request = Request(username=username, apikey=apikey, url=url)
    request.clean_url()

    user_id = request.get_user_id()

    # Print all the modes and call functions indefinitely - until "done"
    # This allows fewer API calls and opening the program again
    while True:
        print()
        for key in modes:
            print(f"{bold(key)}: {modes[key]['description']}")

        selected_mode = input(bold("Select mode: ")).strip().lower()

        if selected_mode != "done":
            try:
                modes[selected_mode]["call_fn"](request, user_id)
            except KeyError:
                print("Such mode does not exist")
                continue
        else:
            break


if __name__ == "__main__":
    main()
