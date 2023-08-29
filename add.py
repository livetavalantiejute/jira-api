import shutil
import os
import pandas as pd

from helpers import bold, get_available_types, check_exists

from Project import Projects
from Issue import Issue


def add(request, user_id):
    """
    Add a new task to a Jira project.
    Gets API request object and user id from main()
    """

    #Get all projects - passed into add_input
    projects = Projects()
    projects.get_projects(request)

    while True:
        add_mode = (
            input(
                bold("How would you like to add a task? Choose either Input or File: ")
            )
            .strip()
            .lower()
        )

        if add_mode == "input":
            add_input(request, user_id, projects)
        elif add_mode == "file":
            add_file(request, user_id)
        else:
            print("Try again")
            continue
        break


def add_input(request, user_id, projects):
    """
    Add a new task by inputting each field in terminal.
    Accepts request object, user id string and projects object
    """
    #Get project id - asks for input and validates
    project_id = projects.get_project_id()

    #Get all priorities and issue types for this project
    all_priorities = Issue.get_priorities(request=request, project_id=project_id)
    all_types = Issue.get_issue_types(request=request, project_id=project_id)

    #Get priority and issue type - asks for input and validates
    priority = get_available_types("Available priorities:", all_priorities, "Priority")
    issue_type = get_available_types("Available issue types:", all_types, "Issue")

    #Ask for parent key if the issue is subtask
    if issue_type == "sub-task":
        parent = input(bold("Parent task key: ")).strip().upper()

    #Summary is mandatory. It asks for input until something is written
    while True:
        summary = input(bold("Summary: ")).strip()
        if not summary:
            print("Provide a summary")
            continue
        else:
            break

    #Optional fields
    description = input(bold("Description: ")).strip()
    assignee = input(bold("Assignee email: ")).strip().lower()

    #Constructs issue object and adds it through API
    issue = Issue(
        summary=summary,
        description=description,
        assignee=assignee,
        priority=priority,
        reporter=user_id,
        issue_type=issue_type,
        parent=parent,
    )
    issue.add_issue(request=request, project_id=project_id)


def add_file(request, user_id):
    """
    Adding issues through file.
    It accepts request object and user id.
    Ignores rows with errors and sends a POST request with correct rows
    """

    #Copies the template to tasks.xlsx, in which changes are made
    filename = "tasks.xlsx"
    shutil.copyfile("task_template.xlsx", filename)
    print(bold(f"Change {filename} file with information, save and close it."))
    while True:
        is_done = input(("Input 'done' when done. ")).strip().lower()
        if is_done == "done":
            break

    #Reads excel file and ignores empty cells (otherwise it would be nan)
    df = pd.read_excel(filename, keep_default_na=False).dropna()

    #Get all projects to compare it to input project id
    projects = Projects()
    projects.get_projects(request)

    #Iterate through excel rows
    for index, row in df.iterrows():
        #If a field is incorrect, the whole row is skipped

        project_id = str(row["project_id"])

        if project_id not in (project.id for project in projects.projects):
            print("Wrong project ID")
            continue

        priority = str(row["priority"])

        all_priorities = Issue.get_priorities(request=request, project_id=project_id)
        if not check_exists(priority, all_priorities):
            print("Wrong priority")
            continue

        issue_type = str(row["issue_type"])

        all_types = Issue.get_issue_types(request=request, project_id=project_id)
        if not check_exists(issue_type, all_types):
            print("Wrong issue type")
            continue

        summary=str(row["summary"])
        description=str(row["description"])
        assignee=str(row["assignee"])
        parent=str(row["parent"])
        
        if issue_type == "sub-task" and not parent:
            print("No parent specified for sub-task")
            continue
        
        #Construct issue object and send a POST request to API
        issue = Issue(
            summary=summary,
            description=description,
            assignee=assignee,
            priority=priority,
            reporter=user_id,
            issue_type=issue_type,
            parent=parent,
        )
        issue.add_issue(request=request, project_id=project_id)

    #remove the tasks.xlsx file
    if os.path.isfile(filename):
        os.remove(filename)
